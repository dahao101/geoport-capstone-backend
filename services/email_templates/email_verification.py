def signup_verification(name, pin):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f7f6;
            }}
            .email-container {{
                width: 100%;
                max-width: 600px;
                margin: 30px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .email-header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .email-header h2 {{
                color: #2c8f2e;
                font-size: 24px;
            }}
            .email-body {{
                font-size: 16px;
                line-height: 1.5;
                color: #333;
            }}
            .verification-code {{
                display: inline-block;
                font-size: 20px;
                font-weight: bold;
                color: #ffffff;
                background-color: #2c8f2e;
                padding: 10px 20px;
                border-radius: 4px;
                margin-top: 20px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 12px;
                color: #888;
            }}
            .footer a {{
                color: #2c8f2e;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h2>Welcome to GSU MOTORPOOL</h2>
                <p>Almost there! Please verify your email to complete your registration.</p>
            </div>
            <div class="email-body">
                <p>Dear {name},</p>
                <p>Thank you for registering with us. To complete your registration, please verify your email address by entering the code below:</p>
                <div class="verification-code">
                    {pin}
                </div>
                <p>If you did not request this, please ignore this message. Your account will remain inactive until you complete the verification process.</p>
            </div>
            <div class="footer">
                <p>Best regards,</p>
                <p>The GSU MOTORPOOL Support Team</p>
                <p><a href="http://localhost:5173">Visit our website</a></p>
            </div>
        </div>
    </body>
    </html>
    """
