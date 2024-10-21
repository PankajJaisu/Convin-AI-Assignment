from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

from expense_tracker.models import Expense, ExpenseSplit  
from django.test import TestCase

import requests  

User = get_user_model()

class IntegrationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.token = AccessToken.for_user(self.user)

    def test_complete_download_balance_sheet_integration(self):
        response = self.client.get(
            reverse('download_balance_sheet'),  
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_balance_sheet_without_authentication(self):
        response = self.client.get(reverse('download_balance_sheet')) 
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  

    def test_expense_creation_and_balance_sheet(self):
        response = self.client.post(
            reverse('add_expense'), 
            data={'description': 'Test Expense', 'total_amount': 100},
            HTTP_AUTHORIZATION=f'Bearer {self.token}'  
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 

        response = self.client.get(
            reverse('download_balance_sheet'),  
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_expense_creation_with_invalid_data(self):
        response = self.client.post(
            reverse('add_expense'), 
            data={'description': '', 'total_amount': ''},
            HTTP_AUTHORIZATION=f'Bearer {self.token}' 
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)