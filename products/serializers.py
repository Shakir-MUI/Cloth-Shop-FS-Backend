from rest_framework import serializers
from .models import Category, Product, Review, Favorite
from django.contrib.auth import get_user_model

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="get_name_display", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "display_name", "description", "created_at"]


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "user",
            "user_name",
            "user_email",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.get_name_display", read_only=True
    )
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "category",
            "category_name",
            "stock",
            "sold",
            "size",
            "color",
            "material",
            "brand",
            "image",
            "image2",
            "image3",
            "average_rating",
            "total_reviews",
            "reviews",
            "in_stock",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "sold",
            "average_rating",
            "total_reviews",
            "created_at",
            "updated_at",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.get_name_display", read_only=True
    )
    category_code = serializers.CharField(source="category.name", read_only=True)

    display_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "category",
            "category_name",
            "category_code",
            "size",
            "color",
            "brand",
            "display_image",
            "average_rating",
            "total_reviews",
            "in_stock",
        ]

    def get_display_image(self, obj):
        if obj.image:
            return obj.image.url
        if obj.image2:
            return obj.image2.url
        if obj.image3:
            return obj.image3.url
        return None


class FavoriteSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source="product", read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "user", "product", "product_details", "created_at"]
        read_only_fields = ["id", "user", "created_at"]
