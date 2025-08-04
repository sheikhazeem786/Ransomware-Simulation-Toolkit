import os
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
import json
from datetime import datetime

class KeyManager:
    def __init__(self):
        self.keys_db = {}
        self.log_file = "simulation.log"
        
    def generate_key(self, client_id):
        key = os.urandom(32)  # 256-bit AES key
        iv = os.urandom(16)
        timestamp = datetime.now().isoformat()
        
        self.keys_db[client_id] = {
            'key': b64encode(key).decode('utf-8'),
            'iv': b64encode(iv).decode('utf-8'),
            'timestamp': timestamp,
            'decrypted': False
        }
        self._log_event(f"Key generated for {client_id} at {timestamp}")
        return key, iv
    
    def get_key(self, client_id):
        if client_id in self.keys_db and not self.keys_db[client_id]['decrypted']:
            self.keys_db[client_id]['decrypted'] = True
            self._log_event(f"Key released for {client_id}")
            return (
                b64decode(self.keys_db[client_id]['key']),
                b64decode(self.keys_db[client_id]['iv'])
            )
        return None
    
    def _log_event(self, message):
        with open(self.log_file, 'a') as log:
            log.write(f"{datetime.now().isoformat()} - {message}\n")
    
    def get_stats(self):
        return {
            'total_infected': len(self.keys_db),
            'active_infections': sum(1 for k in self.keys_db.values() if not k['decrypted'])
        }