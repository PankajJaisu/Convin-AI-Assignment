from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from django.contrib.auth import get_user_model
import requests  # To validate the PDF URL
from rest_framework_simplejwt.tokens import AccessToken


User = get_user_model()
class DownloadBalanceSheetViewTests(TestCase):
    def setUp(self):
        # Create a user for authentication
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.token = AccessToken.for_user(self.user)

    def test_download_balance_sheet_no_expenses(self):
        response = self.client.get(
            reverse('download_balance_sheet'), 
            HTTP_AUTHORIZATION=f'Bearer {self.token}'  
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_balance_sheet_success(self):
        response = self.client.get(
            reverse('download_balance_sheet'), 
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_download_balance_sheet_unauthenticated(self):
        response = self.client.get(reverse('download_balance_sheet')) 
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)