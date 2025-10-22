from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from restaurant.models import Restaurant,Menu,Dish
from restaurant.serializers import RestaurantSerializer


class RestaurantAPITestCase(APITestCase):

    def setUp(self):
        self.restaurant1 = Restaurant.objects.create(
            name="FastFood King",
            description="Tasty burgers",
            address="123 Main St",
            phone="998901112233",
            email="fastfood@example.com",
        )
        self.restaurant2 = Restaurant.objects.create(
            name="Sushi Place",
            description="Fresh sushi",
            address="Tashkent City",
            phone="998907778899",
            email="sushi@example.com",
        )

    def test_1_get_all_restaurants(self):
        url = reverse('restaurant-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        print("✅ Barcha restoranlar olindi:", response.data)

    def test_2_filter_restaurants(self):
        url = reverse('restaurant-list')
        response = self.client.get(url, {'name': 'Sushi Place'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        filtered_queryset = Restaurant.objects.filter(name="Sushi Place")
        serializer = RestaurantSerializer(filtered_queryset, many=True)

        self.assertEqual(response.data,serializer.data)
        print("✅ Name orqali filtrlangan restoranlar:", response.data)

    def test_3_serializer_fields(self):
        serializer = RestaurantSerializer(self.restaurant1)
        data = serializer.data
        self.assertIn('average_rating', data)
        self.assertIn('likes_data', data)
        self.assertIn('reviews', data)
        print("✅ Serializer fieldlari to‘g‘ri chiqdi:", data.keys())

    def test_4_search_restaurants(self):
        url = reverse('restaurant-list')
        response = self.client.get(url, {'search': 'Sushi'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Sushi Place')
        print("✅ SearchFilter ishladi. Natija:", response.data)
