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
from .models import AdminBankAccount,DepositRequest, UserBalance, PurchasePackage,Package,BetHistory,PasswordResetCode,Account,ReferralBonus,UsersReferralPercentage,WithdrawalRequest,WithdrawalTimeAndDate,HotGame,PremierLeagueGame,FootballMatch,Match
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal,InvalidOperation
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from django.core.mail import EmailMultiAlternatives
import pytz
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone
import logging

logger = logging.getLogger(__name__)

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


def check_deposit_status(request):
    try:
        # Parse the request body to get depositId
        data = json.loads(request.body)
        deposit_id = data.get('depositId')

        # Check if depositId is provided
        if not deposit_id:
            return JsonResponse({
                'success': False,
                'message': 'Deposit ID is required.'
            })

        # Retrieve the deposit request from the database
        deposit = DepositRequest.objects.get(id=deposit_id)

        # Return the deposit status
        return JsonResponse({
            'success': True,
            'status': deposit.status  # 'Pending' or 'Completed'
        })

    except DepositRequest.DoesNotExist:
        # Handle case where deposit doesn't exist
        return JsonResponse({
            'success': False,
            'message': 'Deposit not found.'
        })
    except Exception as e:
        # Handle other exceptions and return error message
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        })


def process_deposit(request):
    if request.method == "POST":
        try:
            # Fetch deposit details from form data
            amount = float(request.POST.get("depositAmount"))
            method = request.POST.get("depositMethod")
            payment_receipt = request.FILES.get("paymentScreenshot")  # Get the uploaded file

            # Minimum deposit check
            if amount < 16500:
                return JsonResponse({
                    "success": False, 
                    "message": "Minimum deposit is 16,500."
                })

            # Save the deposit request, including the payment receipt
            deposit_request = DepositRequest.objects.create(
                user=request.user,
                amount=amount,
                method=method,
                payment_receipt=payment_receipt,  # Add the payment receipt
                status="Pending"
            )

            # Return a response with the deposit_id
            return JsonResponse({
                "success": True,
                "message": "Deposit request sent, account will be credited shortly!",
                "deposit_id": deposit_request.id  # Include deposit_id in the response
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



def check_user_package(request):
    has_package = PurchasePackage.objects.filter(user=request.user).exists()
    return JsonResponse({'has_package': has_package})


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

        # Set email subject, plain text, and HTML content
        subject = 'Your Password Reset Code'
        text_content = f'Your password reset code is: {reset_code}'
        html_content = f'''
        <html>
            <body>
                <p>Hello {user.username},</p>
                <p>Your password reset code is:</p>
                <h2>{reset_code}</h2>
                <p>Please use this code to reset your password.</p>
                <p>Thank you!</p>
            </body>
        </html>
        '''
        from_email = settings.DEFAULT_FROM_EMAIL

        # Send email with both plain text and HTML content
        try:
            msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return JsonResponse({'success': True, 'message': 'A password reset code has been sent to your email.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Failed to send email. Please try again later.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


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
        try:
            user_balance = UserBalance.objects.get(user=request.user)  # Fetch the user's balance
        except UserBalance.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User balance not found.'
            })

        # Get the global withdrawal date and time from the WithdrawalTimeAndDate model
        try:
            withdrawal_time_db = WithdrawalTimeAndDate.objects.last()  # Assuming there's only one record for the global time
        except WithdrawalTimeAndDate.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Withdrawal time is not set.'
            })

        # Get the current date and time
        current_datetime = timezone.now()
        current_date = current_datetime.date()  # Get the current date
        current_time = current_datetime.time()  # Get the current time

        # Check if the current date matches the withdrawal date
        if current_date < withdrawal_time_db.withdrawal_date:
            return JsonResponse({
                'success': False,
                'message': f'Withdrawals are allowed starting from {withdrawal_time_db.withdrawal_date.strftime("%d-%m-%Y")}.'
            })

        # Extract the start and end times from the database
        withdrawal_start_time = withdrawal_time_db.withdrawal_start_time
        withdrawal_end_time = withdrawal_time_db.withdrawal_end_time

        # Treat midnight (00:00) as 23:59:59 to include it as the end of the day
        if withdrawal_end_time == datetime.strptime('00:00', '%H:%M').time():
            withdrawal_end_time = (datetime.combine(current_date, withdrawal_end_time) + timedelta(days=1) - timedelta(seconds=1)).time()

        # Check if the current time is within the allowed withdrawal window
        if current_date == withdrawal_time_db.withdrawal_date:
            # Check if current time is before the start time
            if current_time < withdrawal_start_time:
                return JsonResponse({
                    'success': False,
                    'message': f'You can only withdraw after {withdrawal_start_time.strftime("%H:%M")}.'
                })

            # Check if current time is after the end time
            if current_time > withdrawal_end_time:
                return JsonResponse({
                    'success': False,
                    'message': f'Withdrawals can only be made until {withdrawal_end_time.strftime("%H:%M")}.'
                })

        # Check if there are sufficient funds
        if user_balance.main_balance >= withdraw_amount:
            # Deduct the amount from the user's balance
            user_balance.main_balance -= withdraw_amount
            user_balance.save()

            # Create a new withdrawal request
            withdrawal_request = WithdrawalRequest.objects.create(
                user=request.user,
                amount=withdraw_amount,
                method=withdraw_method,
                status='Pending'  # Default status for new requests
            )

            # Success response with withdrawal ID
            return JsonResponse({
                'success': True,
                'message': f'Withdrawal request for {withdraw_amount} via {withdraw_method} has been submitted successfully!',
                'withdraw_id': withdrawal_request.id  # Include the withdrawal ID
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




 # Default redirect to admin index if no match found
def update_game_status(request, game_type, game_id, action):
    # Determine which game model to update based on the game_type
    if game_type == 'hot':
        game = get_object_or_404(HotGame, id=game_id)
    elif game_type == 'football_match':
        game = get_object_or_404(FootballMatch, id=game_id)
    elif game_type == 'premier_league':
        game = get_object_or_404(PremierLeagueGame, id=game_id)
    elif game_type == 'match':
        game = get_object_or_404(Match, id=game_id)
    else:
        messages.error(request, "Invalid game type.")
        return redirect('admin:index')  # Redirect to admin index page if invalid game_type
    
    # Perform action based on 'won' or 'lost'
    if action == 'won':
        game.status = 'won'
        messages.success(request, f"Game '{game}' marked as Won!")
        # Update all bets associated with this match to 'won'
        BetHistory.objects.filter(match=game).update(status='won')
        
    elif action == 'lost':
        game.status = 'lost'
        messages.error(request, f"Game '{game}' marked as Lost!")
        # Update all bets associated with this match to 'lost'
        BetHistory.objects.filter(match=game).update(status='lost')
        
    else:
        messages.error(request, "Invalid action.")
        return redirect('admin:index')  # Redirect to admin if action is invalid

    # Save the updated game status
    game.save()

    # Redirect to the appropriate changelist page based on the game type
    if game_type == 'hot':
        return redirect('admin:accounts_hotgame_changelist')
    elif game_type == 'football_match':
        return redirect('admin:accounts_footballmatch_changelist')  # Replace with correct URL name for football matches
    elif game_type == 'premier_league':
        return redirect('admin:accounts_premierleaguegame_changelist')  # Replace with correct URL name for premier league games
    elif game_type == 'match':
        return redirect('admin:accounts_match_changelist')  # Replace with correct URL name for matches

    return redirect('admin:index')






# def place_bet(request):
#     if request.method == 'POST':
#         user = request.user
#         try:
#             # Load and log the received JSON data
#             bet_details = json.loads(request.body)
          
#             match = bet_details.get('match')
#             date_str = bet_details.get('date')  # Match date as string
#             time_str = bet_details.get('time')  # Match time as string
#             fixed_score = bet_details.get('fixed_score')
#             bet_status = bet_details.get('status')

#             # Validate and convert profit_percentage
#             try:
#                 profit_percentage = Decimal(bet_details.get('profit_percentage'))
#             except (ValueError, InvalidOperation) as e:
#                 logger.error(f"Invalid profit percentage: {e}")
#                 return JsonResponse({'error': 'Invalid profit percentage provided.'}, status=400)

#             # Parse match start date and time from the strings provided
#             try:
#                 # Match start time as timezone-aware datetime in Africa/Lagos timezone
#                 match_start_time = timezone.make_aware(
#                     datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M"),
#                     timezone=pytz_timezone('Africa/Lagos')  # Set timezone to Nigeria time (WAT)
#                 )
#             except ValueError:
#                 logger.error("Invalid date or time format in bet details.")
#                 return JsonResponse({'error': 'Invalid date or time format provided.'}, status=400)

#             # Check if the current date and time are after the match start time
#             current_time = timezone.now()

#             # Convert current time to Nigeria time zone (Africa/Lagos)
#             current_time = current_time.astimezone(pytz_timezone('Africa/Lagos'))

#             # Debugging log to print both current time and match start time
#             logger.debug(f"Current time: {current_time} (Timezone: {current_time.tzinfo})")
#             logger.debug(f"Match start time: {match_start_time} (Timezone: {match_start_time.tzinfo})")

#             # Extract only the date (without time) in the Africa/Lagos timezone
#             match_start_date = match_start_time.astimezone(pytz_timezone('Africa/Lagos')).date()

#             # Get today's date in Africa/Lagos timezone
#             current_date = current_time.date()

#             # Compare the current date and match start date
#             if current_date != match_start_date:
#                 logger.warning(f"Betting attempt on a different date from the match date: "
#                                f"Current Date: {current_date} vs Match Date: {match_start_date}")
#                 logger.warning(f"Received bet details: {bet_details}")

#                 return JsonResponse({'error': 'Betting is only allowed on the match day.'}, status=400)

#             # Check if the current time is before the match start time
#             if current_time < match_start_time:
#                 logger.warning(f"Betting attempt before the scheduled match start time: "
#                                f"Current Time: {current_time} vs Match Start Time: {match_start_time}")
#                 return JsonResponse({'error': 'Bet has not started yet. Please wait for the match to start.'}, status=400)

#             # Check if the game status is "playing"
#             if bet_status != "playing":
#                 logger.warning("Game is not available for betting.")
#                 return JsonResponse({'error': 'Game not available.'}, status=400)

#             # Check the number of bets placed today
#             today = timezone.now().date()
#             bet_count = BetHistory.objects.filter(user=user, placed_at__date=today).count()

#             if bet_count >= 3:
#                 logger.warning(f"User {user.id} exceeded daily bet limit.")
#                 return JsonResponse({'error': 'Betting exceeded: You can only bet 3 times a day.'}, status=400)

#             try:
#                 # Check if user has a purchased package
#                 user_balance = UserBalance.objects.get(user=user)
#                 purchased_package = PurchasePackage.objects.get(name=user_balance.purchased_package_name)

#                 # Convert purchased_package.amount to Decimal
#                 package_amount = Decimal(purchased_package.amount)

#                 # Calculate profit based on the purchased package and profit percentage
#                 profit = (package_amount * profit_percentage) / 100

#                 # Update user's main balance
#                 user_balance.main_balance += profit
#                 user_balance.total_profits += profit
#                 user_balance.save()

#                 # Create a new BetHistory entry
#                 BetHistory.objects.create(
#                     user=user,
#                     match=match,
#                     date=date_str,
#                     time=time_str,
#                     fixed_score=fixed_score,
#                     profit_percentage=profit_percentage,
#                     bet_amount=profit,
#                 )
#                 formatted_profit = f"{profit:,.2f}"
#                 return JsonResponse({'message': 'Bet placed successfully!', 'profit': formatted_profit}, status=200)

#             except PurchasePackage.DoesNotExist:
#                 logger.error(f"PurchasePackage not found for user {user.id}.")
#                 return JsonResponse({'error': 'Please purchase a package before placing a bet.'}, status=400)
#             except UserBalance.DoesNotExist:
#                 logger.error(f"UserBalance not found for user {user.id}.")
#                 return JsonResponse({'error': 'User balance not found.'}, status=400)

#         except json.JSONDecodeError as e:
#             logger.error(f"JSON decoding error: {e}")
#             return JsonResponse({'error': 'Invalid JSON provided.'}, status=400)
#         except Exception as e:
#             logger.error(f"An unexpected error occurred: {str(e)}")
#             return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

#     logger.warning("Invalid request method for place_bet endpoint.")
#     return JsonResponse({'error': 'Invalid request method.'}, status=405)



from django.db import transaction
from django.db.models import F


def check_bet_status(request, bet_id):
    try:
        # Retrieve the bet history record for the given bet ID and ensure it belongs to the current user
        bet_history = BetHistory.objects.get(id=bet_id, user=request.user)
        game_status = bet_history.status

        if game_status == "won":
            # Use a transaction to ensure atomicity
            with transaction.atomic():
                user_balance = UserBalance.objects.select_for_update().get(user=request.user)
                purchased_package = PurchasePackage.objects.get(name=user_balance.purchased_package_name)

                # Calculate profit based on the user's package amount and the match profit percentage
                package_amount = purchased_package.amount
                profit = (package_amount * bet_history.profit_percentage) / 100
                
                
                bet_history.bet_amount = profit  # Set bet_amount to just the profit
                bet_history.save(update_fields=['bet_amount'])
                
                # Update the user's main balance with the calculated profit
                user_balance.main_balance = F('main_balance') + profit
                user_balance.save(update_fields=['main_balance'])

            return JsonResponse({
                'status': 'won',
                'profit': f"{profit:,.2f}"  # Format profit for display
            })

        elif game_status == "lost":
            # Bet lost, no profit to credit
            return JsonResponse({'status': 'loss', 'profit': "0.00"})

        elif game_status == "playing":
            # Game is still in progress
            return JsonResponse({'status': 'playing'})

    except BetHistory.DoesNotExist:
        return JsonResponse({'error': 'Bet not found'}, status=404)
    except PurchasePackage.DoesNotExist:
        return JsonResponse({'error': 'Purchased package not found'}, status=404)
    except UserBalance.DoesNotExist:
        return JsonResponse({'error': 'User balance not found'}, status=404)
    except Exception as e:
        # General exception handling
        return JsonResponse({'error': str(e)}, status=500)






def place_bet(request):
    if request.method == 'POST':
        user = request.user
        try:
            # Load and log the received JSON data
            bet_details = json.loads(request.body)
            match = bet_details.get('match')
            date_str = bet_details.get('date')
            time_str = bet_details.get('time')
            fixed_score = bet_details.get('fixed_score')
            bet_status = bet_details.get('status')

            # Validate and convert profit_percentage
            try:
                profit_percentage = Decimal(bet_details.get('profit_percentage'))
            except (ValueError, InvalidOperation) as e:
                logger.error(f"Invalid profit percentage: {e}")
                return JsonResponse({'error': 'Invalid profit percentage provided.'}, status=400)

            # Parse match start date and time in the correct timezone
            try:
                match_start_time = timezone.make_aware(
                    datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M"),
                    timezone=pytz_timezone('Africa/Lagos')
                )
            except ValueError:
                logger.error("Invalid date or time format in bet details.")
                return JsonResponse({'error': 'Invalid date or time format provided.'}, status=400)

            # Get the current time in the same timezone
            current_time = timezone.now().astimezone(pytz_timezone('Africa/Lagos'))
            match_start_date = match_start_time.date()
            current_date = current_time.date()

            # Allow betting only on the match day
            if current_date != match_start_date:
                logger.warning("Betting is only allowed on the match day.")
                return JsonResponse({'error': 'Betting is only allowed on the match day.'}, status=400)

            # Ensure the current time is before the match start time
            if current_time >= match_start_time:
                logger.warning("Betting attempt before match start time.")
                logger.warning(f"current time: {current_time}, match time: {match_start_time}")
                return JsonResponse({'error': 'Bet has not started yet. Please wait for the match to start.'}, status=400)

            # Check if the game status is "playing"
            if bet_status != "playing":
                logger.warning("Game is not available for betting.")
                return JsonResponse({'error': 'Game not available.'}, status=400)

            # Limit bets to 3 per day
            bet_count = BetHistory.objects.filter(user=user, placed_at__date=current_date).count()
            if bet_count >= 3:
                logger.warning(f"User {user.id} exceeded daily bet limit.")
                return JsonResponse({'error': 'Betting exceeded: You can only bet 3 times a day.'}, status=400)

            # Check for purchased package and user balance
            try:
                user_balance = UserBalance.objects.get(user=user)
                
                purchased_package = PurchasePackage.objects.get(name=user_balance.purchased_package_name)
                
               
                purchased_package_amount = purchased_package.amount 
               
                # Save bet in BetHistory
                bet_history = BetHistory.objects.create(
                    user=request.user,
                    match=match,
                    date=match_start_date,
                    time=timezone.now().time(),  # Set the time to the current time
                    fixed_score=fixed_score,
                    profit_percentage=profit_percentage,
                    bet_amount=purchased_package_amount,
                    status='playing'  # Default status on bet placement
                )

                # Respond with bet details including bet ID
                return JsonResponse({
                    'message': 'Bet placed successfully!',
                    'bet_id': bet_history.id  # Send the bet ID to the frontend
                }, status=200)

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




    
def custom_404_view(request, exception):
    return render(request, 'home/404.html', status=404)

def custom_500_view(request):
    return render(request, 'home/500.html', status=500)