from django.contrib import admin

# Register your models here.
from .models import *

@admin.register(Product)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'inventory_quantity', 'standard_price', 'current_cost','reorder_point')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Sale)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'sale_date')
    list_filter = ('sale_date',)

admin.site.register(Store)