from flask import Flask, render_template, request, redirect, url_for, flash, session
import csv, os, re
from app.main import main_bp
from datetime import datetime

CSV_LOC = 'data/publish_data.csv'
COMMENTS_CSV = 'data/comments_data.csv'
USERS_CSV = 'data/usuarios.csv'
EMOJIS_CSV = 'data/emojis.csv'
REACTION_CSV = 'data/reactions_data.csv'

COLLUMN_HEADER = ['username','title','description','topico_principal','tipo_de_post','linguagem_selecionada','image','visibility']
COMMENTS_HEADER = ['post_title','username','comment_text','timestamp']
EMOJIS_HEADER = ['id', 'emoji']

# Filtragem melhoradinha usando a searchbar, depois eu vou desacoplar essa função da função de filtragem básica(por filtros)
@main_bp.route('/advanced_filtering')
def advance_filtering(publish_vector: str, publish_posts:list):
    if not session.get('usuario'):
        return redirect(url_for('main.login'))

    def normalize(txt):
        return re.sub(r"[^\w\s]", "", txt).lower().split()

    query = normalize(publish_vector)
    scores = {}

    for i, post in enumerate(publish_posts):

        campos = [
            post["title"],
            post["description"],
            post["topico_principal"],
            post["tipo_de_post"],
            post["linguagem_selecionada"]
        ]

        score = 0
        publish_txt = " ".join(c for c in campos if c)
        publish_txt = normalize(publish_txt)

        for keyword in query:
            score += publish_txt.count(keyword)

        if score > 0:
            scores[i] = score

    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    res = []

    for i, v in ordered:
        res.append(publish_posts[i])

    return res


# @gabrielcarvalho, isso aqui lê csv caso você vá fazer o feed
def ler_publicacoes(f_topico_principal,f_tipo_de_post,f_linguagem_selecionada, f_searchbar):
    publicacoes = []
    try:
        with open(CSV_LOC, 'r', newline='', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:

                if f_topico_principal and linha["topico_principal"] != f_topico_principal and f_topico_principal != "Todos":
                    continue
                
                if f_tipo_de_post and linha["tipo_de_post"] != f_tipo_de_post and f_tipo_de_post != "Todos":
                    continue

                if f_linguagem_selecionada and linha["linguagem_selecionada"] != f_linguagem_selecionada and f_linguagem_selecionada != "Todos":
                    continue
                
                publicacoes.append(linha)
    except FileNotFoundError:
        return []
    
    return advance_filtering(f_searchbar, publicacoes) if f_searchbar != "" else publicacoes


def save_publish_data(dados_da_nova_pub):
    with open(CSV_LOC, 'a', newline='', encoding='utf-8') as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLLUMN_HEADER)
        escritor.writerow(dados_da_nova_pub)

def ler_comentarios(titulo_post):
    comentarios = []
    with open(COMMENTS_CSV, 'r', newline='', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            if linha['post_title'] == titulo_post:
                comentarios.append(linha)
    return comentarios

def salvar_comentario(dados_comentario):
    arquivo_existe = os.path.exists(COMMENTS_CSV)
    with open(COMMENTS_CSV, 'a', newline='', encoding='utf-8') as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COMMENTS_HEADER)
        if not arquivo_existe:
            escritor.writeheader()
        escritor.writerow(dados_comentario)

@main_bp.route('/')
def landing():
    session.pop('username', None)
    return render_template('main/landing.html')      
# vai ser nossa primeira página. Landing page :D

# Homepage do app com os posts dos usuários
@main_bp.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get('usuario'):
        return redirect(url_for('main.login'))
    
    f_topico_principal = None
    f_tipo_de_post = None
    f_linguagem_selecionada = None
    f_searchbar = ""

    if request.method == 'POST':
        f_topico_principal = request.form.get("filtro_topico_principal")
        f_tipo_de_post = request.form.get("filtro_tipo_de_post")
        f_linguagem_selecionada = request.form.get("filtro_linguagem_selecionada")
        f_searchbar = request.form.get("search")

    publicacoes = ler_publicacoes(f_topico_principal,f_tipo_de_post,f_linguagem_selecionada, f_searchbar)
    
    posts_com_comentarios = []
    for post in publicacoes:
        post_data = post.copy()
        todos_comentarios = ler_comentarios(post['title'])
        post_data['comentarios'] = todos_comentarios[:3]
        post_data['total_comentarios'] = len(todos_comentarios)
        post_data['tem_mais'] = len(todos_comentarios) > 3
        posts_com_comentarios.append(post_data)

    todos_emojis = {}
    with open(EMOJIS_CSV, 'r', encoding='utf-8') as emojis_data:
        conteudo = emojis_data.read().splitlines()[1:]

        for linha in conteudo:
            id, figura, legenda = linha.split(';')
            emoji = {'id': id,
                     'figura': figura,
                     'legenda': legenda}
            todos_emojis[id] = emoji

    reacoes = []
    with open(REACTION_CSV, 'r', encoding='utf-8') as reacoes_data:
        conteudo = reacoes_data.read().splitlines()[1:]
        for linha in conteudo:
            titulo_post, username, id_emoji = linha.split(';')
            reacao = {'titulo_post': titulo_post,
                     'username': username,
                     'id_emoji': id_emoji}
            reacoes.append(reacao)
    
    for reacao in reacoes:
        emoji_reacao = todos_emojis[reacao['id_emoji']]
        reacao['figura'] = emoji_reacao['figura']
        reacao['legenda'] = emoji_reacao['legenda']
    
    reacoes_post = {}
    for reacao in reacoes:
        titulo_post = reacao['titulo_post']
        id_emoji = reacao['id_emoji']
        if titulo_post in reacoes_post:
            dict_reacoes_post = reacoes_post[titulo_post]
            if id_emoji in dict_reacoes_post:
                dict_reacoes_post[id_emoji]['contador'] += 1
            else:
                dict_reacoes_post[id_emoji] = {'figura': reacao['figura'], 'legenda': reacao['legenda'], 'contador': 1}
        else:
            reacoes_post[titulo_post] = {id_emoji: {'figura': reacao['figura'], 'legenda': reacao['legenda'], 'contador': 1}}
    
    reacoes_usuario = {}
    for reacao in reacoes:
        if reacao['username'] == session['usuario']['nome_usuario']:
            titulo_post = reacao['titulo_post']
            if titulo_post in reacoes_usuario:
                reacoes_usuario[titulo_post].append(reacao['id_emoji'])
            else:
                reacoes_usuario[titulo_post] = [reacao['id_emoji']]
    
    return render_template('main/home.html', posts=posts_com_comentarios, f_topico_principal=f_topico_principal, f_tipo_de_post=f_tipo_de_post, f_linguagem_selecionada=f_linguagem_selecionada, todos_emojis=todos_emojis, reacoes_post=reacoes_post, reacoes_usuario=reacoes_usuario)

@main_bp.route('/adicionar_reacoes', methods=['POST'])
def adicionar_reacoes():
    if not session.get('usuario'):
        return redirect(url_for('main.login'))
    
    ids_emojis_selecionados = request.form.getlist('emojis')
    titulo_post = request.args.get('titulo_post')
    username = session['usuario']['nome_usuario']

    emojis_selecionados = []
    with open(EMOJIS_CSV, 'r', encoding='utf-8') as emojis_data:
        conteudo = emojis_data.read().splitlines()[1:]
        for linha in conteudo:
            id, figura, legenda = linha.split(';')
            if id in ids_emojis_selecionados:
                emojis_selecionados.append(id)
    
    with open(REACTION_CSV, 'a', encoding='utf-8') as reactions_data:
        for id_emoji in emojis_selecionados:
            reactions_data.write(f'{titulo_post};{username};{id_emoji}\n')

    return redirect(url_for('main.home') + f'#post-{titulo_post}')

@main_bp.route('/remover_reacoes', methods=['POST'])
def remover_reacoes():
    if not session.get('usuario'):
        return redirect(url_for('main.login'))

    ids_emojis_remover = request.form.getlist('emojis')
    titulo_post_selecionado = request.args.get('titulo_post')
    usuario = session['usuario']['nome_usuario']

    reacoes_nao_removidos = []
    with open(REACTION_CSV, 'r', encoding='utf-8') as reactions_data:
        conteudo = reactions_data.read().splitlines()[1:]
        for linha in conteudo:
            titulo_post, username, id_emoji = linha.split(';')
            if titulo_post != titulo_post_selecionado or username != usuario or id_emoji not in ids_emojis_remover:
                reacoes_nao_removidos.append((titulo_post, username, id_emoji))
    
    with open(REACTION_CSV, 'w', encoding='utf-8') as reactions_data:
        for titulo_post, username, id_emoji in reacoes_nao_removidos:
            reactions_data.write(f'{titulo_post};{username};{id_emoji}\n')

    return redirect(url_for('main.home') + f'#post-{titulo_post_selecionado}')

# Página de criação de publicações
@main_bp.route('/publish', methods=['GET'])
def publish():
    if not session.get('usuario'):
        return redirect(url_for('main.login'))
    
    return render_template('main/publish.html')

@main_bp.route('/perfil', methods=['GET'])
def perfil():
    if not session.get('usuario'):
        return redirect(url_for('main.login'))
    
    return render_template('main/perfil.html')
# vai ser a página de edição de perfil do usuário

@main_bp.route('/profile_original', methods=['GET'])
def profile_original():
    if not session.get('usuario'):
        return redirect(url_for('main.login'))
    
    return render_template('main/profile_original.html')

@main_bp.route('/editar_perfil', methods=['POST'])
def editar_perfil():
    if not session.get('usuario'):
        return redirect(url_for('main.login'))

    full_name = request.form.get('full_name')
    email = request.form.get('email')
    username = request.form.get('username')
    bio = request.form.get('bio')
    location = request.form.get('location')
    github = request.form.get('github')

    # TODO: salvar os dados do perfil no banco de dados, esperando o PR de Claudino ser mergeado para a develop

    return redirect(url_for('main.perfil'))

@main_bp.route('/send_publish_data', methods=['POST'])
def send_publish_data():
    if not session.get('usuario'):
        return redirect(url_for('main.login'))
    
    nomes_das_colunas = ['titulo', 'descricao', 'categoria', 'image','visibility']
    
    publish_data = {
        'username': session['usuario']['nome_usuario'],
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'topico_principal': request.form.get('topico_principal'),
        'tipo_de_post': request.form.get('tipo_de_post'),
        'linguagem_selecionada': request.form.get('linguagem_selecionada'),
        'image': request.form.get('image'),
        'visibility': request.form.get('visibility')
    }

    save_publish_data(publish_data)
    flash('Publicação realizada!', 'success')
    return redirect(url_for('main.home'))

@main_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """if session.get('usuario'):
        return redirect(url_for('main.home'))"""
    
    if request.method == 'POST':
        nome_completo = request.form.get('nome-completo')
        email = request.form.get('email')
        nome_usuario = request.form.get('nome-usuario')
        senha = request.form.get('senha')
        bio = None
        localizacao = None
        link_github = None
        foto = None

        session['usuario'] = {'nome_completo': nome_completo,
                              'email': email,
                              'nome_usuario': nome_usuario,
                              'bio': bio,
                              'localizacao': localizacao,
                              'link_github': link_github,
                              'foto': foto}

        #Verifica se o arquivo usuarios.csv não existe
        if not os.path.exists(USERS_CSV):
            with open(USERS_CSV, 'x', encoding="utf-8") as arquivo_usuarios:
                arquivo_usuarios.write(f'{nome_completo};{nome_usuario};{email};{senha};{bio};{localizacao};{link_github};{foto}\n')
                session['usuario']['nome_usuario'] = nome_usuario
                return redirect(url_for('main.home'))
        else:
            pode_cadastrar_usuario = True

            # Impede que a pessoa crie sua conta se já houver alguém com o mesmo nome de usuário ou email
            with open(USERS_CSV, "r", encoding="utf-8") as arquivo_usuarios:
                linhas = arquivo_usuarios.readlines()
                for linha in linhas:
                    registro = linha.strip().split(';')
                    usuario_registrado = registro[1]
                    email_registrado = registro[2]
                    if nome_usuario == usuario_registrado or email == email_registrado:
                        pode_cadastrar_usuario = False
                        break
            
            if pode_cadastrar_usuario:
                with open(USERS_CSV, "a", encoding="utf-8") as arquivo_usuarios:
                    arquivo_usuarios.write(f'{nome_completo};{nome_usuario};{email};{senha};{bio};{localizacao};{link_github};{foto}\n')
                    session['usuario']['nome_usuario'] = nome_usuario
                    return redirect(url_for('main.home'))
            else:
                flash('Nome de usuário ou email já existe.', 'error')
                return redirect(url_for('main.cadastro'))
        
    return render_template("main/cadastro.html")

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """if session.get('usuario'):
        return redirect(url_for('main.home'))"""
    
    if request.method == 'POST':
        identificador = request.form.get('identificador')
        senha_digitada = request.form.get('senha')

        pode_autenticar_usuario = False

        if not os.path.exists(USERS_CSV):
            flash('Nome de usuário/email ou senha incorretos.', 'error')
            return redirect(url_for('main.login'))
        
        with open(USERS_CSV, "r", encoding="utf-8") as arquivo_usuarios:
            conteudo = arquivo_usuarios.read().splitlines()[1:]
            for linha in conteudo:
                nome_completo, email, nome_usuario, senha, bio, localizacao, link_github, foto = linha.split(';')
                if (identificador == nome_usuario or identificador == email) and senha_digitada == senha:
                    pode_autenticar_usuario = True
                    break
            
            if pode_autenticar_usuario:
                session['usuario'] = {'nome_completo': nome_completo,
                                      'email': email,
                                      'nome_usuario': nome_usuario,
                                      'bio': bio,
                                      'localizacao': localizacao,
                                      'link_github': link_github,
                                      'foto': foto}
                return redirect(url_for('main.home'))

            else:
                flash('Nome de usuário/email ou senha incorretos.', 'error')
                return redirect(url_for('main.login'))
        
    return render_template("main/login.html")

@main_bp.route('/logout')
def logout():
    if not session.get('usuario'):
        return redirect(url_for('main.login'))

    session.pop('usuario', None)
    return redirect(url_for('main.landing'))

@main_bp.route('/delete_post', methods=['POST'])
def delete_post():
    if not session.get('usuario'):
        return redirect(url_for('main.login'))
    
    titulo_para_deletar = request.form.get('titulo_post')
    caminho_csv = CSV_LOC
    
    postagens_restantes = []

    with open(caminho_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['title'] != titulo_para_deletar:
                postagens_restantes.append(row)

    with open(caminho_csv, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(postagens_restantes)

    return redirect('home')

@main_bp.route('/add_comment', methods=['POST'])
def add_comment():
    if not session.get('usuario'):
        return redirect(url_for('main.login'))
    
    post_title = request.form.get('post_title')
    comment_txt = request.form.get('comment_text')
    redirect_to = request.form.get('redirect_to')
    
    if comment_txt and post_title:
        dados_comentario = {
            'post_title': post_title,
            'username': session['usuario']['nome_usuario'],
            'comment_text': comment_txt,
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        salvar_comentario(dados_comentario)
    
    if redirect_to:
        return redirect(redirect_to)
    return redirect(url_for('main.home'))

@main_bp.route('/delete_comment', methods=['POST'])
def delete_comment():
    if not session.get('usuario'):
        return redirect('login')
    
    post_title = request.form.get('post_title')
    username = request.form.get('username')
    timestamp = request.form.get('timestamp')
    redirect_to = request.form.get('redirect_to')
    
    if username == session['usuario']['nome_usuario']:
        comentarios_restantes = []
        
        with open(COMMENTS_CSV, 'r', newline='', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                if not (linha['post_title'] == post_title and 
                       linha['username'] == username and 
                       linha['timestamp'] == timestamp):
                    comentarios_restantes.append(linha)
        
        with open(COMMENTS_CSV, 'w', newline='', encoding='utf-8') as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=COMMENTS_HEADER)
            escritor.writeheader()
            escritor.writerows(comentarios_restantes)
    
    if redirect_to:
        return redirect(redirect_to)
    return redirect('home')

@main_bp.route('/post/<post_title>')
def ver_post(post_title):
    if not session.get('usuario'):
        return redirect(url_for('main.login'))
    
    publicacoes = ler_publicacoes(None, None, None, "")
    post = None
    for p in publicacoes:
        if p['title'] == post_title:
            post = p
            break
    
    if not post:
        return redirect(url_for('main.home'))
    
    post['comentarios'] = ler_comentarios(post_title)
    post['total_comentarios'] = len(post['comentarios'])
    
    return render_template('main/post.html', post=post)