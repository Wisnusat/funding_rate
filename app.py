from flask import Flask, jsonify
from auth.auth import auth_bp
from auth.auth_middleware import token_required
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
@token_required
def home(current_user):
    return jsonify({'message': f'Welcome, {current_user}!'})

@app.route('/api/data', methods=['GET'])
@token_required
def get_data(current_user):
    data = {
        'message': 'This is a protected data endpoint',
        'data': [1, 2, 3, 4, 5]
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
