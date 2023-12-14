import smtplib

from email.message import EmailMessage


class SmtpSender:
    def __init__(self, login: str, password: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 465):
        self.server = smtp_server
        self.port = smtp_port
        self.login = login
        self.password = password

    def send(self, recievers: list[str], subject: str, message: str):
        msg = EmailMessage()
        msg["From"] = self.login
        msg["To"] = recievers
        msg["Subject"] = subject

        try:
            if isinstance(message, str):
                msg.set_content(message, subtype="plain")
            else:
                raise Exception("wrong message format")

            server = smtplib.SMTP_SSL(self.server, self.port)
            server.ehlo()
            server.login(self.login, self.password)
            server.send_message(msg)
            server.quit()
        except Exception as er:
            print(er)
