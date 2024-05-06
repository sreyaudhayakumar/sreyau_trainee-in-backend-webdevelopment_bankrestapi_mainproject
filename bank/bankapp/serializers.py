from rest_framework import serializers
from .models import CustomUser,Account,Transaction,LoanApplication,Category, Budget, Expense,SavingsGoal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_role(self, value):
        valid_roles = ['admin', 'staff', 'customer']
        if value not in valid_roles:
            raise serializers.ValidationError(
                f"Invalid role. Role must be one of {', '.join(valid_roles)}."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create(**validated_data)
        if password:
            user.set_password(password)  
            user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role']
        

class AccountSerializer(serializers.ModelSerializer):
    account_type = serializers.ChoiceField(choices=Account.ACCOUNT_TYPE_CHOICES)

    class Meta:
        model = Account
        exclude = ['account_number', 'balance',]

class AccountListSerializer(serializers.ModelSerializer):
    account_type = serializers.ChoiceField(choices=Account.ACCOUNT_TYPE_CHOICES)

    class Meta:
        model = Account
        fields = '__all__'
        
class DepositSerializer(serializers.Serializer):
    deposit_amount = serializers.DecimalField(max_digits=10, decimal_places=2)        

class WithdrawalSerializer(serializers.Serializer):
    withdrawal_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    
class AccountSerializer(serializers.ModelSerializer):
    account_type = serializers.ChoiceField(choices=Account.ACCOUNT_TYPE_CHOICES)
    account_number = serializers.CharField(max_length=10, read_only=True)

    class Meta:
        model = Account
        fields = '__all__'

    def create(self, validated_data):
        user = validated_data.pop('user')
        account = Account.objects.create(user=user, **validated_data)
        return account
    
class TransferFundsSerializer(serializers.Serializer):
    source_account_id = serializers.IntegerField()
    destination_account_id = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'source_account', 'destination_account', 'amount', 'date']
        

class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = '__all__'
    
    
class CategoryReportSerializer(serializers.Serializer):
    name = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    budget_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    exceeded_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        
class SavingsGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsGoal
        fields = '__all__'
        