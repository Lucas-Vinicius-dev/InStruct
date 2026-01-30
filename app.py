import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')

from app.main import main_bp
from app.admin import admin_bp

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(main_bp)



if __name__ == "__main__":
    app.run(debug=True)

