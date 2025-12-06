import json
import base64
import os

try:
    with open('infra/terraform.tfstate', 'r') as f:
        state = json.load(f)
    
    key_value = state['outputs']['service_account_key']['value']
    
    # Check if it needs decoding
    if not key_value.strip().startswith('{'):
        print("Decoding Base64 key...")
        decoded = base64.b64decode(key_value).decode('utf-8')
    else:
        print("Key is already JSON.")
        decoded = key_value
        
    with open('gcp_key.json', 'w') as f:
        f.write(decoded)
        
    print("SUCCESS: Key written to gcp_key.json")
    
except Exception as e:
    print(f"ERROR: {e}")
