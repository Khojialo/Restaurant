from rest_framework import serializers
from .models import (
    Restaurant, Menu, Dish,
    Customer, Driver, Order, OrderItem,
    Payment, Delivery, Review
)



class ReviewMiniSerializer(serializers.ModelSerializer):
    """Restaurant ichida review larni soddalashtirilgan holda ko‘rsatish uchun"""
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'customer_name', 'created_at']

    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else None


class RestaurantSerializer(serializers.ModelSerializer):
    reviews = ReviewMiniSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = '__all__'
        depth = 1

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 2)
        return None


class MenuSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    restaurant_id = serializers.PrimaryKeyRelatedField(
        source="restaurant", queryset=Restaurant.objects.all(), write_only=True
    )

    class Meta:
        model = Menu
        fields = '__all__'


class DishSerializer(serializers.ModelSerializer):
    menu = MenuSerializer(read_only=True)
    menu_id = serializers.PrimaryKeyRelatedField(
        source="menu", queryset=Menu.objects.all(), write_only=True
    )

    class Meta:
        model = Dish
        fields = [
            'id', 'name', 'description', 'category', 'price',
            'is_available', 'prep_time_minutes', 'menu', 'menu_id'
        ]


class CustomerSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'full_name', 'email', 'phone', 'user', 'user_full_name',
            'created_at', 'updated_at',
        ]

    def get_user_full_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return None


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)
    dish_id = serializers.PrimaryKeyRelatedField(
        source="dish", queryset=Dish.objects.all(), write_only=True
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = '__all__'

    def get_total_price(self, obj):
        return obj.quantity * obj.dish.price if obj.dish else 0


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        source="customer", queryset=Customer.objects.all(), write_only=True
    )
    restaurant = RestaurantSerializer(read_only=True)
    restaurant_id = serializers.PrimaryKeyRelatedField(
        source="restaurant", queryset=Restaurant.objects.all(), write_only=True
    )
    driver = DriverSerializer(read_only=True)
    driver_id = serializers.PrimaryKeyRelatedField(
        source="driver", queryset=Driver.objects.all(), write_only=True
    )
    calculated_total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'
        depth = 1


    def get_calculated_total(self, obj):
        return sum(item.quantity * item.dish.price for item in obj.items.all())


class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        source="order", queryset=Order.objects.all(), write_only=True
    )
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = '__all__'

    def get_status_display(self, obj):
        return obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status


class DeliverySerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)
    driver_id = serializers.PrimaryKeyRelatedField(
        source="driver", queryset=Driver.objects.all(), write_only=True
    )
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        source="order", queryset=Order.objects.all(), write_only=True
    )

    class Meta:
        model = Delivery
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        source="customer", queryset=Customer.objects.all(), write_only=True
    )
    restaurant = RestaurantSerializer(read_only=True)
    restaurant_id = serializers.PrimaryKeyRelatedField(
        source="restaurant", queryset=Restaurant.objects.all(), write_only=True
    )

    class Meta:
        model = Review
        fields = '__all__'
