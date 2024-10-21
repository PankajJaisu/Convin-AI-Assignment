from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Expense, ExpenseSplit  # Assuming you have these models
from django.db import transaction
from django.http import FileResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import ExpenseSplit

from django.conf import settings
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from reportlab.pdfgen import canvas
from io import BytesIO
import cloudinary.uploader
from decouple import config
import os

User = get_user_model()


class AddExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        description = request.data.get('description')
        amount = request.data.get('amount')
        split_method = request.data.get('split_method')
        participants = request.data.get('participants')  # List of participants
       

        if not description or not amount or not split_method or not participants:
            return JsonResponse({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        users = []
        splits = {}

        
        if split_method == 'equal':
            # For the 'equal' method, participants are just a list of mobile numbers
            for mobile_number in participants:
                try:
                    user = User.objects.get(profile__mobile_number=mobile_number)
                    users.append(user)
                except User.DoesNotExist:
                    return JsonResponse({'error': f'User with mobile number {mobile_number} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            split_amount = amount / len(users)
            splits = {user.id: split_amount for user in users}

        elif split_method == 'exact':
            # For the 'exact' method, participants should be a list of dictionaries with 'mobile' and 'amount'
            for participant in participants:
                mobile_number = participant.get('mobile')
                user_amount = participant.get('amount')
                
                if mobile_number and user_amount:
                    try:
                        user = User.objects.get(profile__mobile_number=mobile_number)
                        users.append(user)
                        splits[user.id] = user_amount
                    except User.DoesNotExist:
                        return JsonResponse({'error': f'User with mobile number {mobile_number} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return JsonResponse({'error': 'Each participant must have a mobile number and amount for exact split.'}, status=status.HTTP_400_BAD_REQUEST)

        elif split_method == 'percentage':
            # For the 'percentage' method, participants should be a list of dictionaries with 'mobile' and 'percentage'
            total_percentage = 0
            for participant in participants:
                mobile_number = participant.get('mobile')
                user_percentage = participant.get('percentage')

                if mobile_number and user_percentage:
                    total_percentage += user_percentage
                    try:
                        user = User.objects.get(profile__mobile_number=mobile_number)
                        users.append(user)
                        splits[user.id] = (user_percentage / 100) * amount
                    except User.DoesNotExist:
                        return JsonResponse({'error': f'User with mobile number {mobile_number} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return JsonResponse({'error': 'Each participant must have a mobile number and percentage for percentage split.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if total_percentage != 100:
                return JsonResponse({'error': 'Total percentage must add up to 100.'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return JsonResponse({'error': 'Invalid split method.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Create the main expense record
                expense = Expense.objects.create(
                    description=description,
                    total_amount=amount,
                    creator=request.user
                )

                # Create individual splits
                for user_id, split_amount in splits.items():
                    ExpenseSplit.objects.create(
                        expense=expense,
                        user_id=user_id,
                        amount_owed=split_amount
                    )

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({'message': 'Expense added successfully.'}, status=status.HTTP_201_CREATED)

class UserExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        expense_splits = ExpenseSplit.objects.filter(user=user).select_related('expense')
        
        expenses = []
        for split in expense_splits:
            expenses.append({
                'description': split.expense.description,
                'total_amount': split.expense.total_amount,
                'amount_owed': split.amount_owed,
                'created_at': split.expense.created_at,
            })

        return JsonResponse({'expenses': expenses}, status=status.HTTP_200_OK)
    
class OverallExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        expenses = Expense.objects.all()
        response_data = []
        
        for expense in expenses:
            expense_data = {
                'description': expense.description,
                'total_amount': expense.total_amount,
                'creator': expense.creator.email,
                'created_at': expense.created_at,
                'splits': []
            }
            
            # Add the splits for each expense
            for split in expense.splits.all():
                expense_data['splits'].append({
                    'user': split.user.email,
                    'amount_owed': split.amount_owed
                })
                
            response_data.append(expense_data)

        return JsonResponse({'overall_expenses': response_data}, status=status.HTTP_200_OK)

class DownloadBalanceSheetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Fetch user's individual expense splits
        expense_splits = ExpenseSplit.objects.filter(user=user).select_related('expense')

        # Fetch overall expenses for all users
        overall_expenses = Expense.objects.all()

        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

        file_name = f'balance_sheet_{user.id}.pdf'  # Unique filename for each user
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        buffer = BytesIO()
        p = canvas.Canvas(file_path)  
        
        # Add header
        p.setFont("Helvetica", 16)
        p.drawString(100, 800, "Balance Sheet")
        p.setFont("Helvetica", 12)
        p.drawString(100, 780, f"User: {user.email}")
        p.drawString(100, 765, f"Name: {user.first_name} {user.last_name}")
        p.drawString(100, 750, "-----------------------------")

        y = 720  

        p.setFont("Helvetica", 14)
        p.drawString(100, y, "Individual Expenses")
        y -= 20
        
        p.setFont("Helvetica", 12)
        if not expense_splits:
            p.drawString(100, y, "No individual expenses recorded.")
            y -= 20
        else:
            for split in expense_splits:
                expense = split.expense
                p.drawString(100, y, f"Description: {expense.description}")
                p.drawString(100, y - 20, f"Total Amount: {expense.total_amount:.2f}")
                p.drawString(100, y - 40, f"Amount Owed: {split.amount_owed:.2f}")
                p.drawString(100, y - 60, "-----------------------------")
                y -= 80  

        p.setFont("Helvetica", 14)
        p.drawString(100, y, "Overall Expenses")
        y -= 20
        
        p.setFont("Helvetica", 12)
        if not overall_expenses:
            p.drawString(100, y, "No overall expenses recorded.")
            y -= 20
        else:
            for expense in overall_expenses:
                p.drawString(100, y, f"Description: {expense.description}")
                p.drawString(100, y - 20, f"Total Amount: {expense.total_amount:.2f}")
                p.drawString(100, y - 40, "-----------------------------")
                y -= 60  # Move down for the next overall expense

        # Summary Section
        p.setFont("Helvetica", 14)
        p.drawString(100, y, "Summary")
        y -= 20
        total_amount_owed = sum(split.amount_owed for split in expense_splits)
        total_expenses = sum(expense.total_amount for expense in overall_expenses)
        
        p.setFont("Helvetica", 12)
        p.drawString(100, y, f"Total Amount Owed: {total_amount_owed:.2f}")
        y -= 20
        p.drawString(100, y, f"Total Overall Expenses: {total_expenses:.2f}")

        p.showPage()
        p.save()

        # Upload the PDF to Cloudinary
        try:
            upload_response = cloudinary.uploader.upload(
                file_path, 
                resource_type="raw",  
                folder="balance_sheets",  
                public_id=f"balance_sheet_{user.id}",  
                api_key=config('CLOUDNARY_API_KEY'),
                api_secret=config('CLOUDNARY_API_SECRET'),
                cloud_name=config('CLOUDNARY_CLOUD_NAME'),
            )

            file_url = upload_response.get("url")

            # Delete the local PDF file after upload
            os.remove(file_path)

            return JsonResponse({'file_url': file_url}, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)