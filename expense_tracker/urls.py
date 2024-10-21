

from django.urls import path
from .views import *
urlpatterns = [
    path('add-expense/', AddExpenseView.as_view(), name='add-expense'),

    path('get-expense/', UserExpensesView.as_view(), name='user_expenses'),

    # Retrieve overall expenses
    path('overall/', OverallExpensesView.as_view(), name='overall_expenses'),

    # Download balance sheet
    path('balance-sheet-download/', DownloadBalanceSheetView.as_view(), name='download_balance_sheet'),

]