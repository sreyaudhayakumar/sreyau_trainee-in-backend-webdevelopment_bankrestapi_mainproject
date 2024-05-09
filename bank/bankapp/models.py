from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.mail import send_mail
import random
import string


class CustomUser(AbstractUser):
    USER_ROLES = (
        ('customer', 'Customer'),
        ('staff', 'Staff'),
    )
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    
    def save(self, *args, **kwargs):
        if self.is_superuser:  
            self.role = 'admin'
        super().save(*args, **kwargs)


class Account(models.Model):
    ACCOUNT_TYPES = [
        (1, 'Savings Account'),
        (2, 'Current Account'),
        (3, 'Fixed Deposit Account'),
        (4, 'Recurring Deposit Account'),
    ]

    ACCOUNT_TYPE_CHOICES = [(x[0], f"{x[0]} - {x[1]}") for x in ACCOUNT_TYPES]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_type = models.IntegerField(choices=ACCOUNT_TYPE_CHOICES)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    guardian_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    gender_choices = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=gender_choices)
    pin_code = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='user_photos/', blank=True)
    account_number = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.get_account_type_display()} for {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.pk:  
            super().save(*args, **kwargs)  
            self.account_number = self.generate_account_number()  
            self.save()  
            self.send_account_number_email()  
        else:
            super().save(*args, **kwargs)

    def generate_account_number(self):
        unique_chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(unique_chars, k=10))

    def send_account_number_email(self):
        user_email = self.user.email
        subject = "Your New Account Number"
        message = f"Dear {self.user.username},\n\nYour new account number is: {self.account_number}"
        send_mail(subject, message, 'sreyabank@example.com', [user_email])
        
    def transfer_funds(self, destination_account, amount):
        if self.balance < amount:
            raise ValidationError("Insufficient funds in the source account.")

        self.balance -= amount
        destination_account.balance += amount
        self.save()
        destination_account.save()
        Transaction.objects.create(source_account=self, destination_account=destination_account, amount=amount)

        return True
        
class Transaction(models.Model):
    source_account = models.ForeignKey(Account, related_name='source_transactions', on_delete=models.CASCADE)
    destination_account = models.ForeignKey(Account, related_name='destination_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)   
    

class LoanApplication(models.Model):
    LOAN_TYPES = [
        ('personal', 'Personal Loan'),
        ('home', 'Home Loan'),
        ('car', 'Car Loan'),
        ('education', 'Education Loan'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    loan_type = models.CharField(max_length=20, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    applied_date = models.DateTimeField(auto_now_add=True)
    document = models.FileField(upload_to='loan_documents/', null=True, blank=True)

    def __str__(self):
        return f"{self.get_loan_type_display()} Loan Application by {self.applicant.username}"
    
    
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class Budget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()

    def __str__(self):
        return f"{self.user.username}'s {self.category.name} Budget"

class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username}'s {self.category.name} Expense"

class SavingsGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date = models.DateField()
    achieved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Savings Goal"

    def check_milestone_completion(self):
        completion_percentage = (self.current_amount / self.goal_amount) * 100
        if completion_percentage >= 25 and not self.achieved:
            self.achieved = True
            self.save()
            return True
        return False