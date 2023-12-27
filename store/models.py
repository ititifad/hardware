from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    inventory_quantity = models.PositiveIntegerField()
    standard_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_cost = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_point = models.PositiveIntegerField()


    def __str__(self):
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    sale_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.product.name
    
    class Meta:
        ordering = ('-sale_date',)


    def get_total_price(self):
        return self.quantity * self.product.standard_price
