from django.urls import path
from . import views

urlpatterns = [
    # Cart URLs
    path('cart/', views.cart_list_view, name='cart-list'),
    path('cart/add/', views.add_to_cart_view, name='add-to-cart'),
    path('cart/<int:cart_id>/update/', views.update_cart_view, name='update-cart'),
    path('cart/<int:cart_id>/remove/', views.remove_from_cart_view, name='remove-from-cart'),
    path('cart/clear/', views.clear_cart_view, name='clear-cart'),
    
    # Order URLs
    path('', views.orders_list_view, name='orders-list'),
    path('create/', views.create_order_view, name='create-order'),
    path('<int:order_id>/', views.order_detail_view, name='order-detail'),
    path('<int:order_id>/cancel/', views.cancel_order_view, name='cancel-order'),
    
    # Admin Order URLs
    path('admin/all/', views.admin_orders_view, name='admin-orders'),
    path('admin/<int:order_id>/update/', views.update_order_status_view, name='update-order-status'),
]