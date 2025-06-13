from django import forms


class MessageForm(forms.Form):
    name = forms.CharField(max_length=32)
    reason = forms.CharField(max_length=32)
    message = forms.CharField()


class ContactForm(forms.Form):
    email = forms.EmailField()
    subject = forms.CharField(max_length=128)
    message = forms.CharField()
    send_copy = forms.BooleanField(required=False)
