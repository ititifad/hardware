import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
import calendar
from .models import *
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseRedirect, Http404
from django.db.models.functions import TruncMonth
# from barcode import EAN13
# from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.utils import timezone
from datetime import date, timedelta, datetime
from django.views.decorators.http import require_POST
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

from django.template.loader import render_to_string


target_date = date.today()
start_date = date.today() - timedelta(days=7)
month_date = date.today().replace(day=1)
year_date = date.today().replace(month=1, day=1)
end_date = date.today()

@login_required(login_url='login')
@admin_only
def homepage(request):
    daily_revenues = Sale.objects.filter(sale_date=target_date).aggregate(total_sales=Sum(models.F('product_id__standard_price') * models.F('quantity')))['total_sales'] 
    sales = Sale.objects.filter(sale_date=target_date).order_by('-id')
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
# class SellProductsView(View):
#     template_name = 'sell_products.html'

#     def get(self, request):
#         # Retrieve search parameter from the query string
#         search_query = request.GET.get('search', '')

#         # Filter products based on search parameter
#         products = Product.objects.filter(
#             Q(name__icontains=search_query) | Q(id__icontains=search_query)
#         )

#         return render(request, self.template_name, {
#             'products': products,
#             'search_query': search_query,
#         })


#     def post(self, request):
#         selected_product_ids = request.POST.getlist('product')
#         quantities = request.POST.getlist('quantity')

#         try:
#             with transaction.atomic():
#                 for product_id, quantity in zip(selected_product_ids, quantities):
#                     product = Product.objects.get(pk=product_id)
#                     quantity = int(quantity)

#                     if quantity > 0 and quantity <= product.inventory_quantity:
#                         # Create a sale record for each selected product
#                         Sale.objects.create(product=product, quantity=quantity)

#                         # Update inventory quantity for the sold product
#                         product.inventory_quantity -= quantity
#                         product.save()
#                         messages.success(request, "Products has been successfully sold")

#                 return redirect('sell_products')
#         except Product.DoesNotExist:
#             # Handle the case where a selected product does not exist
#             pass

#         # If there was an error or invalid input, return to the same page with an error message
#         products = Product.objects.all()
#         return render(request, self.template_name, {'products': products, 'error_message': 'Invalid input'})

# @login_required(login_url='login')
# @admin_only
# def sell_products(request):
#     products = Product.objects.all()
#     return render(request, 'sell_products.html', {'products': products})

# @require_POST
# def get_product_details(request):
#     product_id = request.POST.get('product_id')
#     product = get_object_or_404(Product, pk=product_id)
#     data = {
#         'name': product.name,
#         'inventory_quantity': product.inventory_quantity,
#         'standard_price': str(product.standard_price),
#     }
#     return JsonResponse(data)

# @require_POST
# def make_sale(request):
#     product_id = request.POST.get('product_id')
#     quantity = request.POST.get('quantity')

#     product = get_object_or_404(Product, pk=product_id)

#     if quantity > 0 and quantity <= product.inventory_quantity:
#         # Update inventory quantity
#         product.inventory_quantity -= quantity
#         product.save()

#         # Save the sale
#         Sale.objects.create(product=product, quantity=quantity)

#         return JsonResponse({'success': True, 'message': 'Sale successfully recorded.'})
#     else:
#         return JsonResponse({'success': False, 'message': 'Invalid quantity entered for the sale.'})

# def sell_products(request):
#     products = Product.objects.all()

#     if request.method == 'POST':
#         selected_products = request.POST.getlist('selected_products')
#         quantities = request.POST.getlist('quantities')

#         # Use a set to track unique product IDs
#         unique_product_ids = set()

#         for product_id, quantity in zip(selected_products, quantities):
#             # Check if the product ID is unique
#             if product_id not in unique_product_ids:
#                 unique_product_ids.add(product_id)

#                 product = Product.objects.get(pk=product_id)

#                 # Check if there is enough inventory before selling
#                 if product.inventory_quantity >= int(quantity):
#                     sale = Sale(product=product, quantity=quantity)
#                     sale.save()

#                     # Update inventory quantity
#                     product.inventory_quantity -= int(quantity)
#                     product.save()
#                 else:
#                     # Handle insufficient inventory
#                     messages.error(request, f"Insufficient inventory for {product.name}. Available: {product.inventory_quantity}")

#         return redirect('sell_products')

#     return render(request, 'sell_products.html', {'products': products})


def generate_pdf_receipt(sales):
    # Create a BytesIO buffer to save the PDF
    buffer = BytesIO()

    # Create a PDF canvas
    p = canvas.Canvas(buffer)

    # Initialize total price
    total_price = Decimal(0)

    # Customize the PDF content
    p.drawString(100, 800, "Receipt for Sales")

    for sale in sales:
        product = sale.product
        quantity = sale.quantity

        p.drawString(100, 780, f"Product: {product.name}")
        p.drawString(100, 760, f"Quantity: {quantity}")
        p.drawString(100, 740, f"Total Price: ${product.standard_price * quantity}")
        p.drawString(100, 720, f"Sale Date: {sale.sale_date}")

        # Update total price
        total_price += product.standard_price * quantity

        # Move to the next receipt section
        p.showPage()

    # Add summary information to the last page
    p.drawString(100, 800, "Summary")
    p.drawString(100, 780, f"Total Price for All Sales: ${total_price}")

    # Save the PDF content
    p.save()

    # Reset the buffer position to the beginning
    buffer.seek(0)

    # Create the response with the PDF content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="receipts_combined.pdf"'
    response.write(buffer.getvalue())

    return response

# def sell_products(request):
#     products = Product.objects.all()

#     if request.method == 'POST':
#         selected_products = request.POST.getlist('selected_products')
#         quantities = request.POST.getlist('quantities')

#         # Use a set to track unique product IDs
#         unique_product_ids = set()

#         for product_id, quantity in zip(selected_products, quantities):
#             # Check if the product ID is unique
#             if product_id not in unique_product_ids:
#                 unique_product_ids.add(product_id)

#                 product = Product.objects.get(pk=product_id)

#                 # Check if there is enough inventory before selling
#                 if product.inventory_quantity >= int(quantity):
#                     sale = Sale(product=product, quantity=quantity)
#                     sale.save()

#                     # Update inventory quantity
#                     product.inventory_quantity -= int(quantity)
#                     product.save()
#                     # Success message for selling the product
#                     messages.success(request, f"Successfully sold {quantity} unit(s) of {product.name}.")
#                 else:
#                     # Handle insufficient inventory
#                     messages.info(request, f"Insufficient inventory for {product.name}. Available: {product.inventory_quantity}")

#         # # Retrieve the sales for which the receipt will be generated
#         # sales_to_generate_receipt = Sale.objects.filter(product_id__in=unique_product_ids)

#         # # Generate a single receipt for all sales
#         # if sales_to_generate_receipt:
#         #     return generate_pdf_receipt(sales_to_generate_receipt)

#     return render(request, 'sell_products.html', {'products': products})
# def sell_products(request):
#     products = Product.objects.all()

#     if request.method == 'POST':
#         selected_products = request.POST.getlist('selected_products')
#         quantities = request.POST.getlist('quantities')

#         unique_product_ids = set()
#         error_messages = []
#         newly_created_sales = []  # Store sales for the receipt

#         for product_id, quantity in zip(selected_products, quantities):
#             if product_id not in unique_product_ids:
#                 unique_product_ids.add(product_id)

#                 try:
#                     product = Product.objects.get(pk=product_id)
#                     quantity = int(quantity)

#                     if product.inventory_quantity >= quantity:
#                         sale = Sale(product=product, quantity=quantity)
#                         sale.save()
#                         newly_created_sales.append(sale)  # Append to the list

#                         product.inventory_quantity -= quantity
#                         product.save()
#                         messages.success(request, f"Successfully sold {quantity} unit(s) of {product.name}.")
#                     else:
#                         error_messages.append(f"Insufficient inventory for {product.name}. Available: {product.inventory_quantity}")

#                 except Product.DoesNotExist:
#                     error_messages.append(f"Product with ID {product_id} not found.")
#                 except ValueError:
#                     error_messages.append(f"Invalid quantity value for product ID {product_id}")

#         # If no errors, generate the PDF receipt
#         if not error_messages: 
#             html_content = render_to_string('receipt_template.html', {'sales': newly_created_sales})

#             result = BytesIO()
#             pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), result)

#             if not pdf.err:
#                 response = HttpResponse(result.getvalue(), content_type='application/pdf')
#                 response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
#                 return response
#             else:
#                 messages.error(request, "An error occurred while generating the PDF receipt.")

#         # If errors, display and allow product selection again
#         for message in error_messages:
#             messages.error(request, message) 

#     return render(request, 'sell_products.html', {'products': products})

def sell_products(request):
    products = Product.objects.all()

    if request.method == 'POST':
        selected_products = request.POST.getlist('selected_products')
        quantities = request.POST.getlist('quantities')

        unique_product_ids = set()
        error_messages = []
        newly_created_sales = []  # Store sales for the receipt

        for product_id, quantity in zip(selected_products, quantities):
            if product_id not in unique_product_ids:
                unique_product_ids.add(product_id)

                try:
                    product = Product.objects.get(pk=product_id)
                    quantity = int(quantity)

                    if product.inventory_quantity >= quantity:
                        sale = Sale(product=product, quantity=quantity)
                        sale.save()
                        newly_created_sales.append(sale)  # Append to the list

                        product.inventory_quantity -= quantity
                        product.save()
                        messages.success(request, f"Successfully sold {quantity} unit(s) of {product.name}.")
                    else:
                        error_messages.append(f"Insufficient inventory for {product.name}. Available: {product.inventory_quantity}")

                except Product.DoesNotExist:
                    error_messages.append(f"Product with ID {product_id} not found.")
                except ValueError:
                    error_messages.append(f"Invalid quantity value for product ID {product_id}")

        # If no errors, redirect to dashboard before generating the PDF receipt
        if not error_messages: 
            return redirect('home')

        # If errors, display and allow product selection again
        for message in error_messages:
            messages.error(request, message) 

    return render(request, 'sell_products.html', {'products': products})


def download_receipt(request, sale_id):
    sale = get_object_or_404(Sale, pk=sale_id)

    # Generate a PDF receipt for the specific sale
    pdf_response = generate_pdf_receipt([sale])

    # Set the Content-Disposition header for download
    pdf_response['Content-Disposition'] = f'attachment; filename="receipt_{sale.id}.pdf"'

    return pdf_response


def generate_sale_receipt(sales):
    # 1. Prepare HTML Content
    html_content = render_to_string('receipt_template.html', {'sales': sales}) 

    # 2. Convert HTML to PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), result)

    if not pdf.err:
        return result.getvalue()
    else:
        return None  # Or handle the error more gracefully

# @require_POST
# def save_sale(request):
#     try:
#         sales_data = request.POST.get('sales')
#         sales = json.loads(sales_data)

#         for sale_data in sales:
#             product_id = sale_data.get('product_id')
#             quantity = sale_data.get('quantity')

#             # Use get() instead of get_object_or_404 to handle the case where the product is not found
#             product = Product.objects.get(pk=product_id)

#             # Check if there is enough inventory before deducting
#             if quantity > product.inventory_quantity:
#                 return JsonResponse({'error': 'Insufficient inventory for product: {}'.format(product.name)}, status=400)

#             # Deduct the quantity sold from the product inventory
#             product.inventory_quantity -= quantity
#             product.save()

#             # Save the sale in the database
#             Sale.objects.create(product=product, quantity=quantity)

#         return JsonResponse({'message': 'Sales saved successfully'})
#     except json.JSONDecodeError as json_error:
#         return JsonResponse({'error': 'JSON decoding error: {}'.format(json_error)}, status=400)
#     except Product.DoesNotExist:
#         raise Http404('Product not found')  # Return a 404 response with a helpful error message
#     except Exception as e:
#         # Print the exception to the console for debugging
#         print('Exception in save_sale view:', e)
#         return JsonResponse({'error': 'Internal Server Error'}, status=500)


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


def sold_products(request):
    sales = Sale.objects.all().order_by('-id')
    return render(request, 'sales/sold_products.html', {'sales': sales})


def reorder_point_products(request):
    # Retrieve products that are equal to or below the reorder point
    reorder_products = Product.objects.filter(inventory_quantity__lte=F('reorder_point'))

    return render(request, 'reorder_point_products.html', {'reorder_products': reorder_products})


def quick_inventory_adjustment(request):
    products = Product.objects.all()

    if request.method == 'POST':
        num_adjustments = int(request.POST.get('num_adjustments', 0))  # Get number of adjustments submitted

        for i in range(1, num_adjustments + 1):
            selected_product_id = request.POST.get(f'selected_product_{i}')
            adjustment_quantity = request.POST.get(f'adjustment_quantity_{i}')

            try:
                product = Product.objects.get(pk=selected_product_id)
                adjustment_quantity = int(adjustment_quantity)

                if adjustment_quantity != 0:
                    product.inventory_quantity += adjustment_quantity
                    product.save()
                    messages.success(request, f"Inventory for {product.name} adjusted by {adjustment_quantity}")
                else:
                    messages.warning(request, f"No adjustment made for {product.name}")

            except Product.DoesNotExist:
                messages.error(request, f"Product with ID {selected_product_id} not found.")
            except ValueError:
                messages.error(request, "Invalid adjustment quantity.")

        # Redirect to refresh the form after all adjustments are processed
        return redirect('quick_inventory_adjustment')

    return render(request, 'quick_inventory_adjustment.html', {'products': products})


def quick_price_adjustment(request):
    products = Product.objects.all()

    if request.method == 'POST':
        num_adjustments = int(request.POST.get('num_adjustments', 0))

        for i in range(1, num_adjustments + 1):
            selected_product_id = request.POST.get(f'selected_product_{i}')
            price_adjustment = request.POST.get(f'price_adjustment_{i}')
            cost_adjustment = request.POST.get(f'cost_adjustment_{i}')

            try:
                product = Product.objects.get(pk=selected_product_id)
                price_adjustment = Decimal(price_adjustment)
                cost_adjustment = Decimal(cost_adjustment)

                product.standard_price = price_adjustment
                product.current_cost = cost_adjustment
                product.save()
                messages.success(request, f"Price and cost for {product.name} updated to {price_adjustment} and {cost_adjustment} respectively.")

            except Product.DoesNotExist:
                messages.error(request, f"Product with ID {selected_product_id} not found.")
            except ValueError:
                messages.error(request, "Invalid adjustment value.")

        return redirect('quick_price_adjustment')

    return render(request, 'quick_price_adjustment.html', {'products': products})