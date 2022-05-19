import tempfile
import os
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from recipe.models import Ingredient, Recipe
from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_ingredient(name='Cinnamon'):
    return Ingredient.objects.create(name=name, recipe=sample_recipe())


def sample_recipe(**params):
    defaults = {
        'name': 'Sample recipe',
        'description': 'Sample description',
    }
    defaults.update(params)
    return Recipe.objects.create(name='Sample Name', description='sample description')


class RecipeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_recipes(self):
        Recipe.objects.create(name='Sample Name', description='sample description')

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(serializer.data))
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        recipe = sample_recipe()
        ingredient1 = sample_ingredient(name='Cheese')
        ingredient2 = sample_ingredient(name='milk')

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        payload = {
            'name': 'Chocolate Cheesecake',
            'description': 'Cheese and chocolate, what more do you want?',
        }

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_ingredients(self):
        ingredient1 = Ingredient(name='Prawns')
        ingredient2 = Ingredient(name='Ginger')
        payload = {
            'name': 'Pad Thai',
            'description': 'Thai deliciousness',
            'ingredients': [
                {'name': ingredient1.name},
                {'name': ingredient2.name}
            ]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        for ingredient in ingredients:
            self.assertIn(ingredient.name, [ingredient1.name, ingredient2.name])

    def test_partial_update_recipe(self):
        recipe = sample_recipe()
        payload = {'name': 'Chicken Tikka', 'description': 'some new description'}
        url = detail_url(recipe.id)

        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.name, payload['name'])
        self.assertEqual(recipe.description, payload['description'])

    def test_add_ingredients_to_existing_recipe(self):
        ingredient1 = Ingredient(name='Prawns')
        ingredient2 = Ingredient(name='Ginger')
        recipe = sample_recipe()
        payload = {
            'ingredients': [
                {'name': ingredient1.name},
                {'name': ingredient2.name}
            ]
        }
        url = detail_url(recipe.id)

        res = self.client.patch(url, payload, format='json')

        recipe.refresh_from_db()

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        print(recipe)
        self.assertEqual(ingredients.count(), 2)
        for ingredient in ingredients:
            self.assertIn(ingredient.name, [ingredient1.name, ingredient2.name])

    def test_full_update_recipe(self):
        ingredient1 = Ingredient(name='Prawns')
        ingredient2 = Ingredient(name='Ginger')
        recipe = sample_recipe()
        payload = {
            'name': 'Spaghetti Carbonara',
            'description': 'Spag and meatballs',
            'ingredients': [
                {'name': ingredient1.name},
                {'name': ingredient2.name}
            ]
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, payload['name'])
        self.assertEqual(recipe.description, payload['description'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 0)
