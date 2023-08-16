from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'accounts'

urlpatterns = [
    path('', views.index, name='registration'),

    # URL patterns for purchase requisitions
    path('purchase-requisitions/', views.purchase_requisition_list, name='purchase_requisition_list'),
    path('purchase-requisitions/<int:pk>/', views.purchase_requisition_detail, name='purchase_requisition_detail'),
    path('purchase-requisitions/remove-item/<int:pk>/', views.remove_purchase_item, name='remove_purchase_item'),

    # URL pattern for adding a new purchase item
    path('add-purchase-item/', views.add_purchase_item, name='add_purchase_item'),
    # New URL patterns for delete and print actions
    path('purchase-requisitions/remove/<int:pk>/', views.remove_purchase_requisition, name='remove_purchase_requisition'),
    path('purchase-requisitions/print/<int:pk>/', views.print_purchase_requisition, name='print_purchase_requisition'),
    path('get-units/', views.get_units, name='get_units'),
    path('login/', views.user_login, name='user_login'),
    path('user-logout/', views.user_logout, name='user_logout'), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
