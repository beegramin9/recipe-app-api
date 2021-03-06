from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse("recipe:ingredient-list")


class PublicIngredientApiTests(TestCase):
    """ Test the publicy available ingredients API """
    
    def setUp(self):
        self.client = APIClient()

    def test_login_always_required(self):
        """ Test that login is always required to access the endpoint """
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """ Test the private ingredients API """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """ Test retrieving a list of ingredients """
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        # DB에서 받아오는거기때문에 serializing 필요
        serializer = IngredientSerializer(ingredients, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Test that only ingredients for the authenticated user are returned """
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'testpass'
        )
        Ingredient.objects.create(user=user2, name='Vinegar')

        ingredient = Ingredient.objects.create(user=self.user, name='Tumeric')
        
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    # Create 기능 추가(Viewset에 CreateModelMixin 추가 필요)
    # Viewset에 Create 기능을 추가하지 않으면 
    # exists는 False가 나오고
    def test_create_ingredient_successful(self):
        """ Test create a new ingredient """
        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    # 여기는 method not allowed인 405가 나온다
    def test_create_ingredient_invalid(self):
        """ Test creating invalid ingredient fails """
        payload = {'name':''}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
