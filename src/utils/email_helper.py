import threading
from src.config.brevo import send_email

def send_email_async(email, subject, content):
    thread = threading.Thread(target=send_email, args=(email, subject, content))
    thread.daemon = True
    thread.start()
