from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

User = get_user_model()

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('professional', 'Professional Wear'),
        ('party', 'Party Wear'),
        ('classic', 'Classic Wear'),
        ('street', 'Street Wear'),
        ('daily', 'Daily Wear'),
        ('traditional', 'Traditional Wear'),
    ]
    
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.get_name_display()

class Product(models.Model):
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Stock management
    stock = models.PositiveIntegerField(default=0)
    sold = models.PositiveIntegerField(default=0)
    
    # Product details
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    material = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    
    # Product images
    # image = models.ImageField(upload_to='products/', null=True, blank=True)
    # image2 = models.ImageField(upload_to='products/', null=True, blank=True)
    # image3 = models.ImageField(upload_to='products/', null=True, blank=True)
    image = models.URLField(max_length=500)
    image2 = models.URLField(max_length=500, blank=True, null=True)
    image3 = models.URLField(max_length=500, blank=True, null=True)

    # Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def in_stock(self):
        return self.stock > 0

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating} stars"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product average rating
        self.update_product_rating()
    
    def update_product_rating(self):
        product = self.product
        reviews = product.reviews.all()
        total_rating = sum([review.rating for review in reviews])
        product.total_reviews = reviews.count()
        product.average_rating = total_rating / product.total_reviews if product.total_reviews > 0 else 0
        product.save()

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'favorites'
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"