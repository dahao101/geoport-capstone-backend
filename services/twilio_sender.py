from twilio.rest import Client

account_sid = 'your_account_sid'
auth_token = 'your_auth_token'

client = Client(account_sid, auth_token)

message = client.messages.create(
    body="Hello, this is a test message.",
    from_='+1234567890', 
    to='+09171234567'  
)

print(f"Message sent: {message.sid}")
