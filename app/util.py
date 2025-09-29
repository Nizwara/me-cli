import os
import sys
import requests

def manual_load_dotenv():
    """
    Manually loads environment variables from a .env file in the project root.
    This is a robust fallback if the python-dotenv library fails.
    """
    try:
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dotenv_path = os.path.join(project_dir, '.env')

        if not os.path.exists(dotenv_path):
            # print("No .env file found, skipping manual load.")
            return

        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'') # Remove quotes
                    os.environ.setdefault(key, value)
        # print(".env file manually loaded.")
    except Exception as e:
        print(f"Error manually loading .env file: {e}")


# Load API key from text file named api.key
def load_api_key() -> str:
    if os.path.exists("api.key"):
        with open("api.key", "r", encoding="utf8") as f:
            api_key = f.read().strip()
        if api_key:
            print("API key loaded successfully.")
            return api_key
        else:
            print("API key file is empty.")
            return ""
    else:
        print("API key file not found.")
        return ""
    
def save_api_key(api_key: str):
    with open("api.key", "w", encoding="utf8") as f:
        f.write(api_key)
    print("API key saved successfully.")
    
def delete_api_key():
    if os.path.exists("api.key"):
        os.remove("api.key")
        print("API key file deleted.")
    else:
        print("API key file does not exist.")

def verify_api_key(api_key: str, *, timeout: float = 10.0) -> bool:
    """
    Returns True iff the verification endpoint responds with HTTP 200.
    Any network error or non-200 is treated as invalid.
    """
    try:
        url = f"https://crypto.mashu.lol/api/verify?key={api_key}"
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            json_resp = resp.json()
            print(f"API key is valid.\nId: {json_resp.get('user_id')}\nOwner: @{json_resp.get('username')}")
            return True
        else:
            print(f"API key is invalid. Server responded with status code {resp.status_code}.")
            return False
    except requests.RequestException as e:
        print(f"Failed to verify API key: {e}")
        return False

def ensure_api_key() -> str:
    """
    Load api.key if present; otherwise prompt the user.
    Always verifies the key. Saves only if valid.
    Exits the program if invalid or empty.
    """
    # Try to load from environment variable first
    api_key_from_env = os.getenv("API_KEY")
    if api_key_from_env:
        print("API key loaded from environment variable.")
        if verify_api_key(api_key_from_env):
            return api_key_from_env
        else:
            print("API key from environment variable is invalid. Please check your .env file.")
            sys.exit(1)

    # Try to load an existing key
    current = load_api_key()
    if current:
        if verify_api_key(current):
            return current
        else:
            print("Existing API key is invalid. Please enter a new one.")

    # Prompt user if missing or invalid
    print("Dapatkan API key di Bot Telegram @fyxt_bot")
    api_key = input("Masukkan API key: ").strip()
    if not api_key:
        print("API key tidak boleh kosong. Menutup aplikasi.")
        sys.exit(1)

    if not verify_api_key(api_key):
        print("API key tidak valid. Menutup aplikasi.")
        delete_api_key()
        sys.exit(1)

    save_api_key(api_key)
    return api_key
