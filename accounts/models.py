import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import datetime, timedelta




class AccountManager(BaseUserManager):
    def create_user(self, phone, email, username, password=None, **extra_fields):
        if not phone:
            raise ValueError("User must have a phone number")
        if not username:
            raise ValueError("User must have a username")
        if not email:
            raise ValueError("User must have an email address")

        email = self.normalize_email(email)
        user = self.model(phone=phone, email=email, username=username, **extra_fields)
        user.set_password(password)  # Set the password using Django's hashing method
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not username:
            username = f"admin_{email.split('@')[0]}"  # Generate a default username

        return self.create_user(phone=phone, email=email, username=username, password=password, **extra_fields)


def generate_unique_referral_code(length=6):
    """Generate a unique random alphanumeric referral code."""
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        if not Account.objects.filter(referral_code=code).exists():
            return code

class Account(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(verbose_name="phone number", max_length=15, unique=True)
    email = models.EmailField(verbose_name="email", max_length=100, unique=True)
    username = models.CharField(max_length=100)
    fullname = models.CharField(max_length=200)
    referral_code = models.CharField(max_length=6, unique=True, editable=False)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referred')
    referral = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals', default=None)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # Changed default to True for regular users
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
   
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email']
    
    objects = AccountManager()

    def __str__(self):
        return self.phone

    def save(self, *args, **kwargs):
        # Generate a unique referral code if it hasn't been set
        if not self.referral_code:
            self.referral_code = generate_unique_referral_code()
        super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class UsersReferralPercentage(models.Model):
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    def __str__(self):
        return f"{self.percentage}%"



class ReferralBonus(models.Model):
    referrer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="bonuses_given")
    referred_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="bonuses_received")
    bonus_amount = models.DecimalField(max_digits=15, decimal_places=2)
    date_awarded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bonus_amount} awarded to {self.referrer.username} for referring {self.referred_user.username}"



class UsersBankDetail(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='bank_details')
    account_number = models.CharField(max_length=20, unique=True)
    bank_name = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.account_holder_name} - {self.bank_name}"


class UserBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    main_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_profits = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    purchased_package_name = models.CharField(max_length=100, null=True, blank=True)  # Allow NULL
    purchased_package = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Balance"
    
 
class ShowcaseSlider(models.Model):
    image = models.ImageField(upload_to='showcase_slider/')

    class Meta:
        verbose_name = 'Showcase Slide'
        verbose_name_plural = 'Showcase Slides'

    # Override delete method to delete the image file from storage
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)



class soccer_slider(models.Model):
    image = models.ImageField(upload_to='soccer_slider/')

    class Meta:
        verbose_name = 'soccer_slider'
        verbose_name_plural = 'soccer_slider'

    # Override delete method to delete the image file from storage
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)        

class leagues_slider(models.Model):
    image = models.ImageField(upload_to='leagues_slider/')

    class Meta:
        verbose_name = 'leagues_slider'
        verbose_name_plural = 'leagues_slider'

    # Override delete method to delete the image file from storage
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)        


       


class Package(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    daily_interest = models.DecimalField(max_digits=5, decimal_places=2, help_text="Daily interest rate in percentage")
    withdrawal_frequency = models.CharField(max_length=50, help_text="Withdrawal frequency description")

    def __str__(self):
        return self.name    






class BetHistory(models.Model):
    STATUS_CHOICES = [
        ('playing', 'Playing'),
        ('won', 'Won'),
        ('loss', 'Loss'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use the custom user model
    match = models.CharField(max_length=255)
    date = models.DateField()  # The date of the match
    time = models.TimeField()  # The time of the match
    fixed_score = models.CharField(max_length=10)  # e.g., "2 - 0"
    profit_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 5.00
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 100.00
    placed_at = models.DateTimeField(auto_now_add=True)  # Automatically set the date/time when the bet is placed
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='playing')  # Status of the bet
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.match} on {self.date} at {self.time} (Status: {self.status}, Placed at: {self.placed_at})"
   
   
   
   
class DepositRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to the custom user model
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # Store deposit amount
    method = models.CharField(max_length=50)  # Deposit method (e.g., Bank Transfer)
    date = models.DateTimeField(auto_now_add=True)  # Automatically set the date when created
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')])  # Status of the deposit
    payment_receipt = models.ImageField(upload_to='payment_receipts/', blank=True, null=True)  # Image field for payment receipt

    def __str__(self):
        return f"{self.user.username} - Deposit: {self.amount} ({self.status})"

class WithdrawalRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to the custom user model
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # Store withdrawal amount
    method = models.CharField(max_length=50)  # Withdrawal method (e.g., Bank Transfer)
    date = models.DateTimeField(auto_now_add=True)  # Automatically set the date when created
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')])  # Status of the withdrawal
 
    def __str__(self):
        return f"{self.user.username} - Withdrawal: {self.amount} ({self.status})"



class AdminBankAccount(models.Model):
    account_number = models.CharField(max_length=20, unique=True)
    bank_name = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.account_holder_name} - {self.bank_name} ({self.account_number})"    


class PurchasePackage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    daily_profit = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_withdrawal = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'name']  # Ensure each user has only one package with a specific name
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"



class PasswordResetCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.code}'



class WithdrawalTimeAndDate(models.Model):
    # This field will store the date for the global withdrawal period (input by the admin)
    withdrawal_date = models.DateField()

    # This field will store the start time for the global withdrawal period (fixed time, e.g., 09:00)
    withdrawal_start_time = models.TimeField()

    # This field will store the end time for the global withdrawal period (e.g., 12:00 AM next day)
    withdrawal_end_time = models.TimeField()

    def save(self, *args, **kwargs):
        # If no start or end time is set, use default values
        if not self.withdrawal_start_time:
            self.withdrawal_start_time = datetime.strptime('09:00', '%H:%M').time()
        if not self.withdrawal_end_time:
            self.withdrawal_end_time = datetime.strptime('23:59', '%H:%M').time()

        # If withdrawal date is not provided (default value), calculate the next Monday
        if not self.withdrawal_date:
            today = datetime.today()
            days_ahead = 0 - today.weekday()  # Monday is 0 in weekday()
            if days_ahead <= 0:  # If today is Monday, it should not skip to the next Monday
                days_ahead += 7
            self.withdrawal_date = today + timedelta(days=days_ahead)

        super().save(*args, **kwargs)

    def __str__(self):
        # Format both date and time
        return f'Withdrawal time set at {self.withdrawal_date.strftime("%d-%m-%Y")} from {self.withdrawal_start_time.strftime("%H:%M")} to {self.withdrawal_end_time.strftime("%H:%M")}'







class HotGame(models.Model):
    STATUS_CHOICES = [
        ('playing', 'Playing'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]
    CATEGORY_CHOICES = [
        ('home', 'Home'),
        ('away', 'Away'),
        ('draw', 'Draw'),
    ]

    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    fixed_score = models.CharField(max_length=10)
    start_time = models.DateTimeField()
    profit_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='playing')
    prediction = models.CharField(max_length=10,choices=CATEGORY_CHOICES,default='home')  # New field

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"

    def get_start_time_local(self):
        # Convert start time to the local timezone (WAT)
        return self.start_time.astimezone(timezone.get_current_timezone())






class PremierLeagueGame(models.Model):
    STATUS_CHOICES = [
        ('playing', 'Playing'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]

    match = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    fixed_score = models.CharField(max_length=7)
    profit_percentage = models.PositiveIntegerField(default=3)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='playing')  # Added status field

    def __str__(self):
        return f"{self.match} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"  # Display match and start time

    def get_start_time_local(self):
        # Convert start time to the local timezone (WAT)
        return self.start_time.astimezone(timezone.get_current_timezone())

    class Meta:
        verbose_name = "Premier League Game"
        verbose_name_plural = "Premier League Games"


class FootballMatch(models.Model):
    MATCH_TYPE_CHOICES = [
        ('soccer', 'Soccer Matches'),
    ]
    STATUS_CHOICES = [
        ('playing', 'Playing'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]

    match_type = models.CharField(max_length=10, choices=MATCH_TYPE_CHOICES)
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    fixed_score = models.CharField(max_length=10, help_text="Format: X - Y (e.g., 2 - 1)")
    profit_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Profit percentage")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='playing')  # Added status field

    def __str__(self):
        start_time_str = self.start_time.strftime('%Y-%m-%d %H:%M') if self.start_time else 'Unknown Time'
        return f"{self.home_team} vs {self.away_team} on {start_time_str} ({self.match_type})"

    def get_start_time_local(self):
        # Convert start time to the local timezone (WAT)
        return self.start_time.astimezone(timezone.get_current_timezone())


class Match(models.Model):
    league_choices = [
        ('PL', 'Premier League'),
        ('LL', 'La Liga'),
        ('BL', 'Bundesliga'),
        ('SA', 'Serie A'),
    ]
    STATUS_CHOICES = [
        ('playing', 'Playing'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]

    league = models.CharField(max_length=2, choices=league_choices)
    match_name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    fixed_score = models.CharField(max_length=10, help_text="Format: X - Y (e.g., 2 - 0)")
    profit_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Profit percentage")  # e.g., 5.00 for 5%
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='playing')  # Added status field

    def __str__(self):
        return f"{self.match_name} - {self.fixed_score} ({self.league})"

    def get_start_time_local(self):
        # Convert start time to the local timezone (WAT)
        return self.start_time.astimezone(timezone.get_current_timezone())



class Prediction(models.Model):
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    start_date = models.DateField()
    start_time = models.TimeField()
    fixed_score = models.CharField(max_length=20)
    profit_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20)
    prediction = models.TextField()

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"