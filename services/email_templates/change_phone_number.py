def change_phone_template(pin, name):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Phone Number Change Verification</title>
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
                <h2>Change Your Phone Number</h2>
                <p>To verify your phone number change, please enter the code below.</p>
            </div>
            <div class="email-body">
                <p>Dear user : {name},</p>
                <p>We received a request to change the phone number associated with your account. To proceed, please verify your phone number change by entering the code below:</p>
                <div class="verification-code">
                    {pin}
                </div>
                <p>If you did not request this, please ignore this message. Your account will remain unaffected.</p>
            </div>
            <div class="footer">
                <p>Best regards,</p>
                <p>The Support Team</p>
                <p><a href="http://localhost:5173">Visit our website</a></p>
            </div>
        </div>
    </body>
    </html>
    """
