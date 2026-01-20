from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Category, Product, Review, Favorite
from .serializers import (
    CategorySerializer, ProductSerializer, ProductListSerializer,
    ReviewSerializer, FavoriteSerializer
)

# Category Views 
class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

# Product Views
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'size', 'color']
    search_fields = ['name', 'description', 'brand']
    ordering_fields = ['price', 'created_at', 'average_rating']
    ordering = ['-created_at']

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_product_view(request):
    """
    Create a new product (Admin only)
    """
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Product created successfully',
            'product': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def update_product_view(request, pk):
    """
    Update a product (Admin only)
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Product updated successfully',
            'product': serializer.data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_product_view(request, pk):
    """
    Delete a product (Admin only)
    """
    try:
        product = Product.objects.get(pk=pk)
        product.is_active = False
        product.save()
        return Response({
            'message': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_products_view(request):
    """
    Get all products including inactive (Admin only)
    """
    products = Product.objects.all().order_by('-created_at')
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def product_stats_view(request):
    """
    Get product statistics (Admin only)
    """
    products = Product.objects.all()
    total_products = products.count()
    total_stock = sum([p.stock for p in products])
    total_sold = sum([p.sold for p in products])
    out_of_stock = products.filter(stock=0).count()
    
    return Response({
        'total_products': total_products,
        'total_stock': total_stock,
        'total_sold': total_sold,
        'out_of_stock': out_of_stock
    }, status=status.HTTP_200_OK)

# Review Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review_view(request, product_id):
    """
    Create or update a review for a product
    """
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user already reviewed this product
    review, created = Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            'rating': request.data.get('rating'),
            'comment': request.data.get('comment', '')
        }
    )
    
    serializer = ReviewSerializer(review)
    message = 'Review created successfully' if created else 'Review updated successfully'
    
    return Response({
        'message': message,
        'review': serializer.data
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def product_reviews_view(request, product_id):
    """
    Get all reviews for a product
    """
    reviews = Review.objects.filter(product_id=product_id).order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review_view(request, review_id):
    """
    Delete a review
    """
    try:
        review = Review.objects.get(pk=review_id, user=request.user)
        review.delete()
        return Response({'message': 'Review deleted successfully'}, status=status.HTTP_200_OK)
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

# Favorite Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorites_list_view(request):
    """
    Get user's favorite products
    """
    favorites = Favorite.objects.filter(user=request.user)
    serializer = FavoriteSerializer(favorites, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_favorites_view(request, product_id):
    """
    Add product to favorites
    """
    try:
        product = Product.objects.get(pk=product_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        
        if created:
            return Response({
                'message': 'Product added to favorites',
                'favorite': FavoriteSerializer(favorite).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Product already in favorites'
            }, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_favorites_view(request, product_id):
    """
    Remove product from favorites
    """
    try:
        favorite = Favorite.objects.get(user=request.user, product_id=product_id)
        favorite.delete()
        return Response({'message': 'Product removed from favorites'}, status=status.HTTP_200_OK)
    except Favorite.DoesNotExist:
        return Response({'error': 'Favorite not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_favorite_view(request, product_id):
    """
    Check if product is in user's favorites
    """
    is_favorite = Favorite.objects.filter(user=request.user, product_id=product_id).exists()
    return Response({'is_favorite': is_favorite}, status=status.HTTP_200_OK)