from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Restaurant(models.Model):
    name = models.CharField(max_length=255, verbose_name="Restoran nomi")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    address = models.TextField(verbose_name="Manzil")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Telefon raqam")
    email = models.EmailField(unique=True, verbose_name="Email")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        verbose_name = "Restoran"
        verbose_name_plural = "Restoranlar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(max_length=255, verbose_name="Menyu nomi")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi?")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus', verbose_name="Restoran")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        verbose_name = "Menyu"
        verbose_name_plural = "Menyular"
        ordering = ["name"]

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"


class Dish(models.Model):
    name = models.CharField(max_length=255, verbose_name="Taom nomi")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kategoriya")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")
    is_available = models.BooleanField(default=True, verbose_name="Mavjudmi?")
    prep_time_minutes = models.PositiveIntegerField(default=10, verbose_name="Tayyorlanish vaqti (daqiqa)")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='dishes', verbose_name="Menyu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        verbose_name = "Taom"
        verbose_name_plural = "Taomlar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Customer(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="To‘liq ism")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Telefon raqam")
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='customer_profile', null=True, blank=True,
        verbose_name="Foydalanuvchi"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Driver(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="Haydovchi ismi")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Telefon raqam")
    vehicle_info = models.CharField(max_length=255, verbose_name="Transport ma’lumotlari")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi?")
    is_online = models.BooleanField(default=False, verbose_name="Onlaynmi?")
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Reyting"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        verbose_name = "Haydovchi"
        verbose_name_plural = "Haydovchilar"
        ordering = ["-rating"]

    def __str__(self):
        return self.full_name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('preparing', 'Tayyorlanmoqda'),
        ('delivering', 'Yetkazilmoqda'),
        ('completed', 'Yakunlangan'),
        ('cancelled', 'Bekor qilingan'),
    ]

    delivery_address = models.TextField(verbose_name="Yetkazib berish manzili")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Umumiy summa")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holati")
    placed_at = models.DateTimeField(auto_now_add=True, verbose_name="Buyurtma vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")
    estimated_delivery_time = models.DateTimeField(blank=True, null=True, verbose_name="Taxminiy yetkazish vaqti")
    notes = models.TextField(blank=True, null=True, verbose_name="Izoh")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', verbose_name="Mijoz")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders', verbose_name="Restoran")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name="Haydovchi")

    @property
    def calculated_total(self):
        return sum(item.total_price for item in self.items.all())

    def save(self, *args, **kwargs):
        self.total_amount = self.calculated_total
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-placed_at"]

    def __str__(self):
        return f"Buyurtma #{self.id} - {self.customer.full_name}"


class OrderItem(models.Model):
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miqdor")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bir dona narxi")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Buyurtma")
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name="Taom")

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    class Meta:
        verbose_name = "Buyurtma elementi"
        verbose_name_plural = "Buyurtma elementlari"

    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Naqd'),
        ('card', 'Karta'),
        ('online', 'Onlayn'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('paid', 'To‘langan'),
        ('failed', 'Xatolik'),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="To‘lov summasi")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="To‘lov turi")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holati")
    transaction_reference = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tranzaksiya raqami")
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="To‘langan vaqt")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', verbose_name="Buyurtma")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    class Meta:
        verbose_name = "To‘lov"
        verbose_name_plural = "To‘lovlar"
        ordering = ["-paid_at"]

    def __str__(self):
        return f"To‘lov #{self.id} (Buyurtma {self.order.id})"


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Biriktirilgan'),
        ('picked_up', 'Olingan'),
        ('delivered', 'Yetkazilgan'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned', verbose_name="Holati")
    pickup_at = models.DateTimeField(blank=True, null=True, verbose_name="Olish vaqti")
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name="Yetkazilgan vaqt")
    estimated_time = models.DurationField(blank=True, null=True, verbose_name="Taxminiy vaqt")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery', verbose_name="Buyurtma")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries', verbose_name="Haydovchi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        verbose_name = "Yetkazib berish"
        verbose_name_plural = "Yetkazib berishlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Yetkazib berish #{self.id}"


class Review(models.Model):
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Baholash (1–5)"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="Izoh")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews', verbose_name="Mijoz")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True, verbose_name="Restoran")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews', verbose_name="Haydovchi")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews', verbose_name="Buyurtma")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.full_name} - {self.rating}/5"
