import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "7b2e1e4fd7a6c9c4f81df2a0f46bcd11e35bb4f9fe4b1c3a08429a1d6ce4f07d"

# Cargamos configuraciones
app.config.from_object('config.DevelopmentConfig')
app.config["UPLOAD_CONFS"] = "uploads"


os.makedirs(app.config["UPLOAD_CONFS"], exist_ok=True)

# Generamos las Base de Datos
db = SQLAlchemy(app)

