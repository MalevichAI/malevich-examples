from malevich.square import Context, processor

from .smtp_sender import SmtpSender


@processor()
def send_newsletter(recipients, articles, context: Context):
    app_cfg = context.app_cfg
    sender = SmtpSender(app_cfg["login"], app_cfg["password"])
    top_n = app_cfg.get("top_n", 5)
    
    text = ('\n' * 2 + '-' * 50 + '\n' * 2).join(list(articles[:top_n]["text"]))
    for _, row in recipients.iterrows():
        sender.send([row["recipient"]], row["title"], text)

    recipients = recipients.drop(["title"], axis=1)
    recipients["status"] = ["success"] * len(recipients)
    return recipients
