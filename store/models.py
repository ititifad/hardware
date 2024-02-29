from django.db import models
from django.contrib.auth.models import User

class Store(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    inventory_quantity = models.PositiveIntegerField()
    standard_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_cost = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_point = models.PositiveIntegerField()


    def __str__(self):
        return self.name

class Sale(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    sale_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product.name
    
    class Meta:
        ordering = ('-sale_date',)


    def get_total_price(self):
        return self.quantity * self.product.standard_price
