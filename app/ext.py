from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flasgger import Swagger

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Capsone SMT6 API",
        "version": "1.0.0",
        "description": "API untuk aplikasi capstone",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    }
}

swagger = Swagger(template=swagger_template)