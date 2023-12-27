from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('cashier/', views.sell_products, name='sell_products'),
    path('add-product/', views.add_product, name='add_product'),
    path('products/', views.products, name='stocks'),
    path('inventory/value/', views.inventory_value_report, name='value_report'),
    # path('sales/return/', views.sales_return, name='sales_return'),
    # path('return/<int:product_id>/', views.perform_sales_return, name='perform_sales_return'),
    path('daily/', views.daily_sales_report, name='daily_sales_report'),
    path('weekly/', views.weekly_sales_report, name='weekly_sales_report'),
    path('monthly/', views.monthly_sales_report, name='monthly_sales_report'),
    path('yearly/', views.yearly_sales_report, name='yearly_sales_report'),
    path('search-product/', views.search_product, name='search_product'),
    path('top-selling/', views.top_selling_products, name='top_selling_products'),
    path('stock_data/', views.stock_data, name='stock'),
    path('sales/', views.sales_reports, name='sales-reports'),
    path('sell/success/', views.sales_success, name='sales_success'),

   
]
