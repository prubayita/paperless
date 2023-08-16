import base64
import os
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from .models import *
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import JsonResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO
import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from reportlab.lib.styles import getSampleStyleSheet
from accounts.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page or any other page you want
            return redirect('accounts:purchase_requisition_list')
        else:
            # Display an error message if login fails
            error_message = "Invalid username or password"
            return render(request, 'cre/login.html', {'error_message': error_message})

    return render(request, 'cre/login.html')
@login_required
def index(request):
    departments = Department.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        is_unit_manager = request.POST.get('is_unit_manager') == 'on'
        is_senior_manager = request.POST.get('is_senior_manager') == 'on'
        is_hod = request.POST.get('is_hod') == 'on'
        is_ceo = request.POST.get('is_ceo') == 'on'
        department_id = request.POST.get('department')
        
        # Decode the base64 signature data URL
        signature_data = request.POST.get('signature')
        signature_data = signature_data.split(',')[1]  # Split to remove data URL prefix
        signature_binary = base64.b64decode(signature_data)

        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_unit_manager=is_unit_manager,
            is_senior_manager=is_senior_manager,
            is_hod=is_hod,
            is_ceo=is_ceo,
            department_id=department_id,
            is_staff=True
        )

        if is_hod:
            department = Department.objects.get(id=department_id)
            department.hod = user
            department.save()
            
        if is_unit_manager:
                selected_unit_id = request.POST.get('unit')
                if selected_unit_id:
                    selected_unit = Unit.objects.filter(id=selected_unit_id, unit_manager__isnull=True).first()
                    if selected_unit:
                        selected_unit.unit_manager = user
                        selected_unit.save()
                        user.unit = selected_unit  # Set the unit for the user
                        user.save()  # Save the user to update the unit field

        # Save the signature image to the user's signature field
        user.signature.save(f'{username}_signature.png', ContentFile(signature_binary), save=True)

        return redirect('accounts:registration')

    return render(request, 'paperless/registration.html', {'departments': departments})
@login_required
def purchase_requisition_list(request):
    purchase_requisitions = PurchaseRequisition.objects.all()
    return render(request, 'paperless/purchase_requisition_list.html', {'purchase_requisitions': purchase_requisitions})
@login_required
def purchase_requisition_detail(request, pk):
    print(request.POST)  # Log the POST data
    purchase_requisition = get_object_or_404(PurchaseRequisition, pk=pk)
    departments = Department.objects.all()
    
    if request.method == 'POST':
        department_id = request.POST.get('department')
        print(f"Department ID from request: {department_id}")  # Added this line for debugging
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            department = None 
        else:
            purchase_requisition.department = department
            purchase_requisition.reason_for_request = request.POST.get('reason_for_request')

        try:
            total_amount = float(request.POST.get('total_amount', 0))
        except ValueError:
            total_amount = purchase_requisition.total_amount

        # Update existing purchase items
        with transaction.atomic():
            for item in purchase_requisition.items.all():
                item_name = request.POST.get(f'item_name_{item.id}')
                item_unit_price = request.POST.get(f'item_unit_price_{item.id}')
                item_quantity = request.POST.get(f'item_quantity_{item.id}')
                item.name = item_name

                try:
                    item.unit_price = float(item_unit_price) if item_unit_price else 0.0
                    item.quantity = int(item_quantity) if item_quantity else 0
                except ValueError:
                    pass

                if item_name:  # Check if name is provided
                    item.save()

            # Calculate and update total_amount after saving
            total_amount = sum(item.total_price for item in purchase_requisition.items.all())
            purchase_requisition.total_amount = total_amount
            purchase_requisition.save()

            return redirect('accounts:purchase_requisition_list')
        
    return render(request, 'paperless/purchase_requisition_detail.html', {'purchase_requisition': purchase_requisition, 'departments': departments})
@login_required
def add_purchase_item(request):
    if request.method == 'POST':
        purchase_requisition_id = request.POST.get('purchase_requisition_id')
        item_name = request.POST.get('item_name')
        item_unit_price = request.POST.get('item_unit_price')
        item_quantity = request.POST.get('item_quantity')

        try:
            purchase_requisition = PurchaseRequisition.objects.get(id=purchase_requisition_id)
            item_unit_price = float(item_unit_price) if item_unit_price else 0.0
            item_quantity = int(item_quantity) if item_quantity else 0

            new_item = PurchaseItem.objects.create(
                requisition=purchase_requisition,
                name=item_name,
                unit_price=item_unit_price,
                quantity=item_quantity,
                total_price=item_unit_price * item_quantity
            )

            # Update total_amount of the purchase requisition
            total_amount = sum(item.total_price for item in purchase_requisition.items.all())
            purchase_requisition.total_amount = total_amount
            purchase_requisition.save()

            return JsonResponse({'success': True, 'message': 'Item added successfully.'})
        except (PurchaseRequisition.DoesNotExist, ValueError) as e:
            return JsonResponse({'success': False, 'message': 'Failed to add item. Please try again.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})
@login_required
def remove_purchase_item(request, pk):
    item = get_object_or_404(PurchaseItem, pk=pk)
    requisition = item.requisition

    if request.method == 'POST':
        # Remove the purchase item and update the total_amount of the requisition
        item.delete()
        requisition.save()  # Update the total_amount field

    return redirect('accounts:purchase_requisition_detail', pk=requisition.pk)
@login_required
def remove_purchase_requisition(request, pk):
    requisition = get_object_or_404(PurchaseRequisition, pk=pk)
    requisition.delete()
    return redirect('accounts:purchase_requisition_list')
@login_required
def print_purchase_requisition(request, pk):
    requisition = get_object_or_404(PurchaseRequisition, pk=pk)
    user = requisition.user

    # Create a PDF buffer
    buffer = BytesIO()

    # Create a SimpleDocTemplate object
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Create a list to hold the Story elements
    story = []
    #My Logo
    logo_path = os.path.join(settings.STATIC_ROOT, 'assets/images/BSCLOGO1.png')
    logo = Image(logo_path, width=160, height=69)
    logo.hAlign = "RIGHT"
    story.append(logo)
    story.append(Spacer(1, 20))
    # Set title style
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_text = "PURCHASE REQUISITION FORM"
    title = Paragraph(title_text, title_style)
    story.append(title)

    # Add a space
    story.append(Spacer(1, 20))

    # Add User's name and signature
    user_name = user.username
    user_text = f"Requested by: {user_name}"
    user_signature = Image(os.path.join(settings.MEDIA_ROOT, str(requisition.user.signature)), width=100, height=50)  # Adjust width and height as needed
    user_table = Table([[Paragraph(user_text, styles["Heading2"]), user_signature]])
    user_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (0, 0), 10),
        ('BOTTOMPADDING', (1, 0), (1, 0), 10),
        ('TOPPADDING', (1, 0), (1, 0), 10),
        ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
    ]))
    story.append(user_table)

    # Add Head of Department name and signature
    hod_name = requisition.department.hod.username if requisition.department.hod else "Not Assigned"
    hod_text = f"Head of Department: {hod_name}"
    hod_signature = Image(os.path.join(settings.MEDIA_ROOT, str(requisition.department.hod.signature)), width=100, height=50) if requisition.department.hod else None
    hod_table = Table([[Paragraph(hod_text, styles["Heading2"]), hod_signature]])
    hod_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (0, 0), 10),
        ('BOTTOMPADDING', (1, 0), (1, 0), 10),
        ('TOPPADDING', (1, 0), (1, 0), 10),
        ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
    ]))
    story.append(hod_table)

    # Add Unit Manager name and signature
    unit_manager = requisition.unit.unit_manager.username if requisition.unit.unit_manager else "Not Assigned"
    unit_manager_text = f"Unit Manager: {unit_manager}"
    unit_manager_signature = Image(os.path.join(settings.MEDIA_ROOT, str(requisition.unit.unit_manager.signature)), width=100, height=50) if requisition.unit.unit_manager else None
    unit_manager_table = Table([[Paragraph(unit_manager_text, styles["Heading2"]), unit_manager_signature]])
    unit_manager_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (0, 0), 10),
        ('BOTTOMPADDING', (1, 0), (1, 0), 10),
        ('TOPPADDING', (1, 0), (1, 0), 10),
        ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
    ]))
    story.append(unit_manager_table)
    # Create a data table for purchase requisition items
    currency_symbol = "$" if requisition.currency == "USD" else "RWF"  # Adjust symbols as needed
    data = [['Item', 'Unit Price', 'Quantity', 'Total Price']]
    for item in requisition.items.all():
        data.append([item.name, f"{currency_symbol}{item.unit_price:.2f}", item.quantity, f"{currency_symbol}{item.total_price:.2f}"])  # Format amounts with currency symbol

    table = Table(data, colWidths=[200, 80, 80, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)

    story.append(Spacer(1, 20))

    # Add Reason for Request
    reason_text = f"Reason for Request: {requisition.reason_for_request}"
    reason = Paragraph(reason_text, styles["Normal"])
    story.append(reason)

    story.append(Spacer(1, 10))

    # Add Total Amount
    currency_symbol = "$" if requisition.currency == "USD" else "RWF"
    total_amount_text = f"Total Amount: {currency_symbol} {requisition.total_amount}"
    total_amount = Paragraph(total_amount_text, styles["Normal"])
    story.append(total_amount)

    story.append(Spacer(1, 20))

    # Add Signature
    user_text2 = f"Signed by: {user_name}"
    user2 = Paragraph(user_text2, styles["Normal"])
    story.append(user2)
   # Load user's signature image
    signature_path = os.path.join(settings.MEDIA_ROOT, str(requisition.user.signature))
    signature_image = Image(signature_path, width=200, height=100)
    signature_image.hAlign = "LEFT"

    # Add user's signature to the PDF
    story.append(signature_image)
    # Close the PDF object
    doc.build(story)

    # File response
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=PurchaseRequisition_{requisition.id}.pdf'
    return response

def get_units(request):
    department_id = request.GET.get('department_id')
    units = Unit.objects.filter(department_id=department_id).values('id', 'name')
    return JsonResponse({'units': list(units)})

def user_logout(request):
    logout(request)
    # Redirect to the login page or any other page you want
    return redirect('accounts:user_login')

