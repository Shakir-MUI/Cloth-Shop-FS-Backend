from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from .models import Cart, Order, OrderItem
from products.models import Product
from .serializers import CartSerializer, OrderSerializer, CreateOrderSerializer

# Cart Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_list_view(request):
    """
    Get user's cart items
    """
    cart_items = Cart.objects.filter(user=request.user)
    serializer = CartSerializer(cart_items, many=True)
    
    # Calculate total
    total = sum([item.subtotal for item in cart_items])
    
    return Response({
        'cart_items': serializer.data,
        'total': total,
        'count': cart_items.count()
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart_view(request):
    """
    Add product to cart
    """
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    
    try:
        product = Product.objects.get(pk=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check stock availability
    if product.stock < int(quantity):
        return Response({
            'error': f'Only {product.stock} items available in stock'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Add or update cart item
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += int(quantity)
        if cart_item.quantity > product.stock:
            return Response({
                'error': f'Only {product.stock} items available in stock'
            }, status=status.HTTP_400_BAD_REQUEST)
        cart_item.save()
    
    serializer = CartSerializer(cart_item)
    message = 'Product added to cart' if created else 'Cart updated'
    
    return Response({
        'message': message,
        'cart_item': serializer.data
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_view(request, cart_id):
    """
    Update cart item quantity
    """
    try:
        cart_item = Cart.objects.get(pk=cart_id, user=request.user)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    quantity = request.data.get('quantity')
    
    if int(quantity) <= 0:
        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)
    
    if int(quantity) > cart_item.product.stock:
        return Response({
            'error': f'Only {cart_item.product.stock} items available in stock'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    cart_item.quantity = quantity
    cart_item.save()
    
    serializer = CartSerializer(cart_item)
    return Response({
        'message': 'Cart updated successfully',
        'cart_item': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart_view(request, cart_id):
    """
    Remove item from cart
    """
    try:
        cart_item = Cart.objects.get(pk=cart_id, user=request.user)
        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart_view(request):
    """
    Clear all items from cart
    """
    Cart.objects.filter(user=request.user).delete()
    return Response({'message': 'Cart cleared successfully'}, status=status.HTTP_200_OK)

# Order Views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_view(request):
    """
    Create order from cart
    """
    serializer = CreateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Get cart items
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            # Calculate total
            total_amount = sum([item.subtotal for item in cart_items])
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                full_name=serializer.validated_data['full_name'],
                email=serializer.validated_data['email'],
                phone=serializer.validated_data['phone'],
                address=serializer.validated_data['address'],
                city=serializer.validated_data['city'],
                state=serializer.validated_data['state'],
                pincode=serializer.validated_data['pincode'],
                total_amount=total_amount,
                payment_method=serializer.validated_data['payment_method'],
                transaction_id=serializer.validated_data.get('transaction_id', ''),
                payment_status='paid' if serializer.validated_data['payment_method'] != 'cod' else 'pending'
            )
            
            # Create order items and update product stock
            for cart_item in cart_items:
                product = cart_item.product
                
                # Check stock
                if product.stock < cart_item.quantity:
                    raise Exception(f'Insufficient stock for {product.name}')
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_price=product.price,
                    quantity=cart_item.quantity,
                    subtotal=cart_item.subtotal
                )
                
                # Update product stock and sold count
                product.stock -= cart_item.quantity
                product.sold += cart_item.quantity
                product.save()
            
            # Clear cart
            cart_items.delete()
            
            order_serializer = OrderSerializer(order)
            return Response({
                'message': 'Order created successfully',
                'order': order_serializer.data
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orders_list_view(request):
    """
    Get user's orders
    """
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail_view(request, order_id):
    """
    Get order details
    """
    try:
        order = Order.objects.get(pk=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_order_view(request, order_id):
    """
    Cancel order
    """
    try:
        order = Order.objects.get(pk=order_id, user=request.user)
        
        if order.order_status in ['delivered', 'cancelled']:
            return Response({
                'error': 'Cannot cancel this order'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.order_status = 'cancelled'
        order.save()
        
        # Restore product stock
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.sold -= item.quantity
                item.product.save()
        
        return Response({'message': 'Order cancelled successfully'}, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

# Admin Order Views
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_orders_view(request):
    """
    Get all orders (Admin only)
    """
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_order_status_view(request, order_id):
    """
    Update order status (Admin only)
    """
    try:
        order = Order.objects.get(pk=order_id)
        order_status = request.data.get('order_status')
        
        if order_status not in dict(Order.ORDER_STATUS):
            return Response({'error': 'Invalid order status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.order_status = order_status
        order.save()
        
        serializer = OrderSerializer(order)
        return Response({
            'message': 'Order status updated successfully',
            'order': serializer.data
        }, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)