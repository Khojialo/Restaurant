from rest_framework import serializers
from .models import (
    Restaurant, Menu, Dish,
    Customer, Driver, Order, OrderItem,
    Payment, Delivery, Review
)


class RestaurantSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = '__all__'

    def get_average_rating(self, obj):
        reviews = obj.review_set.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 2)
        return None


class MenuSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = '__all__'

    def get_restaurant_name(self, obj):
        return obj.restaurant.name if obj.restaurant else None


class DishSerializer(serializers.ModelSerializer):
    menu_name = serializers.SerializerMethodField()
    restaurant_name = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = '__all__'

    def get_menu_name(self, obj):
        return obj.menu.name if obj.menu else None

    def get_restaurant_name(self, obj):
        return obj.menu.restaurant.name if obj.menu and obj.menu.restaurant else None


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = '__all__'

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class DriverSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = '__all__'

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    dish_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = '__all__'

    def get_total_price(self, obj):
        return obj.quantity * obj.dish.price if obj.dish else 0

    def get_dish_name(self, obj):
        return obj.dish.name if obj.dish else None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    calculated_total = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    restaurant_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_calculated_total(self, obj):
        return sum(item.quantity * item.dish.price for item in obj.items.all())

    def get_customer_name(self, obj):
        return obj.customer.name if obj.customer else None

    def get_restaurant_name(self, obj):
        return obj.restaurant.name if obj.restaurant else None


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = '__all__'

    def get_status_display(self, obj):
        return obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status


class DeliverySerializer(serializers.ModelSerializer):
    driver_name = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = '__all__'

    def get_driver_name(self, obj):
        return f"{obj.driver.first_name} {obj.driver.last_name}" if obj.driver else None


class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    restaurant_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'

    def get_customer_name(self, obj):
        return obj.customer.name if obj.customer else None

    def get_restaurant_name(self, obj):
        return obj.restaurant.name if obj.restaurant else None
