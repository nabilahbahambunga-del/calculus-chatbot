import smtplib
import os
from email.message import EmailMessage

def send_verification_email(to_email: str, token: str):

    msg = EmailMessage()
    msg["Subject"] = "Verify your Calculus Chatbot account"
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = to_email

    verify_link = f"https://calculus-backend.onrender.com/verify/{token}"

    msg.set_content(f"""
สวัสดีค่ะ

กรุณาคลิกลิงก์ด้านล่างเพื่อยืนยันบัญชีของคุณ:

{verify_link}

หากคุณไม่ได้สมัครสมาชิก กรุณาเพิกเฉยอีเมลนี้
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        smtp.send_message(msg)
