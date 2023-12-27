from django import forms
from .models import *

from django import forms

class BarcodeForm(forms.Form):
    barcode = forms.IntegerField(label='Barcode', widget=forms.TextInput(attrs={'autofocus': True}))

    def clean_barcode(self):
        barcode = self.cleaned_data['barcode']
        try:
            product = Product.objects.get(barcode=barcode)
        except Product.DoesNotExist:
            raise forms.ValidationError('Product with this barcode does not exist.')
        return product
