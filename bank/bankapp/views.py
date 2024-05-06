from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from rest_framework.generics import RetrieveAPIView
from rest_framework import generics
from rest_framework import status
from .models import Account
from decimal import Decimal
from .serializers import TransferFundsSerializer
from .models import Transaction
from django.db.models import Q
from django.conf import settings
from rest_framework import  permissions
from .models import LoanApplication
from django.core.mail import send_mail
from .models import CustomUser
from django.db.models import Sum
from datetime import date
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import Category, Budget, Expense,SavingsGoal
from .serializers import (
    UserSerializer, AccountSerializer,
    UserLoginSerializer,
    UserUpdateSerializer,
    DepositSerializer,CategorySerializer,TransactionSerializer,LoanApplicationSerializer, BudgetSerializer, ExpenseSerializer, WithdrawalSerializer,AccountListSerializer,CategoryReportSerializer,SavingsGoalSerializer
)

class UserRegistration(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                user.last_login = timezone.now()
                user.save()

                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({'detail': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser or request.user.role in ['admin', 'staff']:
            users = CustomUser.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'You do not have permission to access this resource'}, status=status.HTTP_403_FORBIDDEN)



class UserUpdateView(RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()
        

class UserLogout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)



class AccountCreateView(generics.CreateAPIView):
    serializer_class = AccountSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Account created successfully,check mail for your account number"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountListView(generics.ListAPIView):
    serializer_class = AccountListSerializer

    def get_queryset(self):
        queryset = Account.objects.all()

        account_type = self.request.query_params.get('account_type')
        if account_type:
            queryset = queryset.filter(account_type=account_type)

        user_name = self.request.query_params.get('user_name')
        if user_name:
            queryset = queryset.filter(user__username__icontains=user_name)

        return queryset

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication credentials not provided"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not (request.user.is_superuser or request.user.role in ['admin', 'staff']):
            return Response({"error": "You do not have permission to access this resource"}, status=status.HTTP_403_FORBIDDEN)

        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
class UserAccountDetailView(RetrieveAPIView):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(user=user)

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.first()
        if obj:
            obj.account_number = obj.account_number
        return obj
    
class AccountUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    
    def perform_update(self, serializer):
        account = self.get_object()
        if self.request.user.is_superuser or self.request.user.role in ['admin', 'staff']:
            serializer.save()
        elif account.user == self.request.user:
            serializer.save()
        else:
            return Response({"error": "You do not have permission to update this account"}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
class AccountDeleteView(generics.DestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def destroy(self, request, *args, **kwargs):
        account = self.get_object()
        if self.request.user.is_superuser or self.request.user.role in ['admin', 'staff']:
            account.delete()
            return Response({"message": "Account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        elif account.user == self.request.user:
            account.delete()
            return Response({"message": "Account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "You do not have permission to delete this account"}, status=status.HTTP_403_FORBIDDEN)
        

class DepositView(generics.CreateAPIView):

    queryset = Account.objects.all()
    serializer_class = DepositSerializer

    def create(self, request, *args, **kwargs):
        account = self.kwargs['pk']
        account_obj=Account.objects.get(id=account)
        account_type=account_obj.account_type
        if account_type==1:
            account = self.get_queryset().filter(account_type=1).first()
            interest_rate = 0
        elif account_type==2:    
            account = self.get_queryset().filter(account_type=2).first()
            interest_rate = 0
        elif account_type == 4:
            account = self.get_queryset().filter(account_type=4).first()
            interest_rate = 0.05  
        elif account_type == 3:
            account = self.get_queryset().filter(account_type=3).first()
            interest_rate = 0.08  
        else:
            return Response({"error": "Account type not supported"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not account:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        deposit_amount = serializer.validated_data['deposit_amount']

        if deposit_amount <= 0:
            return Response({"error": "Invalid deposit amount"}, status=status.HTTP_400_BAD_REQUEST)
        interest_amount = deposit_amount * Decimal(interest_rate)
        total_deposit = deposit_amount + interest_amount

        account_obj.balance += total_deposit
        account_obj.save()

        return Response({"message": f"Successfully deposited {deposit_amount} into the account",
                         "interest_amount": interest_amount,
                         "updated_balance": account_obj.balance},
                        status=status.HTTP_200_OK)



class WithdrawalView(generics.CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = WithdrawalSerializer

    def create(self, request, *args, **kwargs):
        account = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        withdrawal_amount = serializer.validated_data['withdrawal_amount']

        if withdrawal_amount <= 0:
            return Response({"error": "Invalid withdrawal amount"}, status=status.HTTP_400_BAD_REQUEST)

        if account.account_type == 1 and withdrawal_amount > 50000:
            return Response({"error": "Savings Account holders cannot withdraw more than 50000."}, status=status.HTTP_400_BAD_REQUEST)

        if account.balance < withdrawal_amount:
            return Response({"error": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)
        
        account.balance -= withdrawal_amount
        account.save()
        response_message = f"Withdrawn {withdrawal_amount} from your account. Your new balance is {account.balance}."

        return Response({"message": response_message}, status=status.HTTP_200_OK)



class TransferFunds(APIView):
    def post(self, request):
        source_account_id = request.data.get('source_account_id')
        destination_account_number = request.data.get('destination_account_number')
        amount = request.data.get('amount')
        
        try:
            source_account = Account.objects.get(pk=source_account_id)
            destination_account = Account.objects.get(account_number=destination_account_number)
        except Account.DoesNotExist:
            return Response({'error': 'One of the accounts does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            amount = Decimal(amount)
        except ValueError:
            return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
        
        today = timezone.now().date()
        
        daily_transaction_sum_source = Transaction.objects.filter(
            source_account=source_account,
            date__date=today
        ).aggregate(total_amount=Sum('amount'))['total_amount'] or Decimal('0.0')
        
        if source_account.account_type == 1 and daily_transaction_sum_source + amount > 40000:
            return Response({'error': 'Daily transaction limit exceeded for this Savings Account.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            source_account.transfer_funds(destination_account, amount)
            return Response({'message': 'Funds transferred successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



        
class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['admin', 'staff']:
            return Transaction.objects.all()
        else:
            return Transaction.objects.filter(Q(source_account__user=user) | Q(destination_account__user=user))
        

class LoanApplicationListCreateView(generics.ListCreateAPIView):
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)
    
class LoanApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff: 
            return LoanApplication.objects.all()
        else:
            return LoanApplication.objects.filter(applicant=self.request.user)

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


class LoanApplicationDetailView(generics.RetrieveUpdateAPIView):
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'approved':
            self.send_approval_email(instance)
        elif instance.status == 'rejected':
            self.send_rejection_email(instance)

    def send_approval_email(self, loan_application):
        subject = "Loan Application Approved"
        message = f"Dear {loan_application.applicant.username},\n\nYour {loan_application.get_loan_type_display()} loan application has been approved."
        send_mail(subject, message, 'sreyabank@example.com', [loan_application.applicant.email])

    def send_rejection_email(self, loan_application):
        subject = "Loan Application Rejected"
        message = f"Dear {loan_application.applicant.username},\n\nWe regret to inform you that your {loan_application.get_loan_type_display()} loan application has been rejected."
        send_mail(subject, message, 'sreyabank@example.com', [loan_application.applicant.email])
        
class CategoryCreateAPIView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class BudgetCreateAPIView(generics.CreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

class BudgetListAPIView(generics.ListAPIView):
    serializer_class = BudgetSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['admin', 'staff']:
            return Budget.objects.all()
        else:
            return Budget.objects.filter(user=user)


class ExpenseCreateAPIView(generics.CreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

class ExpenseListAPIView(generics.ListAPIView):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['admin', 'staff']:
            return Expense.objects.all()
        else:
            return Expense.objects.filter(user=user)
        

class ExpenseCategoryReportAPIView(generics.ListAPIView):
    serializer_class = CategoryReportSerializer

    def get_queryset(self):
        user = self.request.user
        
        if user.is_superuser or user.role in ['admin', 'staff']:
            expenses = Expense.objects.all()
        else:
            expenses = Expense.objects.filter(user=user)

        category_list = []
        for expense in expenses:
            category_name = expense.category.name
            
            total_amount = expense.amount
            
            if user.is_superuser or user.role in ['admin', 'staff']:
                budget = Budget.objects.filter(category=expense.category).first()
            else:
                budget = Budget.objects.filter(user=user, category=expense.category).first()

            budget_amount = budget.amount if budget else 0
            
            exceeded_amount = max(total_amount - budget_amount, 0)

            category_data = {
                'name': category_name,
                'total_amount': total_amount,
                'budget_amount': budget_amount,
                'exceeded_amount': exceeded_amount,
            }
            category_list.append(category_data)

        return category_list
    
class SavingsGoalListCreate(generics.ListCreateAPIView):
    serializer_class = SavingsGoalSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return SavingsGoal.objects.all()  
        else:
            return SavingsGoal.objects.filter(user=self.request.user)  

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SavingsGoalDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = SavingsGoal.objects.all()
    serializer_class = SavingsGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return SavingsGoal.objects.all()  
        else:
            return SavingsGoal.objects.filter(user=self.request.user)  

    def perform_update(self, serializer):
        instance = serializer.instance
        updated_amount = serializer.validated_data.get('current_amount', instance.current_amount)
        instance.current_amount += updated_amount
        instance.save()

        if instance.current_amount >= instance.goal_amount:
            instance.achieved = True
            instance.save()
            message = f"Congratulations! You've achieved your savings goal."
            subject = f"Savings Goal Achieved"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [self.request.user.email])

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        if self.request.user.is_superuser or self.request.user == instance.user:
            instance.delete()
            return Response({"detail": "Savings goal deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)