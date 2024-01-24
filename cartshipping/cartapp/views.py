from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from .models import Order, OrderItem, Product
from decimal import Decimal
from .forms import *
from .generate_code import generate_random_system_code
from .clear_session import *
# Create your views here.
def home(req):
    key = check()
    #clear(key)
    return render(req,'cartapp/home.html',{})

def product_list(request):
    products = Product.objects.all()
    form = ProductForm2()
    return render(request, 'cartapp/product_list.html', {'products': products,
                                                         'form':form})
def product_list2(request):
    products = Product.objects.all()
    form = ProductForm2()
    return render(request, 'cartapp/product_list2.html', {'products': products,
                                                         'form':form})
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect to product list page
    else:
        form = ProductForm()

    return render(request, 'cartapp/add_product.html', {'form': form})

def create_cart(request):
    existing_order = Order.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(minutes=10)).first()
    if existing_order:
        order = existing_order
        print(order)
    else:
        random_code = generate_random_system_code()
        order = Order.objects.create(total_price=Decimal('0.00'), ref_code=random_code)
        request.session['order'] = order.ref_code  # Use ref_code for session
        print(order, 'create cart done')
    return render(request, 'cartapp/view_cart.html', {'order': order})

def delete_cart(request):
    order_id = request.session.get('order')
    pop_order_id = request.session.pop('order', None)
    print('order id',order_id)
    if order_id:
        Order.objects.filter(ref_code=order_id).delete()
        print('deleted cart')
    return redirect('home')

def add_to_cart(request,type):
    if request.method == 'POST':
        
        if type=='type1':
            print('type1')
            product_ids = request.POST.getlist('product_id')
            quantities = request.POST.getlist('quantity')
            print('product_ids',product_ids)
            cart = request.session.get('cart', [])
            order_id = request.session.get('order')
            print('order_id',order_id)
            
            for product_id, quantity in zip(product_ids, quantities):
                print('in loop')
                print('product_id',product_id)
                p = Product.objects.all()
                for i in p:
                    print(i.id)
                product = get_object_or_404(Product, pk=product_id)
                print('fuck')
                quantity = int(quantity)  # Convert quantity to an integer

                # Check if the product is already in the cart
                existing_item = next((item for item in cart if item['id'] == product.id), None)
                print('fuck2')

                if existing_item:
                    print('fuck3')
                    # Update quantity if the product is already in the cart
                    existing_item['quantity'] += quantity
                else:
                    # Add a new item to the cart
                    cart.append({'id': product.id, 'name': product.name, 'price': str(product.price), 'quantity': quantity})
                    print('cart',cart)
                # Update order data in the database
                if not order_id:
                    random_code = generate_random_system_code()
                    order = Order.objects.create(total_price=Decimal('0.00'),ref_code=random_code)
        
                    print('created sussess')
                    request.session['order'] = random_code
                else:
                    print('orderlll')
                    order = get_object_or_404(Order, ref_code=order_id)


                order_item, created = OrderItem.objects.get_or_create(order=order, defaults={'quantity': 0, 'price': product.price})
                order_item.products.add(product)
                order_item.quantity = quantity
                order_item.save()

                order.total_price = (product.price * quantity)
                order.save()

            request.session['cart'] = cart
            print('.................')
            print(cart)
            return redirect('product_list')

        else:
            product_ids = request.POST.getlist('product_id')
            quantities = request.POST.getlist('quantity')
            checked_add = request.POST.getlist('add_to_cart')
            special = request.POST.get('special')
            order_id = request.session.get('order')

            # Filter the selected products based on 'add_to_cart' checkbox
            selected_product_ids = [product_id for product_id, checked in zip(product_ids, checked_add) if checked == 'checked']
            selected_products = Product.objects.filter(id__in=selected_product_ids)

            cart = request.session.get('cart', [])


            total_quantity = sum(int(quantity) for quantity in quantities)
            #print(total_quantity)

            if selected_products:
                with transaction.atomic():

                    if not order_id:
                        random_code = generate_random_system_code()
                        order = Order.objects.create(total_price=Decimal('0.00'),ref_code = random_code)
                        request.session['order'] = order.id
                    else:
                        order = get_object_or_404(Order, ref_code=order_id)


                    order_item = OrderItem.objects.create(order=order, quantity=total_quantity, price=0)
                    order_item.products.add(*selected_products)
                    order_item.price = sum(product.price for product in selected_products)
                    order_item.save()

                    # Update the order's total price
                    order.total_price += order_item.price
                    order.save()

                    # Update the cart with the selected products
                    for product in selected_products:
                        # Check if the product is already in the cart
                        existing_item = next((item for item in cart if item['id'] == product.id), None)

                        if existing_item:
                            # Update quantity if the product is already in the cart
                            existing_item['quantity'] += total_quantity
                        else:
                            # Add a new item to the cart
                            cart.append({'id': product.id, 'name': product.name, 'price': str(product.price), 'quantity': total_quantity})

                request.session['cart'] = cart

            return redirect('view_cart')

def view_cart(request):
    cart = request.session.get('cart', [])
    total_price = sum(Decimal(item['price']) * item.get('quantity', 1) for item in cart)  # Convert back to Decimal, and consider quantity
    items = []

    for item in cart:
        product = Product.objects.get(pk=item['id'])
        items.append({
            'id': item['id'],
            'name': item['name'],
            'price': Decimal(item['price']),
            'quantity': item.get('quantity', 1),
            'subtotal': Decimal(item['price']) * item.get('quantity', 1),
        })

    return render(request, 'cartapp/view_cart.html', {'items': items, 'total_price': total_price})

def delete_from_cart(request, product_id):
    product = get_object_or_404(OrderItem, products=product_id).first() # ปัญหาที่ database เพราะมันเป็น object เดียวกัน ต้องแยก
    print(product , 'delete done')
    product.delete()
    # Retrieve the current cart from the session
    cart = request.session.get('cart', [])

    # Remove the product from the cart if it exists
    cart = [item for item in cart if item['id'] != product_id]

    # Update the session with the modified cart
    request.session['cart'] = cart

    # Redirect back to the cart view
    return redirect('view_cart')

def checkout(request):
    order_id = request.session.get('order')
    if order_id:
        order = Order.objects.get(pk=order_id)
        order_items = OrderItem.objects.filter(order=order)
        return render(request, 'cartapp/checkout.html', {'order': order, 'order_items': order_items})
    else:
        return redirect('product_list')

def order_confirmation(request, order_id=None):
    if order_id is None:
        order_id = request.session.pop('order', None)
    if order_id:
        order = Order.objects.get(pk=order_id)
        order_items = OrderItem.objects.filter(order=order)
        return render(request, 'cartapp/order_confirmation.html', {'order': order, 'order_items': order_items})
    else:
        return redirect('product_list')

def place_order(request):
    order_id = request.session.pop('order', None)
    if order_id:
        # Process the order and update any necessary data (e.g., inventory, user information)

        # Clear the cart session
        request.session.pop('cart', None)

        return redirect('order_confirmation', order_id=order_id)
    else:
        return redirect('product_list')
    
def confirm_order(request, order_id):
    order = Order.objects.get(pk=order_id)

    if request.method == 'POST':
        form = OrderConfirmationForm(request.POST)
        if form.is_valid() and form.cleaned_data['confirm']:
            # Perform order confirmation logic here
            # For example, update order status, send confirmation emails, etc.
            order.confirmed = True
            order.save()
            return redirect('order_history')  # Redirect to a success page
    else:
        form = OrderConfirmationForm()

    return render(request, 'cartapp/confirm_order.html', {'form': form, 'order': order})

def order_history(request):
    user_orders = Order.objects.all().order_by('-created_at')
    return render(request, 'cartapp/order_history.html', {'user_orders': user_orders})

