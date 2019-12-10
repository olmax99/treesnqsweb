from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


"""
NOTE: forms.Form Classes essentially translate to html <input ... > elements or
      are used to directly replace values inside of them.
      - Used as input for GET request on the current view, where the data is 
        forwarded to another url via <form> element containing 
        action="{% url "..."}" method="POST"
      - Used as input for POST request on the current view directly replacing 
        arguments in an existing <input > element
"""

PAYMENT_CHOICES = [
    ('S', 'Stripe')
]


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Limmatplatz 1234'
    }))
    apartment_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '2nd Floor'
    }), required=False)
    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
    }))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    """
    CouponForm represents the following html input element (go to order_snippet.html)
    <input type="text" class="form-control" placeholder="Promo code" \
     aria-label="Recipient's username" aria-describedby="basic-addon2"
    """
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria - label': 'Recipient\'s username',
        'aria - describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    refund_email = forms.EmailField()
