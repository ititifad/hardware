from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
# from .views import SellProductsView
# from .views import save_sale

urlpatterns = [
    path('', views.homepage, name='home'),
    # path('make-sale/', views.make_sale, name='make_sale'),
    path('sell-products/', views.sell_products, name='sell_products'),
    path('add-product/', views.add_product, name='add_product'),
    path('products/', views.products, name='stocks'),
    path('inventory/value/', views.inventory_value_report, name='value_report'),
    path('logout/', views.logout_view, name='logout_view'),
    path('sold_products/', views.sold_products, name='sold_products'),
    # path('get_product_details/', views.get_product_details, name='get_product_details'),
    path('generate_pdf_receipt/<int:sale_id>/', views.generate_pdf_receipt, name='generate_pdf_receipt'),
    path('download_receipt/<int:sale_id>/', views.download_receipt, name='download_receipt'),
    path('reorder-point-products/', views.reorder_point_products, name='reorder_point_products'),
    path('quick-inventory-adjustment/', views.quick_inventory_adjustment, name='quick_inventory_adjustment'),
    path('quick-price-adjustment/', views.quick_price_adjustment, name='quick_price_adjustment'),
    # path('save-sale/', save_sale, name='save_sale'),
    # path('counter/', SellProductsView.as_view(), name='sell_products'),
    # path('sales/return/', views.sales_return, name='sales_return'),
    # path('return/<int:product_id>/', views.perform_sales_return, name='perform_sales_return'),
    path('daily/', views.daily_sales_report, name='daily_sales_report'),
    path('weekly/', views.weekly_sales_report, name='weekly_sales_report'),
    path('monthly/', views.monthly_sales_report, name='monthly_sales_report'),
    path('yearly/', views.yearly_sales_report, name='yearly_sales_report'),
    path('search-product/', views.search_product, name='search_product'),
    path('top-selling/', views.top_selling_products, name='top_selling_products'),
    path('stock_data/', views.stock_data, name='stock'),
    path('sales-reports/', views.sales_reports, name='sales-reports'),
    path('sell/success/', views.sales_success, name='sales_success'),

   
]
