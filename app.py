import csv, os, re
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')


CSV_LOC = 'data/publish_data.csv'
COLLUMN_HEADER = ['username','title','description','topico_principal','tipo_de_post','linguagem_selecionada','image','visibility']

# Filtragem melhoradinha usando a searchbar, depois eu vou desacoplar essa função da função de filtragem básica(por filtros)
@app.route('/advanced_filtering')
def advance_filtering(publish_vector: str, publish_posts:list):

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

@app.route('/')
def landing():
    session.pop('username', None)
    return render_template('landing.html')      
# vai ser nossa primeira página. Landing page :D

# Homepage do app com os posts dos usuários
@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get('usuario_logado'):
        return redirect(url_for('login'))
    
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
    return render_template('home.html', posts=publicacoes,f_topico_principal=f_topico_principal,f_tipo_de_post=f_tipo_de_post,f_linguagem_selecionada=f_linguagem_selecionada)

# Página de criação de publicações
@app.route('/publish', methods=['GET'])
def publish():
    if not session.get('usuario_logado'):
        return redirect(url_for('login'))
    
    return render_template('publish.html')

@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')
# vai ser a página de edição de perfil do usuário

@app.route('/profile/edit', methods=['POST'])
def profile_edit():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    username = request.form.get('username')
    bio = request.form.get('bio')
    location = request.form.get('location')
    github = request.form.get('github')

    # TODO: salvar os dados do perfil no banco de dados, esperando o PR de Claudino ser mergeado para a develop

    return redirect(url_for('profile'))

@app.route('/send_publish_data', methods=['POST'])
def send_publish_data():
    if not session.get('usuario_logado'):
        return redirect(url_for('login'))
    
    nomes_das_colunas = ['titulo', 'descricao', 'categoria', 'image','visibility']
    
    publish_data = {
        'username': session['usuario_logado'],
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
    return redirect(url_for('home'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome_completo = request.form.get('nome-completo')
        usuario = request.form.get('nome-usuario')
        email = request.form.get('email')
        senha = request.form.get('senha')

        #Verifica se o arquivo usuarios.csv não existe
        if not os.path.exists("data/usuarios.csv"):
            with open('data/usuarios.csv', 'x', encoding="utf-8") as arquivo_usuarios:
                arquivo_usuarios.write(f'{nome_completo};{usuario};{email};{senha}\n')
                session['usuario_logado'] = usuario
                return redirect(url_for('home'))
        else:
            pode_cadastrar_usuario = True

            # Impede que a pessoa crie sua conta se já houver alguém com o mesmo nome de usuário ou email
            with open("data/usuarios.csv", "r", encoding="utf-8") as arquivo_usuarios:
                linhas = arquivo_usuarios.readlines()
                for linha in linhas:
                    registro = linha.strip().split(';')
                    usuario_registrado = registro[1]
                    email_registrado = registro[2]
                    if usuario == usuario_registrado or email == email_registrado:
                        pode_cadastrar_usuario = False
                        break
            
            if pode_cadastrar_usuario:
                with open("data/usuarios.csv", "a", encoding="utf-8") as arquivo_usuarios:
                    arquivo_usuarios.write(f"{nome_completo};{usuario};{email};{senha}\n")
                    session['usuario_logado'] = usuario
                    return redirect(url_for('home'))
            else:
                flash('Nome de usuário ou email já existe.', 'error')
                return redirect(url_for('cadastro'))
        
    return render_template("cadastro.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identificador = request.form.get('identificador')
        senha = request.form.get('senha')

        pode_autenticar_usuario = False

        if not os.path.exists("data/usuarios.csv"):
            flash('Nome de usuário/email ou senha incorretos.', 'error')
            print("sem csv")
            return redirect(url_for('login'))
        
        with open("data/usuarios.csv", "r", encoding="utf-8") as arquivo_usuarios:
            linhas = arquivo_usuarios.readlines()
            for linha in linhas:
                registro = linha.strip().split(';')
                usuario_registrado = registro[1]
                email_registrado = registro[2]
                senha_registrada = registro[3]

                if (identificador == usuario_registrado or identificador == email_registrado) and senha == senha_registrada:
                    pode_autenticar_usuario = True
                    break
            
            if pode_autenticar_usuario:
                session['usuario_logado'] = usuario_registrado
                return redirect(url_for('home'))
            else:
                flash('Nome de usuário/email ou senha incorretos.', 'error')
                print(identificador, usuario_registrado)
                print(senha, senha_registrada)
                return redirect(url_for('login'))
        
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    return redirect(url_for('landing'))

@app.route('/delete_post', methods=['POST'])
def delete_post():
    titulo_para_deletar = request.form.get('titulo_post')
    caminho_csv = 'data/publish_data.csv'
    
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

    return redirect('/home')



if __name__ == "__main__":
    app.run(debug=True)

