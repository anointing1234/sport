from django.shortcuts import render
from django.shortcuts import render,get_object_or_404, redirect
from django.urls import reverse
from .forms import RegistrationForm, UsersBankDetailsForm,LoginForm,PasswordSendResetForm,PasswordResetForm
from django.http import JsonResponse
import requests 
from decimal import Decimal, InvalidOperation
import logging
import json
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate,logout as auth_logout,login as auth_login
from .models import AdminBankAccount,DepositRequest, UserBalance, PurchasePackage,Package,BetHistory,PasswordResetCode,Account,ReferralBonus,UsersReferralPercentage,WithdrawalRequest
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal 
from django.views import View
from django.views.decorators.csrf import csrf_exempt


User = get_user_model()

# Create your views here.
def login(request):
    login_form = LoginForm()
    return render(request,'Auth/login.html',{
        'login':login_form
    })




def signup(request):
    user_form = RegistrationForm()
    bank_form = UsersBankDetailsForm()
    
    return render(request,'Auth/signup.html',{
        'user_form': user_form,
        'bank_form': bank_form,
    })
    
  
User = get_user_model()

def your_signup_view(request):
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST)
        bank_form = UsersBankDetailsForm(request.POST)
        
        if user_form.is_valid() and bank_form.is_valid():
            # Save the user data
            user = user_form.save()
            bank_details = bank_form.save(commit=False)
            bank_details.user = user  # Associate bank details with the user
            bank_details.save()

            # Handle the referral code
            referral_code = user_form.cleaned_data.get('referral_code')  # Make sure this matches your form field name
            
            if referral_code:
                try:
                    # Fetch the user with the referral code
                    referrer = User.objects.get(referral_code=referral_code)
                    # Set the referral field for the referrer to the new user
                    referrer.referral = user  # Update the referral field
                    referrer.save()  # Save the referrer to persist the change
                except User.DoesNotExist:
                    # Optionally handle the case where the referral code is invalid
                    pass  # Log this or notify the user if needed

            return JsonResponse({'success': True, 'message': 'Registration successful!', 'redirect_url': '/accounts/login'})  # Redirect URL

        else:
            # Collect all form errors
            error_messages = []
            if user_form.errors:
                for field, errors in user_form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field.capitalize()}: {error}")

            if bank_form.errors:
                for field, errors in bank_form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field.capitalize()}: {error}")

            # Join all error messages into a single string
            error_message = "\n".join(error_messages)

            return JsonResponse({'success': False, 'message': error_message})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful!',
                'redirect_url': '/'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid phone number or password.'
            })
    else:
        form = LoginForm()
    return render(request, 'Auth/login.html', {'login': form})




def logout_view(request):
    auth_logout(request)
    login_form = LoginForm()
    return render(request,'Auth/login.html',
    { 
     'login':login_form                                         
    })
    
    

def get_admin_bank_account(request):
    try:
        # Fetch the first bank account entry
        account = AdminBankAccount.objects.first()
        
        if account:
            data = {
                'success': True,
                'account': {
                    'account_holder_name': account.account_holder_name,
                    'bank_name': account.bank_name,
                    'account_number': account.account_number,
                }
            }
        else:
            data = {'success': False, 'message': 'No bank account found.'}
        
    except Exception as e:
        data = {'success': False, 'message': str(e)}
    
    return JsonResponse(data)    






def process_deposit(request):
    if request.method == "POST":
        try:
            amount = float(request.POST.get("depositAmount"))
            method = request.POST.get("depositMethod")

            # Minimum deposit check
            if amount < 16500:
                return JsonResponse({
                    "success": False, 
                    "message": "Minimum deposit is 16,500."
                })

            # Save the deposit request
            DepositRequest.objects.create(
                user=request.user,
                amount=amount,
                method=method,
                status="Pending"
            )

            return JsonResponse({
                "success": True,
                "message": "Deposit request sent , account will be credited shortly!"
            })

        except ValueError:
            return JsonResponse({
                "success": False,
                "message": "Invalid deposit amount."
            })

    return JsonResponse({
        "success": False,
        "message": "Invalid request method."
    })



    
def confirm_deposit(request):
    deposit_id = request.GET.get('deposit_id')
    deposit = get_object_or_404(DepositRequest, pk=deposit_id)  # Fetch the deposit request

    if deposit.status == 'Pending':
        deposit.status = 'Completed'
        deposit.save()

        # Credit the user's main balance in UserBalance
        user_balance, created = UserBalance.objects.get_or_create(user=deposit.user)
        user_balance.main_balance += deposit.amount
        user_balance.save()

        # Check if the user has a referrer
        referrer = deposit.user.referred_by
        if referrer:
            # Check if a bonus has already been awarded for this referrer and referred user
            existing_bonus = ReferralBonus.objects.filter(referrer=referrer, referred_user=deposit.user).exists()

            if not existing_bonus:
                # Get the referral percentage
                referral_percentage_obj = UsersReferralPercentage.objects.first()
                if referral_percentage_obj:
                    referral_percentage = Decimal(referral_percentage_obj.percentage) / Decimal(100)
                    referral_bonus = deposit.amount * referral_percentage

                    # Credit the referral bonus to the referrer's main balance
                    referrer_balance, created = UserBalance.objects.get_or_create(user=referrer)
                    referrer_balance.main_balance += referral_bonus
                    referrer_balance.save()

                    # Record the referral bonus
                    ReferralBonus.objects.create(
                        referrer=referrer,
                        referred_user=deposit.user,
                        bonus_amount=referral_bonus
                    )

                    messages.success(
                        request,
                        f"Deposit of {deposit.amount} credited to {deposit.user.username}'s main balance. "
                        f"Referral bonus of {referral_bonus} credited to referrer {referrer.username}."
                    )
                else:
                    messages.warning(request, "Referral percentage not set.")
            else:
                messages.info(request, "Deposit was successfull Referral bonus has already been awarded for this referral.")

    else:
        messages.warning(request, "This deposit has already been processed.")

    return redirect('admin:accounts_depositrequest_changelist')


def decline_deposit(request):
    deposit_id = request.GET.get('deposit_id')
    deposit = get_object_or_404(DepositRequest, pk=deposit_id)
    
    if deposit.status == 'Pending':
        deposit.status = 'Failed'
        deposit.save()
        messages.error(request, f"Deposit of {deposit.amount} for user {deposit.user.username} has been declined.")
    else:
        messages.warning(request, "This deposit has already been processed.")

    return redirect('admin:accounts_depositrequest_changelist')

def confirm_withdrawal(request):
    withdraw_id = request.GET.get('withdraw_id')  # Get the ID from the query parameters
    if withdraw_id:
        withdraw_request = get_object_or_404(WithdrawalRequest, id=withdraw_id)
        withdraw_request.status = 'Completed'  # Update the status to confirmed
        withdraw_request.save()

        # Redirect back to admin with a success message (you can implement flash messages if needed)
        return redirect('/admin/accounts/withdrawalrequest/')  # Adjust the URL according to your admin panel structure

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

def decline_withdrawal(request):
    withdraw_id = request.GET.get('withdraw_id')  # Get the ID from the query parameters
    if withdraw_id:
        withdraw_request = get_object_or_404(WithdrawalRequest, id=withdraw_id)
        withdraw_request.status = 'Failed'  # Update the status to declined
        withdraw_request.save()

        # Redirect back to admin with a success message (you can implement flash messages if needed)
        return redirect('/admin/accounts/withdrawalrequest/')  # Adjust the URL according to your admin panel structure

    return JsonResponse({'success': False, 'message': 'Invalid request.'})




def purchase_package(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        package_name = data.get('name')
        amount = Decimal(data.get('price'))  # Convert to Decimal
        daily_interest = Decimal(data.get('daily_interest'))

        # Fetch the package object
        package = get_object_or_404(Package, name=package_name)

        # Check user's balance
        user_balance = UserBalance.objects.get(user=request.user)
        
        if user_balance.main_balance >= amount:
            # Deduct the amount from the main balance
            user_balance.main_balance -= amount
            user_balance.save()

            # Try to find an existing PurchasePackage for the user
            try:
                purchase_package = PurchasePackage.objects.get(user=request.user)
                # Update the existing PurchasePackage
                purchase_package.name = package_name
                purchase_package.amount = amount
                purchase_package.daily_profit = daily_interest
                purchase_package.weekly_withdrawal = package.withdrawal_frequency
                purchase_package.save()
                package_updated = True
            except PurchasePackage.DoesNotExist:
                # If no package exists, create a new PurchasePackage
                purchase_package = PurchasePackage(
                    user=request.user,
                    name=package_name,
                    amount=amount,
                    daily_profit=daily_interest,
                    weekly_withdrawal=package.withdrawal_frequency
                )
                purchase_package.save()
                package_updated = False

            # Update UserBalance with purchased package details
            user_balance.purchased_package_name = package_name
            user_balance.purchased_package = amount
            user_balance.save()

            message = 'Package updated successfully!' if package_updated else 'Package purchased successfully!'
            return JsonResponse({'success': True, 'message': message})
        else:
            return JsonResponse({'success': False, 'message': 'Insufficient balance for this purchase.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})



logger = logging.getLogger(__name__)


import json
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.utils import timezone
import logging

# Set up logging
logger = logging.getLogger(__name__)

def place_bet(request):
    if request.method == 'POST':
        user = request.user
        try:
            # Load and log the received JSON data
            bet_details = json.loads(request.body)
            logger.debug(f"Received bet details: {bet_details}")

            match = bet_details.get('match')
            date = bet_details.get('date')  # Match date
            time = bet_details.get('time')  # Match time
            fixed_score = bet_details.get('fixed_score')

            # Validate and convert profit_percentage
            try:
                profit_percentage = Decimal(bet_details.get('profit_percentage'))
            except (ValueError, InvalidOperation) as e:
                logger.error(f"Invalid profit percentage: {e}")
                return JsonResponse({'error': 'Invalid profit percentage provided.'}, status=400)

            # Check the number of bets placed today
            today = timezone.now().date()
            bet_count = BetHistory.objects.filter(user=user, placed_at__date=today).count()

            if bet_count >= 3:
                logger.warning(f"User {user.id} exceeded daily bet limit.")
                return JsonResponse({'error': 'Betting exceeded: You can only bet 3 times a day.'}, status=400)

            try:
                # Check if user has a purchased package
                user_balance = UserBalance.objects.get(user=user)
                purchased_package = PurchasePackage.objects.get(name=user_balance.purchased_package_name)

                # Convert purchased_package.amount to Decimal
                package_amount = Decimal(purchased_package.amount)

                # Calculate profit based on the purchased package and profit percentage
                profit = (package_amount * profit_percentage) / 100

                # Update user's main balance
                user_balance.main_balance += profit
                user_balance.total_profits += profit
                user_balance.save()

                # Create a new BetHistory entry
                BetHistory.objects.create(
                    user=user,
                    match=match,
                    date=date,
                    time=time,
                    fixed_score=fixed_score,
                    profit_percentage=profit_percentage,
                    bet_amount=profit,
                )
                formatted_profit = f"{profit:,.2f}"
                return JsonResponse({'message': 'Bet won successfully!', 'profit': formatted_profit}, status=200)

            except PurchasePackage.DoesNotExist:
                logger.error(f"PurchasePackage not found for user {user.id}.")
                return JsonResponse({'error': 'Please purchase a package before placing a bet.'}, status=400)
            except UserBalance.DoesNotExist:
                logger.error(f"UserBalance not found for user {user.id}.")
                return JsonResponse({'error': 'User balance not found.'}, status=400)

        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {e}")
            return JsonResponse({'error': 'Invalid JSON provided.'}, status=400)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    logger.warning("Invalid request method for place_bet endpoint.")
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def check_user_package(request):
    if request.user.is_authenticated:
        has_package = PurchasePackage.objects.filter(user=request.user).exists()
        return JsonResponse({'has_package': has_package})
    return JsonResponse({'has_package': False})



def send_pass_msg(request):
    form = PasswordSendResetForm()
    return render(request,'Auth/send_pass_msg.html',{'form':form})



def send_password_reset_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No user with this email address.'})

        # Generate a random reset code
        reset_code = get_random_string(length=6, allowed_chars='0123456789')
        
        # Save the reset code to the database
        PasswordResetCode.objects.create(user=user, code=reset_code)

        # Send the reset code via email
        subject = 'Your Password Reset Code'
        message = f'Your password reset code is: {reset_code}'
        from_email = settings.DEFAULT_FROM_EMAIL

        try:
            send_mail(subject, message, from_email, [email])
            return JsonResponse({'success': True, 'message': 'A password reset code has been sent to your email.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Failed to send email. Please try again later.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    form = PasswordResetForm()
    return render(request,'Auth/send_pass_msg.html',{'form':form})



def Passwordresetpage(request):
    form = PasswordResetForm()
    return render(request, 'Auth/reset_pass.html', {'form': form})





def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        
        if form.is_valid():
            phone = form.cleaned_data['phone']
            reset_code = form.cleaned_data['reset_code']
            new_password = form.cleaned_data['new_password']

            try:
                # Fetch the user by phone number
                user = Account.objects.get(phone=phone)

                # Verify the reset code
                if not verify_reset_code(user, reset_code):
                    return JsonResponse({'success': False, 'message': 'Invalid reset code.'})

                # Update the user's password
                user.set_password(new_password)
                user.save()

                # Optionally, delete the reset code after successful reset
                PasswordResetCode.objects.filter(user=user, code=reset_code).delete()

                return JsonResponse({'success': True, 'message': 'Your password has been reset successfully.'})

            except Account.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Phone number not found.'})
        
        # Handle form errors
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({'success': False, 'message': 'Form is invalid.', 'errors': errors})

    else:
        form = PasswordResetForm()
        return render(request, 'reset_pass.html', {'form': form})

def verify_reset_code(user, code):
    try:
        reset_code_entry = PasswordResetCode.objects.get(user=user, code=code)
        # Optionally, check if the reset code is still valid (e.g., check the created_at timestamp)
        return True
    except PasswordResetCode.DoesNotExist:
        return False
    
    





def withdraw(request):
    if request.method == 'POST':
        withdraw_amount = Decimal(request.POST.get('withdrawAmount'))  # Use Decimal for the amount
        withdraw_method = request.POST.get('withdrawMethod')

        # Get the user's balance
        user_balance = UserBalance.objects.get(user=request.user)  # Fetch the user's balance
        
        # Get the start of the current week (assuming week starts on Monday)
        start_of_week = timezone.now() - timedelta(days=timezone.now().weekday())

        # Check if the user has made a withdrawal request this week
        this_week_request = WithdrawalRequest.objects.filter(
            user=request.user, 
            date__gte=start_of_week
        ).exists()

        if this_week_request:
            return JsonResponse({
                'success': False,
                'message': 'You can only make one withdrawal request per week.'
            })

        # Check if there are sufficient funds
        if user_balance.main_balance >= withdraw_amount:
            # Deduct the amount from the user's balance
            user_balance.main_balance -= withdraw_amount
            user_balance.save()

            # Create a new withdrawal request
            WithdrawalRequest.objects.create(
                user=request.user,
                amount=withdraw_amount,
                method=withdraw_method,
                status='Pending'  # Default status for new requests
            )

            # Success response
            return JsonResponse({
                'success': True,
                'message': f'Withdrawal request for {withdraw_amount} via {withdraw_method} has been submitted successfully!'
            })
        else:
            # Insufficient balance response
            return JsonResponse({
                'success': False,
                'message': 'Insufficient balance for this withdrawal request!'
            })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })    
    
 
class UpdateUserDetailsView(View):

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        
        if 'fullname' in data:
            request.user.fullname = data['fullname']  # Update fullname
            request.user.save()
            return JsonResponse({'success': True})

        if 'username' in data:
            request.user.username = data['username']  # Update username
            request.user.save()
            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'message': 'Invalid request.'})    
    
def custom_404_view(request, exception):
    return render(request, 'home/404.html', status=404)

def custom_500_view(request):
    return render(request, 'home/500.html', status=500)