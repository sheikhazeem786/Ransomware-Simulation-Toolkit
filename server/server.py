from flask import Flask, jsonify, request
from key_manager import KeyManager
import os
from dotenv import load_dotenv
import json

load_dotenv()
app = Flask(__name__)
key_manager = KeyManager()
AUTH_TOKEN = os.getenv("ADMIN_TOKEN", "secure-admin-token")

@app.route('/generate-key/<client_id>', methods=['POST'])
def generate_key(client_id):
    key, iv = key_manager.generate_key(client_id)
    return jsonify({
        'client_id': client_id,
        'key': key.hex(),
        'iv': iv.hex()
    }), 201

@app.route('/decrypt/<client_id>', methods=['POST'])
def decrypt(client_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    key_data = key_manager.get_key(client_id)
    if not key_data:
        return jsonify({"error": "Key not found or already used"}), 404
    
    key, iv = key_data
    return jsonify({
        'key': key.hex(),
        'iv': iv.hex()
    })

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify(key_manager.get_stats())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')