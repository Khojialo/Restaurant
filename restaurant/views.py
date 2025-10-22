from rest_framework import viewsets, permissions,filters
from django_filters.rest_framework import DjangoFilterBackend



from .models import (
    Restaurant, Menu, Dish,
    Customer, Driver, Order, OrderItem,
    Payment, Delivery, Review
)
from .serializers import (
    RestaurantSerializer, MenuSerializer, DishSerializer,
    CustomerSerializer, DriverSerializer, OrderSerializer,
    OrderItemSerializer, PaymentSerializer, DeliverySerializer, ReviewSerializer
)


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name', 'address', 'phone']
    ordering_fields = ['name', 'created_at']
    permission_classes = [permissions.AllowAny]


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'restaurant__name']
    permission_classes = [permissions.AllowAny]


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name', 'category', 'menu__restaurant__name']
    ordering_fields = ['price', 'name']
    permission_classes = [permissions.AllowAny]


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['rating']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('customer', 'restaurant', 'driver')
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer__full_name', 'restaurant__name']
    ordering_fields = ['placed_at', 'status']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        if hasattr(user, 'customer_profile'):
            return self.queryset.filter(customer=user.customer_profile)
        return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'customer_profile'):
            serializer.save(customer=user.customer_profile)
        else:
            serializer.save()


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['paid_at', 'amount']
    permission_classes = [permissions.IsAuthenticated]


class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['status', 'created_at']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related('customer', 'restaurant', 'driver')
    serializer_class = ReviewSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['customer__full_name', 'restaurant__name', 'driver__full_name']
    ordering_fields = ['rating', 'created_at']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        if hasattr(user, 'customer_profile'):
            return self.queryset.filter(customer=user.customer_profile)
        return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'customer_profile'):
            serializer.save(customer=user.customer_profile)
        else:
            serializer.save()
