from django.test import TestCase

from django.urls import reverse
from rest_framework import status

from recipe.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer
from rest_framework.test import APIClient


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class IngredientsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_ingredient_list(self):
        Ingredient.objects.create(name='Kale')
        Ingredient.objects.create(name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_ingredient_successful(self):
        payload = {'name': 'cabbage'}

        self.client.post(INGREDIENTS_URL, payload)
        exists = Ingredient.objects.filter(
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        payload = {'name': ''}

        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

