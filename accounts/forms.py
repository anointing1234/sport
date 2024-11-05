from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import authenticate
from accounts.models import Account,UsersBankDetail
import re
from django.core.exceptions import ValidationError



class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(max_length=100, help_text='Required. Add a valid email address')
    phone = forms.CharField(max_length=15, help_text='Required. Add a valid phone number')
    password = forms.CharField(widget=forms.PasswordInput(), help_text='Required. Enter a password')
    referral_code = forms.CharField(required=False, max_length=20, label='Referral Code', widget=forms.TextInput(attrs={'placeholder': 'Optional Referral Code'}))

    class Meta:
        model = Account
        fields = ("email", "phone", "password")  # Include password field directly

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-control-bg'  # Use Bootstrap styling
            field.widget.attrs['style'] = 'border: 1px solid black;'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if Account.objects.filter(password=password).exists():  # Check if the password exists (not typical)
            raise forms.ValidationError('This password has been used.')
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']  # Set phone field correctly
        user.fullname = 'Not set'  # Set fullname properly
        user.username = 'Not set'   # Set username properly
        
        if commit:
            user.set_password(self.cleaned_data['password'])  # Hash the password securely
            user.save()
        
        # Process referral code
        referral_code = self.cleaned_data.get('referral_code')
        if referral_code:
            try:
                referrer = Account.objects.get(referral_code=referral_code)
                user.referred_by = referrer  # Associate the new user with the referrer
                user.save()
            except Account.DoesNotExist:
                pass  # Optionally handle the case where the referral code is invalid
            
        return user



class UsersBankDetailsForm(forms.ModelForm):
    BANK_CHOICES = [
        ('Select bank', 'Select Bank'),
        ('Access Bank', 'Access Bank'),
        ('Citibank Nigeria', 'Citibank Nigeria'),
        ('Ecobank Nigeria', 'Ecobank Nigeria'),
        ('Fidelity Bank', 'Fidelity Bank'),
        ('First Bank of Nigeria', 'First Bank of Nigeria'),
        ('First City Monument Bank', 'First City Monument Bank'),
        ('Guaranty Trust Bank', 'Guaranty Trust Bank'),
        ('Heritage Bank', 'Heritage Bank'),
        ('Keystone Bank', 'Keystone Bank'),
        ('Polaris Bank', 'Polaris Bank'),
        ('Providus Bank', 'Providus Bank'),
        ('Stanbic IBTC Bank', 'Stanbic IBTC Bank'),
        ('Standard Chartered Bank', 'Standard Chartered Bank'),
        ('Sterling Bank', 'Sterling Bank'),
        ('SunTrust Bank', 'SunTrust Bank'),
        ('Union Bank of Nigeria', 'Union Bank of Nigeria'),
        ('United Bank for Africa', 'United Bank for Africa'),
        ('Unity Bank', 'Unity Bank'),
        ('Wema Bank', 'Wema Bank'),
        ('Zenith Bank', 'Zenith Bank'),
        ('Opay', 'Opay'),
        ('Kuda Bank', 'Kuda Bank'),
        ('VFD Microfinance Bank', 'VFD Microfinance Bank'),
        ('ALAT by Wema', 'ALAT by Wema'),
        ('Rubies Microfinance Bank', 'Rubies Microfinance Bank'),
        ('Sparkle Bank', 'Sparkle Bank'),
        ('Eyowo', 'Eyowo'),
        ('One Finance (OneBank)', 'One Finance (OneBank)'),
        ('PalmPay', 'PalmPay'),
        ('Paycom (Paga)', 'Paycom (Paga)'),
    ]

    # Define bank_name as a ChoiceField
    bank_name = forms.ChoiceField(choices=BANK_CHOICES, label='Bank Name', required=True)

    class Meta:
        model = UsersBankDetail
        fields = ['account_number', 'bank_name', 'account_holder_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-control-bg'  # Use Bootstrap styling
            field.widget.attrs['style'] = 'border: 1px solid black;'
            




class LoginForm(forms.Form):
    phone = forms.CharField(label="Phone Number", max_length=15)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ['phone', 'password']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control form-control-bg'  # Use Bootstrap styling
            field.widget.attrs['style'] = 'border: 1px solid black;'
            
    def clean(self):
        phone = self.cleaned_data.get('phone')
        password = self.cleaned_data.get('password')

        # Authenticate with phone and password
        user = authenticate(phone=phone, password=password)
        if user is None:
            raise forms.ValidationError("Invalid phone number or password.")
        self.user_cache = user
        return self.cleaned_data

    def get_user(self):
        return self.user_cache
    
    
    
    
    
      
class PasswordSendResetForm(forms.Form):
    email = forms.EmailField(
        label="Enter your email address",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control border-none',  # Bootstrap class for styling
            'placeholder': 'example@example.com',
            'style': 'border: 1px solid black;'# Placeholder text
        }),
        error_messages={
            'required': 'This field is required.',
            'invalid': 'Enter a valid email address.',
        }
    )  
   
   




class PasswordResetForm(forms.Form):
    phone = forms.CharField(
        max_length=15,
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'border: 1px solid black;',
            'placeholder': 'Enter your phone number'
        }),
        error_messages={
            'required': 'Phone number is required.',
            'max_length': 'Phone number cannot exceed 15 characters.'
        }
    )
    reset_code = forms.CharField(
        max_length=10,
        label="Reset Code",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'border: 1px solid black;',
            'placeholder': 'Enter reset code'
        }),
        error_messages={
            'required': 'Reset code is required.',
            'max_length': 'Reset code cannot exceed 10 characters.'
        }
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'style': 'border: 1px solid black;',
            'placeholder': 'Enter new password'
        }),
        label="New Password",
        error_messages={'required': 'New password is required.'}
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'style': 'border: 1px solid black;',
            'placeholder': 'Confirm new password'
        }),
        label="Confirm Password",
        error_messages={'required': 'Please confirm your new password.'}
    )

    def clean_reset_code(self):
        reset_code = self.cleaned_data.get('reset_code')
        if not reset_code.isdigit() or len(reset_code) != 6:  # Assuming a 6-digit numeric code
            raise ValidationError("Reset code must be a 6-digit number.")
        return reset_code

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        # Password strength check: Minimum 8 characters, includes letters and numbers
        if len(new_password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", new_password) or not re.search(r"[0-9]", new_password):
            raise ValidationError("Password must contain both letters and numbers.")
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "The two password fields must match.")