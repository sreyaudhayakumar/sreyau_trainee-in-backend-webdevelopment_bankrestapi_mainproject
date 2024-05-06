from django.contrib import admin
from .models import CustomUser,Account,Transaction,LoanApplication,Category,SavingsGoal

admin.site.register(CustomUser)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(LoanApplication)
admin.site.register(Category)
admin.site.register(SavingsGoal)
