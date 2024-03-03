from django import forms
from .models import *
from django.contrib.auth.models import User


class ProductNameForm(forms.Form):
    name = forms.CharField(label='Product Name', widget=forms.TextInput(attrs={'autofocus': True}))
    # quantity = forms.IntegerField(label='Quantity', widget=forms.NumberInput(attrs={'min': 1}))

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            # Searching by product name instead of barcode
            product = Product.objects.get(name=name)
        except Product.DoesNotExist:
            raise forms.ValidationError('Product with this name does not exist.')
        return product
    
    # def clean_quantity(self):
    #     quantity = self.cleaned_data['quantity']
    #     if quantity <= 0:
    #         raise forms.ValidationError('Quantity must be greater than 0.')
    #     return quantity

# class BarcodeForm(forms.Form):
#     barcode = forms.IntegerField(label='Barcode', widget=forms.TextInput(attrs={'autofocus': True}))

#     def clean_barcode(self):
#         barcode = self.cleaned_data['barcode']
#         try:
#             product = Product.objects.get(barcode=barcode)
#         except Product.DoesNotExist:
#             raise forms.ValidationError('Product with this barcode does not exist.')
#         return product
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'inventory_quantity', 'standard_price', 'current_cost', 'reorder_point']