

from django.urls import path
from .views import* 

urlpatterns = [
    path('register/', UserRegistration.as_view(), name='user-registration'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('logout/', UserLogout.as_view(), name='user_logout'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
    path('accounts/create/', AccountCreateView.as_view(), name='account-create'),
    path('accounts/', AccountListView.as_view(), name='account-list'),
    path('accounts/detailviewbyuser/', UserAccountDetailView.as_view(), name='user_account_detail'),
    path('accounts/<int:pk>/update/', AccountUpdateView.as_view(), name='account-update'),
    path('accounts/<int:pk>/delete/', AccountDeleteView.as_view(), name='account-delete'),
    path('accounts/<int:pk>/deposit/', DepositView.as_view(), name='account-deposit'),
    path('accounts/<int:pk>/withdraw/', WithdrawalView.as_view(), name='account-withdraw'),
    path('transfer/', TransferFunds.as_view(), name='transfer_funds'),
    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
    path('loan-applications/', LoanApplicationListCreateView.as_view(), name='loan-application-list-create'),
    # path('loan-applications/<int:pk>/', LoanApplicationDetailView.as_view(), name='loan-application-detail'),
    path('loan-applicationsview/', LoanApplicationListCreateView.as_view(), name='loan-application-list-create'),
    path('loan-applications/<int:pk>/', LoanApplicationDetailView.as_view(), name='loan-application-detail'),
    path('categories/create/', CategoryCreateAPIView.as_view(), name='category-create'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('budgets/create/', BudgetCreateAPIView.as_view(), name='budget-create'),
    path('budgets/', BudgetListAPIView.as_view(), name='budget-list'),
    path('expenses/create/', ExpenseCreateAPIView.as_view(), name='expense-create'),
    path('expenses/', ExpenseListAPIView.as_view(), name='expense-list'),
    path('expense-report/', ExpenseCategoryReportAPIView.as_view(), name='expense-category-report'),
    path('savingsgoals/', SavingsGoalListCreate.as_view(), name='savings_goal_list_create'),
    path('savingsgoals/<int:pk>/', SavingsGoalDetailUpdateDelete.as_view(), name='savings_goal_detail_update_delete'),
]
