import yaml
from werkzeug.security import generate_password_hash
from pathlib import Path
import getpass  # For secure password input

def add_user_to_auth_file():
    # File path configuration
    auth_file = Path("sailing_auth.yaml")
    
    # Create directory if it doesn't exist
    auth_file.parent.mkdir(exist_ok=True)
    
    # Load existing data or initialize empty structure
    if auth_file.exists():
        with open(auth_file, 'r') as f:
            auth_data = yaml.safe_load(f) or {}
    else:
        auth_data = {}
    
    # Initialize users dictionary if it doesn't exist
    if 'users' not in auth_data:
        auth_data['users'] = {}
    
    # Get user input
    print("\n=== Add New User ===")
    username = input("Username: ").strip()
    
    # Check if user already exists
    if username in auth_data['users']:
        print(f"Error: User '{username}' already exists!")
        return
    
    # Get password securely
    while True:
        password = getpass.getpass("Password: ").strip()
        confirm_password = getpass.getpass("Confirm Password: ").strip()
        
        if password != confirm_password:
            print("Error: Passwords don't match! Try again.")
        elif len(password) < 8:
            print("Error: Password must be at least 8 characters!")
        else:
            break
    
    # Get optional role
    role = input("Role (optional, press Enter to skip): ").strip() or "user"
    
    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    # Add user to data structure
    auth_data['users'][username] = {
        'password': hashed_password,
        'role': role
    }
    
    # Write back to file
    with open(auth_file, 'w') as f:
        yaml.dump(auth_data, f, sort_keys=False)
    
    print(f"\nSuccessfully added user '{username}' with role '{role}'")
    print(f"Credentials saved to {auth_file}")

if __name__ == "__main__":
    add_user_to_auth_file()