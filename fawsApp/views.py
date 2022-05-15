
from django.views.decorators.csrf import csrf_exempt
from django.http import request
from django.shortcuts import render,redirect
from .models import *
from django.core.mail import send_mail
from random import randint
from django.conf import settings
from django.db.utils import *
from .paytm import generate_checksum, verify_checksum
import os, re, requests



# Create your views here.
# app_info
app_info = {
    'app_title': 'Seeds farming',
    'app_name': 'Farming Assistant web service',
    'msg_data': {'name': '', 'msg': '', 'type':'success', 'display': ''},
}    

def console(err):
    print(err)
    print('Type of error: ', type(err))
    print(err.args)


# check internet connection
def isConnected():
    try:
        url = requests.get('http://google.com')
        status  = url.status_code
        if status:
            return True
    except Exception as err:
        app_info['msg_data']['name'] = 'Internet Not Available'
        app_info['msg_data']['msg'] = 'Check your internet connection.'
        return False

# Home page        
def index(request):
    return render(request, 'index.html', app_info)

# about page
def about_page(request):
    return render(request,'app/about.html',app_info)

# contact page
def contact_page(request):
    return render(request,'app/contact.html',app_info)
# contact page
def saved_page(request):
    return render(request,'app/ex-deals.html',app_info)

def order_page(request):
    load_cart(request)
    return render(request,'app/order-details.html', app_info)   

def checkout_page(request):
    return render(request,'app/checkout.html',app_info)   

def shop_page(request):
    load_all_product()
    return render(request,'app/shop-now.html',app_info)


# profile page
def profile_page(request):
    profile_data(request)   
    return render(request,'app/profile.html', app_info)






###################################################
###.....   MAIN PAGE FUNCTIONALITY    ........#####
################################################### 

# send otp on mail
def send_otp(request, otp_for='reg'):
    app_info['verify_for'] = otp_for

    email_to_list = [request.session['email'],]
    subject = 'OTP for Forgot Password'
    otp = randint(1000,9999)
    print('OTP is: ', otp)
    request.session['otp'] = otp
    message = f"your one time otp for Register Farming Assistant Web Service is: {otp}"
    email_from = settings.EMAIL_HOST_USER

    try:
        if isConnected():
            send_mail(subject, message, email_from, email_to_list)
            return True
        return False
    except settings.EMAIL_AUTH_ERROR as err:
        link = '((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)'
        get_link = re.findall(link, err.args[1].decode('utf8'))[0][0]
        print('Email Error: ', get_link)
        
        app_info['msg_data']['name'] = 'Auth Error'
        app_info['msg_data']['msg'] = f'Username and password not accepted.'
        app_info['msg_data']['help_link'] = get_link
        app_info['msg_data']['type'] = 'success'
        app_info['msg_data']['display'] = 'show'
        return False

# otp page
def otp_page(request):
    print('Verify for: ', app_info['verify_for'])
    return render(request,'app/otp_page.html', app_info)

# otp verify functionality
def verify_otp(request, verify_for='reg'):
    if request.method == 'POST':
        if int(request.POST['otp']) == request.session['otp']:
            master = Master.objects.get(Email=request.session['email'])
            
            if verify_for == 'rec':
                master.Password = request.POST['Password']
                app_info['msg_data']['name'] = 'Password Changed'
                app_info['msg_data']['msg'] = 'Congratulations!! Your password has successfully changed.'
            else:
                master.IsActive = True
                if master.Role.Role == 'seller':
                    Seller.objects.create(Master=master)
                elif master.Role.Role == 'farmer':
                    Farmer.objects.create(Master=master)
               
                
                app_info['msg_data']['name'] = 'Verified'
                app_info['msg_data']['msg'] = 'Congratulations!! Your email has successfully verified.'

            master.save()

            app_info['msg_data']['type'] = 'success'
            app_info['msg_data']['display'] = 'show'

            del request.session['otp']
            del request.session['email']
            
            return redirect(login_page)
        else:
            app_info['msg_data']['name'] = 'Invalid OTP'
            app_info['msg_data']['msg'] = "OTP does not matched. Please enter correct otp."
            app_info['msg_data']['type'] = 'warning'
            app_info['msg_data']['display'] = 'show'
            return redirect(otp_page)
    else:
        app_info['msg_data']['name'] = 'Invalid Request'
        app_info['msg_data']['msg'] = "Something went wrong. Please try again leter."
        app_info['msg_data']['type'] = 'warning'
        app_info['msg_data']['display'] = 'show'
        return redirect(otp_page)
    pass
      
# load all roles
def load_role():
    all_role = Role.objects.all()
    return all_role

app_info['all_roles'] = load_role()

# register page
def register_page(request):
    print(app_info['msg_data'])
    return render(request, 'app/register.html', app_info)

# register functionality
def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        role_id = int(request.POST['role'])
        password = request.POST['password']
        print(request.POST)
        try:
            role = Role.objects.get(id=role_id)
            Master.objects.create(Email=email,Role=role,Password=password)

            request.session['email'] = email
            
            on_success = send_otp(request)

            print('success: ', on_success)
            
            if on_success:
                app_info['msg_data']['name'] = 'OTP Sent'
                app_info['msg_data']['msg'] = f'One-Time Password has sent to {email}.'
                app_info['msg_data']['type'] = 'success'
                app_info['msg_data']['display'] = 'show'
                
                return redirect(otp_page)
            else:
                return redirect(profile_page)

        except IntegrityError as err:
            msg = f'Error in register view @ line 174: {err}'
            print(msg)
            console(err) # display error in terminal
            print('unique'.upper() in err.args[0])
            
            if 'unique'.upper() in err.args[0]:
                app_info['msg_data']['name'] = 'Email existed'
                app_info['msg_data']['msg'] = f'{email} is already existed.'

            app_info['msg_data']['type'] = 'danger'
            app_info['msg_data']['display'] = 'show'

            return redirect(register_page)
    else:
        pass

# login page
def login_page(request):
    return render(request, 'app/login.html', app_info)

# login functionality
@csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        master = ''
        try:
            master =  Master.objects.get(Email=email)
            print(password, master.Password)
            role = master.Role
            print(role.Role)
            app_info['user_role'] = role
            if master.Password != password:
                raise Exception('password does not matched.')
            else:
                request.session['email'] = email

            profile_data(request)
            return redirect(index)
        except Master.DoesNotExist as err:
            console(err) # display error in terminal
            print('not exist' in err.args[0])
            
            if 'not exist' in err.args[0]:
                app_info['msg_data']['name'] = 'Not Registered'
                app_info['msg_data']['msg'] = f'{email} is not registered.'

            app_info['msg_data']['type'] = 'warning'
            app_info['msg_data']['display'] = 'show'
            return redirect(login_page)
        except Exception as err:
            console(err) # display error in terminal
            if master.Password != password:
                app_info['msg_data']['name'] = 'Wrong Password'
                app_info['msg_data']['msg'] = f'Your {err.args[0]}'

                app_info['msg_data']['type'] = 'warning'
                app_info['msg_data']['display'] = 'show'
            return redirect(login_page)
    else:
        pass




# forgot password page
def forgot_pass_page(request):
    return render(request,'app/forgot_password.html',app_info)

# forgot password functionality
@csrf_exempt
def forgot_pass(request):
    if request.method == 'POST':
        email_to = request.session['email'] = request.POST['email']

        on_success = send_otp(request, otp_for='rec')

        if on_success:
            app_info['msg_data']['name'] = 'OTP Sent'
            app_info['msg_data']['msg'] = f'One-Time Password has sent to {email_to} for verification.'
            app_info['msg_data']['type'] = 'success'
            app_info['msg_data']['display'] = 'show'

            return redirect(otp_page)
        else:
            return redirect(login_page)
    else:
        pass


# get profile data

def profile_data(request):
    print(request.session['email'])
    if 'email' in request.session:
        try:
            master =  Master.objects.get(Email=request.session['email'])
            user_role = master.Role.Role

            app_info['user_role'] = user_role
            # print(app_info['user_role'])
            if user_role == 'farmer':
                farmer = Farmer.objects.get(Master=master) 
                app_info['profile_data'] = farmer
                load_all_product()
                # print('products ', app_info['all_products'])

            elif user_role == 'seller':
                seller = Seller.objects.get(Master=master)
                app_info['profile_data'] = seller
                load_seller_product(request)
                

            if app_info['profile_data'].Image.url.split('/')[-1] != 'default.png':
                app_info['has_profile_image'] = True
            else:
                app_info['has_profile_image'] = False
        except Exception as err:
            print('Error in profile_data method @ line 189', err)

def upload_profile_pic(request):
    master = Master.objects.get(Email=request.session['email'])
    user = ''
    user_role = master.Role.Role

    if user_role == 'farmer':
        user = Farmer.objects.get(Master=master)
    elif user_role == 'seller':
        user = Seller.objects.get(Master=master)

    user_image_path = os.path.join(settings.MEDIA_ROOT, f'{user_role}\\')
        
    if 'user_image' in request.FILES:
        user_image = request.FILES['user_image']
        print('--------------------------------',user_image)
        
        # renaming the uploaded image according to user id
        user_name = ''

        if user.FullName:
            user_name = '_'.join(user.FullName.split())
        
        user_image.name = f'{user_role}_{user_name.lower()}.{user_image.name.split(".")[-1]}'

        print('image path: ', user.Image)
        # print('user path from model ', str(user.Image).split('/')[1])
        
        if user.Image != 'default.png':
            if str(user.Image).split('/')[1] not in os.listdir(user_image_path):
                print('folder created')
                os.mkdir(f'{user_image_path}\\{str(user.Image).split("/")[1]}')
            else:
                user_image_path = os.path.join(settings.MEDIA_ROOT, f'{user_image_path}\\{str(user.Image).split("/")[1]}\\')

        for fname in os.listdir(user_image_path):
            print('files: ', fname)
            if fname == user_image.name:
                f = os.path.join(user_image_path, user_image.name)
                print(f)
                os.remove(f)
                print(f"file {f} is deleted successfully")


        user.Image = user_image
    user.save()
    return redirect(profile_page)

 # profile update
def profile_update(request):
    master = Master.objects.get(Email=request.session['email'])
    user = ''
    user_role = master.Role.Role
    if user_role == 'farmer':
        user = Farmer.objects.get(Master=master)
    elif user_role == 'seller':
        user = Seller.objects.get(Master=master)
       
    
    user.FullName = request.POST['fullname']
    user.Mobile = request.POST['mobile']
    user.Gender = request.POST['gender']
    user.Country = request.POST['country']
    user.State = request.POST['state']
    user.City = request.POST['city']
    user.Pincode = request.POST['pincode']
    user.Address = request.POST['address']

    user.save()

    
    
    app_info['msg_data']['name'] = 'Profile Updated'
    app_info['msg_data']['msg'] = f'Your profile has been successfully updated.'
    app_info['msg_data']['type'] = 'success'
    app_info['msg_data']['display'] = 'show'
    return redirect(profile_page)

# change password
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']

        master = Master.objects.get(Email=request.session['email'])

        if current_password == master.Password:
            master.Password = new_password
            master.save()
            app_info['msg_data']['name'] = 'Password Changed'
            app_info['msg_data']['msg'] = f'Your password changed successfully done.'
            app_info['msg_data']['type'] = 'success'
        else:
            app_info['msg_data']['name'] = 'Not Matched'
            app_info['msg_data']['msg'] = f'Please enter your currect current password.'
            app_info['msg_data']['type'] = 'warning'
        app_info['msg_data']['display'] = 'show'
        return redirect(profile_page)
    else:
        pass

app_info['all_categories'] = []
for category in Product_categories_choices:
    app_info['all_categories'].append({'short_tag': category[0], 'tag': category[1]})

app_info['all_unit'] = []
for unit in product_unit_choices:
    app_info['all_unit'].append({'short_tag': unit[0], 'tag': unit[1]})    

## Load product  card in seller page
def load_seller_product(request):
    master = Master.objects.get(Email=request.session['email'])
    seller = Seller.objects.get(Master=master)
    # print('categories data ', Product_categories_choices)
    app_info['seller_products'] = Product.objects.filter(Seller=seller)[::-1]

## load all product farmer account   
def load_all_product():
    app_info['all_products'] = Product.objects.all()

## Add product in seller page
def products(request):
    categories = request.POST['categories']
    name = request.POST['name']
    unit = request.POST['unit']
    price = request.POST['price']
    
    is_active = False
    if 'isproductsActive' in request.POST:
        is_active = True

    master = Master.objects.get(Email=request.session['email'])
    seller = Seller.objects.get(Master=master)

    products = Product.objects.create(
        Seller = seller,
        Categories = categories,
        Name = name,
        Unit = unit,
        Price = price
       
    )
    if 'product_image' in request.FILES:
        products.Image = request.FILES['product_image']
        products.save()

    app_info['msg_data']['name'] = 'product Added'
    app_info['msg_data']['msg'] = f'product  added successfully.'
    app_info['msg_data']['type'] = 'success'
    app_info['msg_data']['display'] = 'show'
    return redirect(profile_page)

## Delete product from profile page
def delete_product(request, pk):
    Product.objects.get(pk=pk).delete()
    app_info['msg_data']['name'] = 'product Delete to Cart'
    app_info['msg_data']['msg'] = f'product  deleted successfully.'
    app_info['msg_data']['type'] = 'success'
    app_info['msg_data']['display'] = 'show'
    return redirect(profile_page)    

# load cart
def load_cart(request):
    master = Master.objects.get(Email=request.session['email'])
    farmer = Farmer.objects.get(Master=master)
    cart = Cart.objects.filter(Farmer=farmer)[::-1]
    total_cart_amount = 0
    for c in cart:
        total_cart_amount += c.Total
        print('total_cart', c.Total)
    
    print(type(total_cart_amount), (total_cart_amount / 100) * 18)

    tax = (total_cart_amount / 100) * 18
    final_amount = total_cart_amount + tax

    app_info['cart_data'] = {'cart': cart, 'tax':tax, 'final_amount': final_amount, 'total_cart_amount': total_cart_amount, 'total_cart': len(cart)}

def add_to_cart(request, pk):
    
    master = Master.objects.get(Email=request.session['email'])
    farmer = Farmer.objects.get(Master=master)

    product = Product.objects.get(pk=pk)
    qty = 1
    total = product.Price * qty
    

    Cart.objects.create(
        Farmer = farmer,
        Product = product,
        Quantity = qty,
        Total = total
    )
    load_cart(request)
    app_info['msg_data']['name'] = 'product AddToCart'
    app_info['msg_data']['msg'] = f'product  addToCart successfully.'
    app_info['msg_data']['type'] = 'success'
    app_info['msg_data']['display'] = 'show'
    return redirect(shop_page)



## view cart
def view_cart(request):
    master = Master.objects.get(Email=request.session['email'])
    farmer = Farmer.objects.get(Master=master)
    cart = Cart.objects.filter(Farmer=farmer)[::-1]
    app_info['cart_data'] = {'cart': cart, 'total_cart': len(cart)}

    return redirect(order_page)

def update_cart(request, pk):
    cart = Cart.objects.get(pk=pk)
    cart.Quantity = int(request.POST['qty'])
    print(type(cart.Quantity), cart.Quantity)
    # print(cart.Product.Price)
    cart.Total = cart.Quantity * cart.Product.Price
    cart.save()
    app_info['msg_data']['name'] = 'Quantity UpdateToCart'
    app_info['msg_data']['msg'] = f'Quantity  UpdateToCart successfully.'
    app_info['msg_data']['type'] = 'success'
    app_info['msg_data']['display'] = 'show'
    return redirect(order_page)


## delete cart
def delete_cart(request,pk):
    Cart.objects.get(pk=pk).delete()
    app_info['msg_data']['name'] = 'product Delete To Cart'
    app_info['msg_data']['msg'] = f'product  Delete To Cart successfully.'
    app_info['msg_data']['type'] = 'success'
    app_info['msg_data']['display'] = 'show'
    return redirect(order_page)


## order
def order_details(request):
    master = Master.objects.get(Email=request.session['email'])
    farmer = Farmer.objects.get(Master=master)
    product = Product.objects.get()
    qty = 1
    total = product.Price * qty
    

    Order.objects.create(
        Farmer = farmer,
        Product = product,
        Quantity = qty,
        Total = total
    )


## checkout page
def checkout(request):
    if request.method=="POST":
        shipping_name = request.POST.get('shipping_name', '')
        phone_number = request.POST.get('phone_number', '')
        house_number = request.POST.get('house_number', '')
        floor_number = request.POST.get('floor_number', '')
        country = request.POST.get('country', '')
        state = request.POST.get('state', '')
        city = request.POST.get('city', '')
        area = request.POST.get('area', '')
        address = request.POST.get('address', '')
        pincode = request.POST.grt('pincode', '')


    return render(request,'app/checkout.html')    
        

   
   

###,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,PAYTM PAYMENT VIEW ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,##

## payment views
@csrf_exempt
def initiate_payment(request):
    try:
        amount = float(request.POST['amount'])
        # amount = 10
        print('final_amount', request.POST['amount'], type(request.POST['amount']))
    except Exception as e:
        print(e)
        return render(request, 'app/order-details.html')

    transaction = Transaction.objects.create(made_by=request.session['email'], amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', transaction.made_by),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    print('params ', params)

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'app/redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
            msg = 'Your payment made successfully done.'
        else:
            msg = 'Your payment failed. Please try again later.'
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'app/callback.html', context=received_data)
        #return render(request, 'mycart.html', context=received_data)
        return redirect('index')


# signout
def signout(request):
    if 'email' in request.session:
        del request.session['email']
        app_info['profile_data'] = ''
        app_info['user_role'] = ''
        app_info['msg_data'] = ''
        
    return redirect(index)

