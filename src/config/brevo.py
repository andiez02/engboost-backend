import sib_api_v3_sdk
from src.config.environment import BREVO_API_KEY, ADMIN_EMAIL_ADDRESS, ADMIN_EMAIL_NAME

# Cấu hình API Client
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key["api-key"] = BREVO_API_KEY

# Tạo instance của API
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def send_email(recipient_email: str, subject: str, html_content: str):
    """Gửi email thông qua Brevo."""
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender={"email": ADMIN_EMAIL_ADDRESS, "name": ADMIN_EMAIL_NAME},
        to=[{"email": recipient_email}],
        subject=subject,
        html_content=html_content,
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        return {"success": True, "message": "Email sent successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}
