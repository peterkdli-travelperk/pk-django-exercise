import tempfile
import os
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from recipe.models import Ingredient, Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_ingredient(name='Cinnamon'):
    return Ingredient.objects.create(name=name)


def sample_recipe(**params):
    defaults = {
        'name': 'Sample recipe',
        'description': 'Sample description',
    }
    defaults.update(params)
    return Recipe.objects.create(**defaults)


class RecipeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_recipes(self):
        sample_recipe()
        sample_recipe(name='A second sample recipe')

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(serializer.data))
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        recipe = sample_recipe()
        recipe.ingredients.add(sample_ingredient())

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        payload = {
            'name': 'Chocolate Cheesecake',
            'description': 'Cheese and chocolate, what more do you want?',
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objecgit cts.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_ingredients(self):
        ingredient1 = sample_ingredient(name='Prawns')
        ingredient2 = sample_ingredient(name='Ginger')
        payload = {
            'name': 'Pad Thai',
            'description': 'Some description',
            'ingredients': [ingredient1.id, ingredient2.id]
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        recipe = sample_recipe()
        new_ingredient = sample_ingredient(name='Orange')
        payload = {'name': 'Chicken Tikka', 'ingredients': [new_ingredient.id]}
        url = detail_url(recipe.id)

        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.name, payload['name'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 1)
        self.assertIn(new_ingredient, ingredients)

    def test_full_update_recipe(self):
        recipe = sample_recipe()
        recipe.tags.add(sample_ingredient())
        payload = {
            'title': 'Spaghetti Carbonara',
            'description': 'Spag and meatballs'
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.name, payload['name'])
        self.assertEqual(recipe.description, payload['description'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 0)
