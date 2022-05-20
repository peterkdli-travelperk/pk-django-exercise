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
    return Ingredient.objects.create(name=name, recipe=create_sample_recipe())


def create_sample_recipe(**params):
    defaults = {
        'name': 'Sample recipe',
        'description': 'Sample description'
    }
    defaults.update(params)
    return Recipe.objects.create(**defaults)


class RecipeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_recipes(self):
        test_name = 'Pasta Bake'
        test_description = 'Baked goodness'
        create_sample_recipe(name=test_name, description=test_description)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), len(serializer.data))
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data[0]['name'], test_name)
        self.assertEqual(res.data[0]['description'], test_description)

    def test_view_recipe_detail(self):
        recipe = create_sample_recipe()

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail_invalid_id(self):
        recipe = create_sample_recipe()

        url = detail_url(recipe.id * 20)
        res = self.client.get(url)

        serializer = RecipeSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


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

        ingredient_name = 'Prawns'
        ingredient1 = Ingredient(name=ingredient_name)
        ingredient2 = Ingredient(name='Ginger')
        recipe = create_sample_recipe()
        recipe.ingredients.add(sample_ingredient(name=ingredient_name))

        payload = {
            'name': 'Chicken Tikka',
            'description': 'some new description',
        }
        url = detail_url(recipe.id)

        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.name, payload['name'])
        self.assertEqual(recipe.description, payload['description'])
        self.assertEqual(recipe.ingredients.first().name, ingredient_name)

    def test_add_ingredients_to_existing_recipe(self):
        test_name = 'Pasta Bake'
        test_description = 'Baked goodness'
        recipe = create_sample_recipe(name=test_name, description=test_description)

        ingredient1 = Ingredient(name='Prawns')
        ingredient2 = Ingredient(name='Ginger')

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

        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(recipe.name, test_name)
        for ingredient in ingredients:
            self.assertIn(ingredient.name, [ingredient1.name, ingredient2.name])

    def test_full_update_recipe(self):
        ingredient1 = Ingredient(name='Prawns')
        ingredient2 = Ingredient(name='Ginger')
        recipe = create_sample_recipe()
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
