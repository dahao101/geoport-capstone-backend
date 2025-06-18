from backend.services.email_templates.password_sender import generated_password_template
from backend.services.password_generator import generate_password
from backend.services.email_sender import emailSender
from fastapi import HTTPException, status
from fastapi import HTTPException, status, BackgroundTasks


async def google_signup(background_task: BackgroundTasks):
    try:
        print('signup google reached')
        # Logic for google login including the saving of credentials
        
        # Template setup
        subject = 'GENERATED PASSWORD'
        email = 'martdahao@gmail.com'
        name = 'Mart Ervin Dahao'
        password = generate_password()
        template = generated_password_template(name,password)

        # Send the email portion including the template
        background_task.add_task(emailSender, email, subject, template)

    except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))  