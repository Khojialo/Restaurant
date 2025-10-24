import json
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import connection

from restaurant.models import Restaurant, Menu, Dish
from restaurant.serializers import RestaurantSerializer


class RestaurantAPITestCase(APITestCase):

    def setUp(self):
        super().setUp()
        Restaurant.objects.all().delete()
        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE restaurant_restaurant_id_seq RESTART WITH 1;")
        # user = User.objects.create(username='ali')
        # self.client.force_login(user)
        self.user = User.objects.create_user(username='ali', password='ali12345@')
        token_url = reverse('login')
        responce = self.client.post(token_url, data={'username': 'ali', 'password': 'ali12345@'})
        token = responce.data['auth_token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

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

        self.list_url = reverse('restaurant-list')

    def test_create_restaurant(self):
        data = {
            "name": "New Cafe",
            "description": "Coffee and snacks",
            "address": "456 Elm St",
            "phone": "998909999999",
            "email": "newcafe@example.com"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Restaurant.objects.count(), 3)
        new_restaurant = Restaurant.objects.order_by('-created_at').first()
        self.assertEqual(new_restaurant.name, "New Cafe")
        print("✅ Yangi restoran muvaffaqiyatli yaratildi:", response.data)

    def test_update_restaurant_put(self):
        url = reverse('restaurant-detail', args=[self.restaurant1.id])
        data = {
            "name": "Tokio Food",
            "description": "the best",
            "address": "New Address 123",
            "phone": "998901234567",
            "email": "updated@example.com",
            "is_active": True
        }

        response = self.client.put(url, data=json.dumps(data), content_type='application/json'
                                   )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.restaurant1.refresh_from_db()
        self.assertEqual(self.restaurant1.name, "Tokio Food")
        self.assertEqual(self.restaurant1.address, "New Address 123")
        print("✅ Restoran PUT orqali muvaffaqiyatli yangilandi:", response.data)
        print(json.dumps(response.data, indent=4, ensure_ascii=False))

    def test_update_restaurant_patch(self):
        url = reverse('restaurant-detail', args=[self.restaurant1.id])
        data = {
            "name": "Tokio London",
            "address": "Partial Update 999"
        }

        response = self.client.patch(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.restaurant1.refresh_from_db()
        self.assertEqual(self.restaurant1.name, "Tokio London")
        self.assertEqual(self.restaurant1.address, "Partial Update 999")
        print("✅ Restoran PATCH orqali qisman muvaffaqiyatli yangilandi:", response.data)
        print(json.dumps(response.data, indent=4, ensure_ascii=False))

    def test_get_restaurant_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        print("✅ API orqali olingan fieldlari to‘g‘ri chiqdi:", response.data)

    def test_get_restaurant_detail(self):
        url = reverse('restaurant-detail', args=[self.restaurant1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.restaurant1.name)
        print("✅ API orqali olingan fieldlari to‘g‘ri chiqdi:", response.data)

    def test_delete_restaurant(self):
        url = reverse('restaurant-detail', args=[self.restaurant1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        exists = Restaurant.objects.filter(id=self.restaurant1.id).exists()
        self.assertFalse(exists)

        print(f"✅ Restoran ID={self.restaurant1.id} muvaffaqiyatli o‘chirildi.")

    def test_1_get_all_restaurants(self):
        url = reverse('restaurant-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        print("✅ Barcha restoranlar olindi:", response.data)

    def test_get_order(self):
        url = reverse('restaurant-list')
        serializer = RestaurantSerializer([self.restaurant1,self.restaurant2], many=True)
        responce = self.client.get(url, data={'ordering': 'address'})
        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertEqual(responce.data, serializer.data)
        print("✅ API orqali olingan fieldlari to‘g‘ri chiqdi:", responce.data)
        print("✅ Serializer fieldlari to‘g‘ri chiqdi:", serializer.data[0].keys())

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
