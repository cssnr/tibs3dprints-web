from django import forms


class BetaForm(forms.Form):
    email = forms.EmailField()
    name = forms.CharField(max_length=255)
    details = forms.CharField(required=False)
