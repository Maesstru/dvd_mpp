
from django import forms
from . import models
from .models import Binevoitor
import re
import hashlib

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=100, label="Email",label_suffix="",widget=forms.TextInput(attrs={'placeholder': 'placeholder'}))
    parola = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'placeholder'}), max_length=100, label="Parola",label_suffix="")

class EmailForm(forms.Form):
    email = forms.EmailField(max_length=100, label="Email",label_suffix="",widget=forms.TextInput(attrs={'placeholder': 'placeholder'}))

class UpdateParolaForm(forms.Form):
    parola_noua = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'placeholder'}), max_length=100, label="Parola noua",label_suffix="")
    confirma_parola = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'placeholder'}), max_length=100, label="Confirma parola",label_suffix="")


class SignupForm(forms.Form):
    nume = forms.CharField(max_length=100, label='Nume',label_suffix="",widget=forms.TextInput(attrs={'placeholder': 'placeholder'}))
    telefon = forms.CharField(max_length=20, label='Telefon',label_suffix="",widget=forms.TextInput(attrs={'placeholder': 'placeholder'}))
    email = forms.EmailField(max_length=100, label="Email",label_suffix="",widget=forms.TextInput(attrs={'placeholder': 'placeholder'}))
    parola = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'placeholder'}), max_length=100, label="Parola",label_suffix="")
    confirmare_parola = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'placeholder'}), max_length=100, label="Confirma Parola",label_suffix="")
    

    def clean(self):
        clean_data = super().clean()
        if clean_data['parola'] != clean_data['confirmare_parola']:
            self.add_error(None, "Parolele nu corespund!")
        import re
        if not re.fullmatch(r'^\d{10}$|^\+\d{12}$', clean_data['telefon']):
            self.add_error(None,"Numar de telefon invalid!")
        return self.cleaned_data

class MainFilterForm(forms.Form):
    gen = forms.ChoiceField(
        label="Gen",
        initial="NONE",
        choices=[('NONE','Aleator')] + models.Copil.GEN,
    )
    def __init__(self, *args, **kwargs):
        varste_ramase = kwargs.pop('varste_ramase')
        super(MainFilterForm, self).__init__(*args, **kwargs)

        self.fields["varsta"] = forms.ChoiceField(
            label="Varsta",
            initial="NONE",
            choices=[(-1,'Aleator')] + varste_ramase,
        )
class UpdateUserForm(forms.ModelForm):
    confirma_parola = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'placeholder'}),
        label="Confirmă parola",
        max_length=100
    )
    class Meta:
        model = Binevoitor
        fields = ['email', 'nume', 'telefon','parola']
        widgets = {
            'parola': forms.PasswordInput(attrs={'placeholder': 'placeholder'}),
        }
        labels = {
            'parola': 'Parolă nouă'  # Change 'parola' field label here
        }
    def clean(self):
        cleaned_data = super().clean()
        parola = cleaned_data.get("parola")
        confirma_parola = cleaned_data.get("confirma_parola")
        if parola and confirma_parola and parola != confirma_parola:
            self.add_error("Parolele nu corespund!")

        if parola:
            cleaned_data['parola']=str(hashlib.sha256(parola.encode('utf-8')).hexdigest())
        if not re.fullmatch(r'^\d{10}$|^\+\d{12}$' ,cleaned_data['telefon']):
            self.add_error(None,"Numar de telefon invalid!")
        return cleaned_data
