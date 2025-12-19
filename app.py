import csv, os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')


CSV_LOC = 'data/publish_data.csv'
COLLUMN_HEADER = ['username','title','description','topico_principal','tipo_de_post','linguagem_selecionada','image','visibility']

# @gabrielcarvalho, isso aqui lê csv caso você vá fazer o feed
def ler_publicacoes(): 
    publicacoes = []
    try:
        with open(CSV_LOC, 'r', newline='', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                publicacoes.append(linha)
    except FileNotFoundError:
        return [] 
    return publicacoes

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
@app.route('/home')
def home():
    publicacoes = ler_publicacoes()
    return render_template('home.html', posts=publicacoes)

# Página de criação de publicações
@app.route('/publish', methods=['GET'])
def publish():
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
    session['username'] = 'anônimo'
    nomes_das_colunas = ['titulo', 'descricao', 'categoria', 'image','visibility']
    
    publish_data = {
        'username': request.form.get('username', 'anônimo'),  # default para anonymous pois ainda nao temos cadastro/login, claudino está encarregado disso :D
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
        if not os.path.exists("usuarios.csv"):
            with open('usuarios.csv', 'x', encoding="utf-8") as arquivo_usuarios:
                arquivo_usuarios.write(f'{nome_completo};{usuario};{email};{senha}\n')
                session['usuario_logado'] = usuario
                return redirect(url_for('home'))
        else:
            pode_cadastrar_usuario = True

            # Impede que a pessoa crie sua conta se já houver alguém com o mesmo nome de usuário ou email
            with open("usuarios.csv", "r", encoding="utf-8") as arquivo_usuarios:
                linhas = arquivo_usuarios.readlines()
                for linha in linhas:
                    registro = linha.split(';')
                    usuario_registrado = registro[1]
                    email_registrado = registro[2]
                    if usuario == usuario_registrado or email == email_registrado:
                        pode_cadastrar_usuario = False
                        break
            
            if pode_cadastrar_usuario:
                with open("usuarios.csv", "a", encoding="utf-8") as arquivo_usuarios:
                    arquivo_usuarios.write(f"{nome_completo};{usuario};{email};{senha}\n")
                    session['usuario_logado'] = usuario
                    return redirect(url_for('home'))
            else:
                flash('Nome de usuário ou email já existe.', 'error')
                return redirect(url_for('cadastro'))
        
    return render_template("cadastro.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    pass

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

