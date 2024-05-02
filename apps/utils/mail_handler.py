from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from config.settings import EMAIL_HOST_USER


class EmailHandler:
    def __init__(self, to, subject, message=None, cc=None, bcc=None, reply_to=None, files=None):
        self.subject = subject
        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.reply_to = reply_to
        self.message = message
        self.files = files

        self.email = EmailMessage()
        self.email.to = [x.strip() for x in self.to.split(",")]
        self.email.subject = self.subject
        self.email.from_email = EMAIL_HOST_USER

        if self.message:
            self.email.body = self.message

        if self.files:
            for file in self.files:
                self.email.attach(file["name"], file["bytes"])

    # html: This method format the email message to html format.
    def html(self, template, context, logos=None):
        self.email.content_subtype = "html"
        self.email.mixed_subtype = "related"
        self.email.body = render_to_string(template, context)
        return self

    # send: This method actually send the email on after response.
    def send(self):
        if self.cc:
            self.email.cc = [x.strip() for x in self.cc.split(",")]

        if self.bcc:
            self.email.bcc = [x.strip() for x in self.bcc.split(",")]

        if self.reply_to:
            self.email.reply_to = [x.strip() for x in self.reply_to.split(",")]
        try:
            dat = self.email.send()
            return {"status": True}
        except Exception as ex:
            return {"status": False}
