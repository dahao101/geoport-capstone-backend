import random
from datetime import datetime, timedelta

def create_pin():
    pin = generate_pin()
    expiration_time = datetime.now() + timedelta(minutes=3)  
    return pin, expiration_time
    
def generate_pin():
    pin = random.randint(100000, 999999)  
    return pin