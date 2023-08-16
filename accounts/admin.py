from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_staff',
        'is_unit_manager', 'is_senior_manager', 'is_hod', 'is_ceo', 'signature', 'department', 'unit'
    )

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('is_unit_manager', 'is_senior_manager', 'is_hod', 'is_ceo', 'signature', 'department', 'unit')
        })
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Additional info', {
            'fields': ('is_unit_manager', 'is_senior_manager', 'is_hod', 'is_ceo', 'signature', 'department', 'unit')
        })
    )

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'hod')

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1

class PurchaseRequisitionAdmin(admin.ModelAdmin):
    inlines = [PurchaseItemInline]
    list_display = ['user', 'reason_for_request', 'total_amount', 'currency', 'department', 'unit']
    list_filter = ('department', 'unit')
    search_fields = ['user__username', 'department__name', 'unit__name']


    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        instance = form.instance
        total_amount = sum(item.total_price for item in instance.items.all())
        if instance.total_amount != total_amount:
            instance.total_amount = total_amount
            instance.save()

class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ('requisition', 'name', 'unit_price', 'quantity', 'total_price')
    
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'unit_manager')  # Include 'unit_manager'
    fields = ('name', 'department', 'unit_manager')  # Include 'unit_manager' here too



# Register your models and admin classes
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(PurchaseRequisition, PurchaseRequisitionAdmin)
admin.site.register(PurchaseItem, PurchaseItemAdmin)
admin.site.register(Unit, UnitAdmin)