from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from restaurant.models import Restaurant, Menu, Dish
from restaurant.serializers import DishSerializer


class DishAPITestCase(APITestCase):

    def setUp(self):
        # Restoran va menyu yaratish
        self.restaurant = Restaurant.objects.create(
            name="FastFood King",
            description="Tasty burgers",
            address="123 Main St",
            phone="998901112233",
            email="fastfood@example.com",
        )
        self.menu = Menu.objects.create(
            name="Lunch Menu",
            description="Best lunch deals",
            restaurant=self.restaurant
        )

        # Taomlar yaratish
        self.dish1 = Dish.objects.create(
            name="Burger",
            description="Juicy beef burger",
            price=5.99,
            category="Fast Food",
            menu=self.menu
        )
        self.dish2 = Dish.objects.create(
            name="Fries",
            description="Crispy potato fries",
            price=2.99,
            category="Fast Food",
            menu=self.menu
        )

    def test_1_get_all_dishes(self):
        url = reverse('dish-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        print("✅ Barcha taomlar olindi:", response.data)

    def test_2_filter_dishes_by_name(self):
        url = reverse('dish-list')
        response = self.client.get(url, {'name': 'Burger'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        filtered_queryset = Dish.objects.filter(name="Burger")
        serializer = DishSerializer(filtered_queryset, many=True)
        self.assertEqual(response.data, serializer.data)
        print("✅ Name orqali filtrlangan taomlar:", response.data)

    def test_3_serializer_fields(self):
        serializer = DishSerializer(self.dish1)
        data = serializer.data
        self.assertIn('name', data)
        self.assertIn('price', data)
        self.assertIn('category', data)
        self.assertIn('menu', data)
        print("✅ Serializer fieldlari to‘g‘ri chiqdi:", data.keys())

    def test_4_search_dishes(self):
        url = reverse('dish-list')
        response = self.client.get(url, {'search': 'Fries'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Fries')
        print("✅ SearchFilter ishladi. Natija:", response.data)
