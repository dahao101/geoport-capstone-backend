import os
import socket
from dotenv import load_dotenv

load_dotenv()

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  
        local_ip = s.getsockname()[0]
        s.close()
        print('the ip fetched from google is ',local_ip)
        return local_ip
    except:
        return ""
    
local_ip = get_ip()

env_file = ".env"
if not os.getenv("APP_IP") or os.getenv("APP_IP") != local_ip:
    with open(env_file, "a") as f:
        f.write(f"\nAPP_IP={local_ip}\n")

