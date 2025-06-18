import os
from dotenv import load_dotenv
load_dotenv()
image = 'https://res.cloudinary.com/douasd2ik/image/upload/v1736572350/logo/nzg9hir3bbieqrg42hev.png'


def update_report_processing( name, details, admin_name):
    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Report successful submittion</title>
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
                    <h2>Report successful submittion</h2>
                </div>
                <div class="content">
                    <p>Dear {name},</p>
                    <p>Your report about <strong>{details}</strong> has been successfully submitted. Our administrator is currently reviewing your report. Please wait for future response from our admins.</p>
                    <p>Please note that this is an automated response. If the report is an emergency that needed to have an instant action. We encourage you to call the emergency hotline for immediate action. Thankyou! </p><br />
                    <p>CDRRMO HOTLINE: <span style={{color:'red'}}> 032168465 </span> </p><br/>
                    <p>HOSPITAL HOTLINE: <span style={{color:'red'}}> 215468 </span> </p><br/>
                    <a href="mailto:{os.getenv('EMAIL_SENDER')}" class="cta-button">Contact Us</a>
                </div>
                <div class="signature">
                    <p>Sincerely,</p>
                    <p>{admin_name}<br>Geoport Malaybalay</p>
                </div>
                <div class="footer">
                    <p>If you believe this message was sent in error, please <a href="mailto:{os.getenv('EMAIL_SENDER')}">contact us</a>.</p>
                </div>
            </div>
        </body>
        </html>
    """
    return html_content
