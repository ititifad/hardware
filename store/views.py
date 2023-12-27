from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
import calendar
from .models import *
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.db.models.functions import TruncMonth
# from barcode import EAN13
# from barcode.writer import ImageWriter
from io import BytesIO
from django.utils import timezone
from datetime import date, timedelta, datetime

from django.db.models import Q
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, FloatField
from django.db import transaction
from .forms import *
from .decorators import allowed_users, admin_only
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views import View
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template



target_date = date.today()
start_date = date.today() - timedelta(days=7)
month_date = date.today().replace(day=1)
year_date = date.today().replace(month=1, day=1)
end_date = date.today()

@login_required(login_url='login')
@admin_only
def homepage(request):
    daily_revenues = Sale.objects.filter(sale_date=target_date).aggregate(total_sales=Sum(models.F('product_id__standard_price') * models.F('quantity')))['total_sales'] 
    sales = Sale.objects.all()[:10]
    count_today_sales = Sale.objects.filter(sale_date=target_date)
    total_sales = count_today_sales.aggregate(total=Sum('quantity'))['total'] 
    daily_profit = Sale.objects.filter(sale_date=target_date).aggregate(total_profit=Sum(models.F('product_id__standard_price') * models.F('quantity')) - Sum(models.F('product_id__current_cost') * models.F('quantity')))['total_profit']
    
    top_products = count_today_sales.values('product_id__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    product_names = [item['product_id__name'] for item in top_products]
    product_quantities = [item['total_quantity'] for item in top_products]

    daily_profit = daily_profit or 0
    daily_revenues = daily_revenues or 0
    total_sales = total_sales or 0


    context = {
        'sales':sales,
        'daily_profit':daily_profit,
        'total_sales':total_sales,
        'daily_revenues':daily_revenues,
        'product_names': product_names,
        'product_quantities': product_quantities
  
    }
    
    return render(request, 'homepage.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['cashier', 'admin'])
def add_product(request):
    if request.method == 'POST':
        # barcode = request.POST.get('barcode')
        name = request.POST.get('name')
        inventory_quantity = request.POST.get('inventory_quantity')
        standard_price = request.POST.get('standard_price')
        current_cost = request.POST.get('current_cost')
        reorder_point = request.POST.get('reorder_point')


        # Create the product
        product = Product.objects.create(
                name=name,
                inventory_quantity=inventory_quantity,
                standard_price=standard_price,
                current_cost=current_cost,
                reorder_point=reorder_point,
                
            )
        # Populate other fields as per your requirement
        product.save()
        messages.success(request, f'Product has been successfully added')

        return redirect('/')  # Replace 'product_list' with your actual product list URL name

    return render(request, 'add_product.html')
# def add_product(request):
#     if request.method == 'POST':
#         name = request.POST['name']
#         inventory_quantity = request.POST['inventory_quantity']
#         standard_price = request.POST['standard_price']
#         current_cost = request.POST['current_cost']
#         reorder_point = request.POST['reorder_point']
#         product = Product(name=name, inventory_quantity=inventory_quantity,
#                           standard_price=standard_price, current_cost=current_cost,
#                           reorder_point=reorder_point)
#         product.save()
#         messages.success(request, 'Product added successfully!')
#         return redirect('add_product')
#     return render(request, 'add_product.html')

def search_product(request):
    if request.method == 'POST':
        search_query = request.POST['search_query']
        products = Product.objects.filter(name__icontains=search_query)
        return render(request, 'search_product.html', {'products': products})
    return render(request, 'search_product.html')



# def sell_products(request):
#     if request.method == 'GET':
#         search_query = request.GET.get('search_query', '')
#         products = Product.objects.filter(
#             Q(barcode__icontains=search_query) |    # Search by barcode
#             Q(name__icontains=search_query)       # Search by name
#         ,inventory_quantity__gte=1)[:]
#         return render(request, 'sell_products.html', {'products': products})
#     elif request.method == 'POST':
#         for key, value in request.POST.items():
#             if key.startswith('quantity_'):
#                 product_id = key.split('_')[1]
#                 quantity = int(value)
#                 if quantity > 0:
#                     product = Product.objects.get(id=product_id)
#                     if quantity <= product.inventory_quantity:
#                         sale = Sale(product=product, quantity=quantity)
#                         sale.save()
#                         product.inventory_quantity -= quantity
#                         product.save()
#                         messages.success(request, 'Product sold successfully!')

#                     else:
#                         messages.info(request, f"No products available in stock")
#         return redirect('sell_products')

# @login_required(login_url='login')
# @admin_only
# def sell_products(request):
#     product = None  # Default value for the product variable
    
#     if request.method == 'POST':
#         form = ProductNameForm(request.POST)
#         if form.is_valid():
#             product_name = form.cleaned_data['name']
#             try:
#                 # Searching by product name instead of barcode
#                 product = Product.objects.get(name=product_name)
#                 quantity = int(request.POST.get('quantity', 0))  # Set default quantity to 1

#                 if quantity > 0 and quantity <= product.inventory_quantity:
#                     product.inventory_quantity -= quantity
#                     product.save()
#                     Sale.objects.create(product=product, quantity=quantity)
#                     messages.success(request, "Product has been successfully sold")
#                     return redirect('sell_products')
#                 else:
#                     messages.error(request, "Invalid quantity entered.")
#             except Product.DoesNotExist:
#                 messages.error(request, "Product not found.")
#         else:
#             messages.error(request, "Invalid form submission.")
#     else:
#         form = ProductNameForm()

#     # If no product name was entered or an error occurred, render the template again
#     return render(request, 'sell_products.html', {'form': form, 'product': product})
class SellProductsView(View):
    template_name = 'sell_products.html'

    def get(self, request):
        # Retrieve search parameter from the query string
        search_query = request.GET.get('search', '')

        # Filter products based on search parameter
        products = Product.objects.filter(
            Q(name__icontains=search_query) | Q(id__icontains=search_query)
        )

        return render(request, self.template_name, {
            'products': products,
            'search_query': search_query,
        })


    def post(self, request):
        selected_product_ids = request.POST.getlist('product')
        quantities = request.POST.getlist('quantity')

        try:
            with transaction.atomic():
                for product_id, quantity in zip(selected_product_ids, quantities):
                    product = Product.objects.get(pk=product_id)
                    quantity = int(quantity)

                    if quantity > 0 and quantity <= product.inventory_quantity:
                        # Create a sale record for each selected product
                        Sale.objects.create(product=product, quantity=quantity)

                        # Update inventory quantity for the sold product
                        product.inventory_quantity -= quantity
                        product.save()
                        messages.success(request, "Products has been successfully sold")

                return redirect('sell_products')
        except Product.DoesNotExist:
            # Handle the case where a selected product does not exist
            pass

        # If there was an error or invalid input, return to the same page with an error message
        products = Product.objects.all()
        return render(request, self.template_name, {'products': products, 'error_message': 'Invalid input'})
# def sell_products(request):
#     product = None  # Default value for the product variable
    
#     if request.method == 'POST':
#         barcode = request.POST.get('barcode')
#         try:
#             product = Product.objects.get(barcode=barcode)
#             quantity = int(request.POST.get('quantity', 0))  # Set default quantity to 1

#             if quantity > 0 and quantity <= product.inventory_quantity:
#                 product.inventory_quantity -= quantity
#                 product.save()
#                 Sale.objects.create(product=product, quantity=quantity)
#                 messages.success(request, "Product has been successfully sold")
#                 return redirect('sell_products')
            
#         except Product.DoesNotExist:
#             messages.error(request, "Product not found.")
#         except Exception as e:
#             messages.error(request, f"An error occurred: {str(e)}")

#     # If no barcode was scanned or an error occurred, render the template again
#     return render(request, 'sell_products.html', {'product': product})




def sales_success(request):
    return render(request, 'sales_success.html')

@login_required(login_url='login')
@admin_only
def sales_reports(request):
    target_date = date.today()
    start_date = date.today() - timedelta(days=7)
    month_date = date.today().replace(day=1)
    year_date = date.today().replace(month=1, day=1)
    end_date = date.today()

    daily_sales = Sale.objects.filter(sale_date=target_date).aggregate(total_sales=Sum(models.F('product_id__standard_price') * models.F('quantity')))['total_sales']
    daily_profit = Sale.objects.filter(sale_date=target_date).aggregate(total_profit=Sum(models.F('product_id__standard_price') * models.F('quantity')) - Sum(models.F('product_id__current_cost') * models.F('quantity')))['total_profit']

    #weekly sales and profit
    weekly_sales = Sale.objects.filter(sale_date__range=[start_date, end_date]).aggregate(total_sales=Sum(models.F('product_id__standard_price') * models.F('quantity')))['total_sales']
    weekly_profit = Sale.objects.filter(sale_date__range=[start_date, end_date]).aggregate(total_profit=Sum(models.F('product_id__standard_price') * models.F('quantity')) - Sum(models.F('product_id__current_cost') * models.F('quantity')))['total_profit']

    #monthly sales and profit
    monthly_sales = Sale.objects.filter(sale_date__range=[month_date, end_date]).aggregate(total_sales=Sum(models.F('product_id__standard_price') * models.F('quantity')))['total_sales']
    monthly_profit = Sale.objects.filter(sale_date__range=[month_date, end_date]).aggregate(total_profit=Sum(models.F('product_id__standard_price') * models.F('quantity')) - Sum(models.F('product_id__current_cost') * models.F('quantity')))['total_profit']

    #yearly sales and profits
    yearly_sales = Sale.objects.filter(sale_date__range=[year_date, end_date]).aggregate(total_sales=Sum(models.F('product_id__standard_price') * models.F('quantity')))['total_sales']
    yearly_profit = Sale.objects.filter(sale_date__range=[year_date, end_date]).aggregate(total_profit=Sum(models.F('product_id__standard_price') * models.F('quantity')) - Sum(models.F('product_id__current_cost') * models.F('quantity')))['total_profit']

    context = {
        'daily_sales':daily_sales,
        'daily_profit':daily_profit,
        'weekly_sales':weekly_sales,
        'weekly_profit':weekly_profit,
        'monthly_sales':monthly_sales,
        'monthly_profit':monthly_profit,
        'yearly_sales':yearly_sales,
        'yearly_profit':yearly_profit
    }

    return render(request, 'sales_reports.html', context)

@login_required(login_url='login')
@admin_only
def stock_data(request):
    stocks = Product.objects.all()
    labels = []
    inventory_quantity = []

    for stock in stocks:
        labels.append(stock.name)
        inventory_quantity.append(stock.inventory_quantity)

    return JsonResponse({'labels': labels, 'quantity': inventory_quantity})

@login_required(login_url='login')
@admin_only
def products(request):
    products = Product.objects.order_by('-inventory_quantity')

    context = {
        'products':products
    }

    return render(request, 'product_list.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


# def sales_return(request):
#     if request.method == 'POST':
#         # Retrieve form data
#         product_id = request.POST.get('product_id')
#         quantity = int(request.POST.get('quantity'))

#         try:
#             # Retrieve product
#             product = Product.objects.get(pk=product_id)
#             # Update inventory quantity
#             product.inventory_quantity += quantity
#             product.save()

#             # Create a new sales return entry
#             return_entry = Sale(product=product, quantity=quantity, sale_date=end_date)
#             return_entry.save()

#             # Redirect to a success page or display a success message
#             return HttpResponseRedirect('/')

#         except Product.DoesNotExist:
#             # Handle the case when the product does not exist
#             return render(request, 'sales_return.html', {'error': 'Invalid product'})

#     else:
#         return render(request, 'sales_return.html')

# def sales_return(request):
#     if request.method == 'POST':
#         barcode_or_name = request.POST['barcode_or_name']
#         products = Product.objects.filter(
#             models.Q(barcode=barcode_or_name) | models.Q(name__icontains=barcode_or_name)
#         )
#         return render(request, 'sales_return.html', {'products': products})
#     return render(request, 'sales_return.html')
@login_required(login_url='login')
@admin_only
def daily_sales_report(request):
    sales = Sale.objects.filter(sale_date=target_date).order_by('-sale_date')
    total_sales = sales.aggregate(total=Sum('quantity'))['total']
    total_revenue = sales.aggregate(total_sales=Sum(models.F('product_id__standard_price') * models.F('quantity')))['total_sales'] or 0
    total_cost = sales.aggregate(cost=Sum(F('quantity') * F('product__current_cost')))['cost']

    # Check if total_cost is None and assign 0 as default value
    total_cost = total_cost or 0

    profit = (float(total_revenue) - float(total_cost))

    context = {
        'sales': sales,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_cost':total_cost,
        'profit':profit
    }

    # Check if the request is for a PDF download
    if request.GET.get('pdf'):
        return render_to_pdf('sales/daily_report_pdf.html', context)
    else:
        return render(request, 'sales/daily_report.html', context)
    # return render(request, 'sales/daily_report.html', context)

@login_required(login_url='login')
@admin_only
def weekly_sales_report(request):
    today = date.today()
    start_date = date.today() - timedelta(days=7)
    end_date = date.today()

    sales = Sale.objects.filter(sale_date__range=[start_date, end_date])
    total_sales = sales.aggregate(total=Sum('quantity'))['total']
    total_revenue = sales.aggregate(revenue=Sum(ExpressionWrapper(F('quantity') * F('product__standard_price'), output_field=FloatField())))['revenue']
    total_cost = sales.aggregate(cost=Sum(F('quantity') * F('product__current_cost')))['cost']

    total_cost = total_cost or 0

    profit = (float(total_revenue) - float(total_cost))

    context = {
        'sales': sales,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_cost':total_cost,
        'profit':profit
    }

    if request.GET.get('pdf'):
        return render_to_pdf('sales/weekly_report_pdf.html', context)
    
    else:
        return render(request, 'sales/weekly_report.html', context)
    
    # return render(request, 'sales/weekly_report.html', {
    #     'sales': sales,
    #     'total_sales': total_sales,
    #     'total_revenue': total_revenue,
    #     'total_cost':total_cost,
    #     'profit':profit
    # })


@login_required(login_url='login')
@admin_only
def monthly_sales_report(request):
    today = date.today()
    month_date = date.today().replace(day=1)
    end_date = date.today()
    
    sales = Sale.objects.filter(sale_date__range=[month_date, end_date])
    total_sales = sales.aggregate(total=Sum('quantity'))['total']
    total_revenue = sales.aggregate(revenue=Sum(ExpressionWrapper(F('quantity') * F('product__standard_price'), output_field=FloatField())))['revenue']
    total_cost = sales.aggregate(cost=Sum(F('quantity') * F('product__current_cost')))['cost']

    total_cost = total_cost or 0

    profit = (float(total_revenue) - float(total_cost))

    context = {
        'sales': sales,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_cost':total_cost,
        'profit':profit
    }

    if request.GET.get('pdf'):
        return render_to_pdf('sales/monthly_report_pdf.html', context)
    
    else:
        return render(request, 'sales/monthly_report.html', context)
    # return render(request, 'sales/monthly_report.html', {
    #     'sales': sales,
    #     'total_sales': total_sales,
    #     'total_revenue': total_revenue,
    #     'total_cost':total_cost,
    #     'profit':profit
    # })


@login_required(login_url='login')
@admin_only
def yearly_sales_report(request):
    year_date = date.today().replace(month=1, day=1)
    end_date = date.today()
    sales = Sale.objects.filter(sale_date__range=[year_date, end_date])
    total_sales = sales.aggregate(total=Sum('quantity'))['total']
    total_revenue = sales.aggregate(revenue=Sum(ExpressionWrapper(F('quantity') * F('product__standard_price'), output_field=FloatField())))['revenue']
    total_cost = sales.aggregate(cost=Sum(F('quantity') * F('product__current_cost')))['cost']

    total_cost = total_cost or 0

    profit = (float(total_revenue) - float(total_cost))

    context = {
        'sales': sales,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_cost':total_cost,
        'profit':profit
    }

    if request.GET.get('pdf'):
        return render_to_pdf('sales/yearly_report_pdf.html', context)
    
    else:
        return render(request, 'sales/yearly_report.html', context)
    # return render(request, 'sales/yearly_report.html', {
    #     'sales': sales,
    #     'total_sales': total_sales,
    #     'total_revenue': total_revenue,
    #     'total_cost':total_cost,
    #     'profit':profit
    # })


@login_required(login_url='login')
@admin_only
def inventory_value_report(request):
    stocks = Product.objects.all()
    labels = []
    inventory_quantity = []

    
    total_cost = sum(product.inventory_quantity * product.current_cost for product in stocks)
    total_value = sum(product.inventory_quantity * product.standard_price for product in stocks)

    profit = (float(total_value) - float(total_cost))

    for stock in stocks:
        labels.append(stock.name)
        inventory_quantity.append(stock.inventory_quantity)

    return render(request, 'sales/inventory_report.html', {
        'products': stocks,
        'total_cost': total_cost,
        'total_value': total_value,
        'labels': labels, 
        'quantity': inventory_quantity,
        'profit':profit
    })


@login_required(login_url='login')
@admin_only
def top_selling_products(request):
    top_products = Product.objects.annotate(total_quantity_sold=models.Sum('sale__quantity')).order_by('-total_quantity_sold')[:10]
    return render(request, 'sales/top_selling_products.html', {'top_products': top_products})


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    return None