from django.urls import path
from . import views

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    
    # Product URLs
    path('', views.ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('create/', views.create_product_view, name='product-create'),
    path('update/<int:pk>/', views.update_product_view, name='product-update'),
    path('delete/<int:pk>/', views.delete_product_view, name='product-delete'),
    
    # Admin URLs
    path('admin/all/', views.admin_products_view, name='admin-products'),
    path('admin/stats/', views.product_stats_view, name='product-stats'),
    
    # Review URLs
    path('<int:product_id>/reviews/', views.product_reviews_view, name='product-reviews'),
    path('<int:product_id>/reviews/create/', views.create_review_view, name='create-review'),
    path('reviews/<int:review_id>/delete/', views.delete_review_view, name='delete-review'),
    
    # Favorite URLs
    path('favorites/', views.favorites_list_view, name='favorites-list'),
    path('favorites/<int:product_id>/add/', views.add_to_favorites_view, name='add-favorite'),
    path('favorites/<int:product_id>/remove/', views.remove_from_favorites_view, name='remove-favorite'),
    path('favorites/<int:product_id>/check/', views.check_favorite_view, name='check-favorite'),
]