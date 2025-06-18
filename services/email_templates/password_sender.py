
import os
from dotenv import load_dotenv
load_dotenv()
image = 'https://res.cloudinary.com/douasd2ik/image/upload/v1736572350/logo/nzg9hir3bbieqrg42hev.png'


def generated_password_template( name, password):
    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pin Verification</title>
             <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {{
                     font-family: 'Montserrat', sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                    color: #333;
                    min-height: 100vh;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: left;
                    margin-bottom: 25px;
                }}
                .header img {{
                    width: 80px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                }}
                .header h2 {{
                    font-size: 24px;
                    color: green;
                    font-weight: bold;
                    margin: 0;
                }}
                .content {{
                    font-size: 15px;
                    line-height: 1.5;
                    color: #555;
                    margin-bottom: 25px;
                }}
                .content p {{
                    margin-bottom: 15px;
                    text-align: justify;
                }}
                .cta-button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #FA812F;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    text-align: center;
                    transition: background-color 0.3s;
                }}
                .cta-button:hover {{
                    background-color: #d66a1a;
                }}
                .signature {{
                    margin-top: 30px;
                    font-size: 16px;
                    font-weight: bold;
                    color: #333;
                }}
                .footer {{
                    font-size: 12px;
                    color: #888;
                    text-align: center;
                    margin-top: 30px;
                    border-top: 1px solid #ddd;
                    padding-top: 10px;
                }}
                .footer a {{
                    color: #FA812F;
                    text-decoration: none;
                    font-weight: bold;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <img src={image} alt="Geoport Logo" draggable="false" >
                    <h2>Password Generator</h2>
                </div>
                <div class="content">
                    <p>Good day! {name},</p>
                    <p>Welcome to Geoport Malaybalay. In geoport malaybalay you can report or submit road defects and road collisions. You can Log in manually by using your email and this randomly generated password:</p><br/><br/>
                    <h3>{password}</h3><br/><br/>
                    <p>For your security, We encourage you to change the password after receiving it. If you didn’t make this request, you can email us below. </p><br/>
                    <p>If you need further assistance, feel free to contact our support team. </p><br/>
                    <a href="mailto:{os.getenv('EMAIL_SENDER')}" class="cta-button">Contact Us</a>
                </div>
                <div class="signature">
                    <p>Sincerely,</p>
                    <p>CDRRMO EMS OPERATION<br>Geoport Malaybalay</p>
                </div>
                <div class="footer">
                    <p>If you believe this message was sent in error, please <a href="mailto:{os.getenv('EMAIL_SENDER')}">contact us</a>.</p>
                </div>
            </div>
        </body>
        </html>
    """
    return html_content
