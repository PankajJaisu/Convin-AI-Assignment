from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    description = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  
    created_at = models.DateTimeField(auto_now_add=True)

class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, related_name='splits', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)