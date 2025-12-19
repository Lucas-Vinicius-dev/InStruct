# Projeto de Programação para Web 1 - Instruct
## Descrição do Projeto
InStruct é uma plataforma comunitária focada no aprendizado colaborativo de algoritmos e estruturas de dados. É um espaço dedicado para desenvolvedores postarem, visualizarem e discutirem soluções para problemas de programação competitiva.

<img width="1875" height="908" alt="image" src="https://github.com/user-attachments/assets/9f2949cb-cc75-414f-9d5f-df62f37f1011" />

## Executando o projeto localmente
```
git clone https://github.com/Lucas-Vinicius-dev/InStruct.git
python -m venv venv

# ativação no Windows
venv\Scripts\activate

# ativação no Linux/macOS
source venv/bin/activate
```
## Configurando o projeto
### Crie um arquivo .env na mesma pasta de app.py e gere a chave no terminal usando:
```
python -c 'import os; print(os.urandom(24).hex())'
```
### Depois, coloque dentro do .env a chave gerada
```
FLASK_SECRET_KEY = chave_gerada_no_python
```
### Instale as dependências
```
pip install -r requirements.txt
```
### Execute o back-end
```
python app.py
```

O URL será: http://127.0.0.1:5000/

