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

    id = async_to_sync(user_table.add_user(username, password))    
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

    id = async_to_sync(user_table.get_user(username))

    if async_to_sync(user_table.check_password(password, id)):
        access_token = create_access_token(identity=id)
        return jsonify({'message': 'Login Success', 'access_token': access_token})
    
@app.route('/get_name', methods=['GET'])
@jwt_required()
def get_name():
    """basicly test rout to check, if jwt auth is correct"""
    user_id = get_jwt_identity()
    user_name = async_to_sync(user_table.get_user(user_id=user_id))

    if user_name:
        return jsonify({'message': 'User found', 'name': user_name})
    else:
        return jsonify({'message': 'User not found'}), 404   


@app.route('/journals', method=["GET"])
@jwt_required
def get_journals():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"message": "bad jwt"}), 400
    user_journals = async_to_sync(journal_table.get_posts(user_id))
    return jsonify({"journal_posts": user_journals})


@app.route('/journals', method=["POST"])
@jwt_required
def post_journal():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"message": "bad jwt"}), 400
    data = request.get_json()
    try: 
        async_to_sync(journal_table.add_post(
            user_id=user_id,
            line_mark=data['mark'],
            category=data['category'],
            line_text=data['line_text']
        ))
    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": "you may not have passes some fields. required mark, category, line_text"}), 400
    return jsonify({"message": "post added"})
    

@app.route("/journal/<number>")
@jwt_required
def get_journal(number):
    number = int(number)
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"message": "bad jwt"}), 400
    return jsonify(async_to_sync(journal_table.get_post(user_id, number)))
    
    
if __name__ == '__main__':
    app.run(debug=True)