from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Davitokens, DaviPayment, Wallet, DaviConvertion
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime
import stripe

def home(request):
    return render(request, 'index.html')

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        location = request.POST.get('location')

        if User.objects.filter(email=email).exists():
            return render(request, 'register_user.html', {'error': 'email id is already exists'})

        try:
            User.objects.create_user(email=email, password=password, username=username, mobile=mobile, location=location)
            return redirect('login')
        except Exception as e:
            pass
    return render(request, 'register_user.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

            if check_password(password, user.password):
                login(request, user)

                if user.is_superuser:
                    print('user is superuser')
                    return redirect('admin_index')
                elif user.is_approved == True:
                    return redirect('user_index')
                else:
                    return render(request, 'login.html', {'error': 'The admin is not approved you'})
            else:
                print('invalid email or password')
                return render(request, 'login.html', {'error': 'Invalid email or password'})
        except User.DoesNotExist:
            print('user dows not exist')
            return render(request, 'login.html', {'error': 'user does not exist'})
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('home')

def admin_index(request):
    return render(request, 'admin_index.html')

def manage_users(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        if action == 'approve':
            user = User.objects.get(id=user_id)
            user.is_approved = True
            user.save()
            return redirect('manage_users')
        elif action == 'remove':
            user = User.objects.get(id=user_id)
            user.delete()
            return redirect('manage_users')
        
    users = User.objects.filter(is_approved=False, is_superuser=False)
    approved_users = User.objects.filter(is_superuser=False, is_approved=True)
    return render(request, 'manage_users.html', {'users': users, 'approved_users': approved_users})

def user_index(request):
    return render(request, 'user_index.html')

def admin_davis(request):
    davitokens = Davitokens.objects.all()
    if request.method == 'POST':
        image = request.FILES.get('image')
        amount = request.POST.get('amount')
        davitokenss = request.POST.get('davitokens') 

        Davitokens.objects.create(amount=amount, 
                                  image=image,
                                  davitokens=davitokenss,
                                  released=datetime.today())
        return redirect('admin_davis')
    
    return render(request, 'admin_davis.html', {'davitokens': davitokens})

def delete_token(request, token_id):
    token = Davitokens.objects.get(id=token_id)
    token.delete()
    return redirect('admin_davis')

def purchase_davis(request):
    davitokens = Davitokens.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        token_id = request.POST.get('token_id')

        if action == 'buy':
            return redirect('davi_payment', token_id=token_id)

    return render(request, 'purchase_davis.html', {'davitokens': davitokens})

def davi_payment(request, token_id):
    token = get_object_or_404(Davitokens, id=token_id)
    stripe.api_key = 'sk_test_51Qq5lDSIlf9ctLPP4As9xtAonS2qFRneLHoZ750gjJ6u57Gp6fRrOip73Y7mr2qX1qZfNo3qE3xRiJUMQj7wwz5g00nEKvfKko'

    # Check if the request includes a Stripe session ID to verify payment status
    session_id = request.GET.get('session_id')

    if session_id:
        # Retrieve the session details from Stripe
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            print(session.payment_status)

            if session.payment_status == 'paid':
                # Payment succeeded, perform actions
                user = request.user
                amount = token.amount
                davitokens = token.davitokens
                date = datetime.today()

                # Save payment details
                DaviPayment.objects.create(
                    user=user,
                    amount=amount,
                    davitokens=davitokens,
                    transaction_id=session['id'],
                    date=date,
                )

                # Update user's Davitokens
                user_davi = User.objects.get(email=user.email)
                user_davi.davitokens += davitokens
                user_davi.save()

                return render(request, 'success.html', {'message': 'Payment successful!'})

            else:
                # Payment failed
                return render(request, 'error.html', {'error': 'Payment not completed.'})

        except stripe.error.StripeError as e:
            print(f"Stripe Error: {e}")
            return render(request, 'error.html', {'error': 'An error occurred while verifying payment.'})

    else:
        # Create a Stripe Checkout Session
        try:
            success_url = f"{request.scheme}://{request.get_host()}{request.path}?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{request.scheme}://{request.get_host()}/cancel"

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': 'Davitokens Purchase',
                        },
                        'unit_amount': token.amount * 100,  # Amount in paise
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                billing_address_collection='required',
            )

            # Redirect to Stripe Checkout
            return redirect(session.url)

        except Exception as e:
            print(f"Stripe Error: {e}")
            return render(request, 'error.html', {'error': 'Unable to create a payment session.'})




def success(request):
    return render(request, 'success.html')

def davipayment_record(request):
    records = DaviPayment.objects.all()
    revenue = sum(transaction.amount for transaction in DaviPayment.objects.all())
    return render(request, 'davipayment_record.html', {'records': records, 'revenue': revenue})

def simon_game(request):
    email = request.user.email
    user = get_object_or_404(User, email=email)
    if user.davitokens >= 10:
        user.davitokens = user.davitokens - 10
        user.save()
        return render(request, 'simon_game.html')
    else:
        return render(request, 'games.html', {'error': 'Not Enough Davitokens... Buy Some ...!!!'})

def games(request):
    return render(request, 'games.html')

def user_payment(request):
    records = DaviPayment.objects.filter(user=request.user)
    return render(request, 'user_payment.html', {'records': records})

def simon_win(request):
    email = request.user.email
    user = get_object_or_404(User, email=email)
    user.davitokens = user.davitokens + 20
    user.save()
    return redirect('games')

def mole_game(request):
    email = request.user.email
    user = get_object_or_404(User, email=email)
    if user.davitokens >= 10:
        user.davitokens = user.davitokens - 10
        user.save()
        return render(request, 'mole.html')
    else:
        return render(request, 'games.html', {'error': 'Not Enough Davitokens... Buy Some ...!!!'})
    
def mole_win(request):
    email = request.user.email
    user = get_object_or_404(User, email=email)
    user.davitokens = user.davitokens + 20
    user.save()
    return redirect('games')

def davi_conversion(request):
    conversions = DaviConvertion.objects.all()
    if request.method == 'POST':
        davitokens = request.POST.get('davitokens')
        amount = request.POST.get('amount')
        DaviConvertion.objects.create(davitokens=davitokens, amount=amount)
    return render(request, 'davi_conversion.html', {'conversions': conversions})

def user_wallet(request):
    conversions = DaviConvertion.objects.all()
    if request.method == 'POST':
        davitokens = int(request.POST.get('davitokens'))
        ifsc_code = request.POST.get('ifsc')
        account_number = request.POST.get('account_number')

        email = request.user.email
        user = get_object_or_404(User, email=email)

        if user.davitokens < davitokens:
            return render(request, 'user_wallet.html', {'error': 'Not Enogh Davitokens', 'conversions': conversions})

        conv = get_object_or_404(DaviConvertion, davitokens=davitokens)
        amount = conv.amount
        
        try:
            Wallet.objects.create(user=request.user,
                              amount=amount,
                              davitokens=davitokens, 
                              account_number=account_number, 
                              ifsc_code=ifsc_code,
                              date=datetime.today())
            user.davitokens = user.davitokens - davitokens
            user.wallet_amount = user.wallet_amount + amount
            user.save()
            return redirect('success')
        except Exception as e:
            print(e)
    return render(request, 'user_wallet.html', {'conversions': conversions})

def delete_conversion(request, conv_id):
    conversion = get_object_or_404(DaviConvertion, id=conv_id)
    conversion.delete()
    return redirect('davi_conversion')


def wallet_transfer(request):
    records = Wallet.objects.all()
    return render(request, 'wallet_transfer.html', {'records': records})

def cancel(request):
    return render(request, 'cancel.html')

