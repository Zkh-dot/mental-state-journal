from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from models import *
from singleton_logger import Logger

logger = Logger().get_logger()

app = Flask(__name__)
user_table = UserTable()
journal_table = JournalTable()

# Configuration
app.config['SECRET_KEY'] = 'your_strong_secret_key'
app.config["JWT_SECRET_KEY"] = 'your_jwt_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Database Initialization
db = SQLAlchemy(app)

# JWT Initialization
jwt = JWTManager(app)

@app.route('/')
def hello_message():
    return "Hello! It is backend endpoint for app to control your mental state"

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    logger.info(f'Registering user with username: {username}')

    id = user_table.add_user(username, password)    
    if id: 
        access_token = create_access_token(identity=id)
        return jsonify({'message': 'Login Success', 'access_token': access_token})
    else:
        return jsonify({'message': 'Login Failed'}), 401

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    logger.info(f'Logging in user with username: {username}')

    id = user_table.get_user(username)

    if user_table.check_password(password, id):
        access_token = create_access_token(identity=id)
        return jsonify({'message': 'Login Success', 'access_token': access_token})

if __name__ == '__main__':
    app.run(debug=True)

