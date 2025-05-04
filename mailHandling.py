from http.client import HTTPException

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from starlette.responses import JSONResponse

SENDGRID_API_KEY="here you have to mention our api key"
FROM_EMAIL="tskiran5114@gmail.com"

async def send_reset_email(to_email:str,reset_link:str):
    message=Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject="password reset request",
        html_content=f"""
        <p>hello,</p>
        <p>we recieve a request to reset your password </p>
        <p><a href="{reset_link}">click here to reset your password</a></p>
        <p>this link will expire in 30 minutes. </p>
"""
    )

    try:
        sg=SendGridAPIClient(api_key=SENDGRID_API_KEY)
        response=sg.send(message=message)
        if response.status_code == 202:
            print("success")
            return True
        else:
            print("error")
            return False

        # return response.status_code
    except Exception as e:
        print(f"error{e}")
        return False


