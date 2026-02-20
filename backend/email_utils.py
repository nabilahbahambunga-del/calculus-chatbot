import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def send_verification_email(to_email: str, otp: str):
    try:
        response = resend.Emails.send({
            "from": "PSU AI Tutor <onboarding@resend.dev>",
            "to": to_email,
            "subject": "Your OTP Code",
            "html": f"""
                <h2>PSU AI Tutor Verification</h2>
                <p>Your OTP code is:</p>
                <h1>{otp}</h1>
                <p>This code will expire in 5 minutes.</p>
            """
        })
        return response

    except Exception as e:
        print("Email sending error:", e)
        return None