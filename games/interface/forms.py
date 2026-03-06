from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    balance = forms.DecimalField(min_value=0, max_digits=12, decimal_places=2, initial=1000)

class RoulettePlayForm(forms.Form):
    BET_TYPES = (
        ("number", "Number"),
        ("color", "Color"),
        ("odd_even", "Odd / Even"),
    )
    bet_type = forms.ChoiceField(choices=BET_TYPES)
    bet_value = forms.CharField(max_length=20)
    amount = forms.DecimalField(min_value=0.01, max_digits=12, decimal_places=2)