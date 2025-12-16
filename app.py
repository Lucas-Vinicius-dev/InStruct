from flask import Flask, render_template

app = Flask(__name__)

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
    return render_template('landing.html')      
# vai ser nossa primeira página. Landing page :D

@app.route('/home')
def home():
    publicacoes = ler_publicacoes()
    return render_template('home.html', posts=publicacoes)
# vai ser a homepage do app onde aparecem os posts dos usuários

@app.route('/publish', methods=['GET'])
def publish():
    return render_template('publish.html')
# vai ser a página relacionada à publicações :) 

@app.route('/send_publish_data', methods=['POST'])
def send_publish_data():
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
    return redirect(url_for('home'))

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

if __name__ == "__main__":
    app.run(debug=True)