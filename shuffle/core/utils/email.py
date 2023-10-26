from django.conf import settings

from django.core.mail import EmailMultiAlternatives as EmailMessage
from django.core.mail.backends.console import EmailBackend as BaseEmailBackend

from django.utils.html import strip_tags
from django.template.loader import render_to_string

def assemble_email(attachment_file=None, html_content=None, to=None, *args, **kwargs):
    email_message = EmailMessage(to=([to] if not type(to) in (tuple, list) else to), *args, **kwargs)

    if html_content is not None:
        email_message.attach_alternative(html_content, "text/html")

    if attachment_file is not None:
        email_message.attach(
            "proforma_invoice.pdf",
            attachment_file.getvalue(),
            'application/pdf')

    return email_message

def send_mail(
    to=None, 
    subject=None, 
    text_content=None, 
    template_name=None, 
    template_context=None, 
    html_content=None, 
    attachment_file=None,
    from_email=None, 
    bcc=None,
    send_immediately=True,
    reply_to=None,
    **kwargs
):
    if html_content and template_context and template_name:
        raise TypeError("You defined both html_content and template_name and template_context")
    
    if html_content is None and template_context and template_name:
        html_content = render_to_string(template_name, template_context) # render with dynamic value
        text_content = strip_tags(html_content) # Strip the html tag. So people can see the pure text at least.

    #Prepare it!
    email_message = assemble_email(
        subject=subject,
        body=text_content,
        to=to,
        from_email=(from_email or settings.NDI_SUPPORT_EMAIL),
        bcc=(bcc or settings.NDI_SUPPORT_TEAM_EMAILS),
        reply_to=(reply_to or [settings.NDI_REPLY_EMAIL]),
        html_content=html_content,
        **kwargs)

    if send_immediately:
        #Send it now!
        email_message.send()

    return email_message

class DummyEmailBackend(BaseEmailBackend):
    messages = []

    def __init__(self, *args, **kwargs):
        super(DummyEmailBackend, self).__init__(*args, **kwargs)

    def write_message(self, message):
        DummyEmailBackend.messages.append(message)
        return super(DummyEmailBackend, self).write_message(message)

    def send_messages(self, email_messages):
        for message in email_messages:
            self.write_message(message)
        return super(DummyEmailBackend, self).send_messages(email_messages)