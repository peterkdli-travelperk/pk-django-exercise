from django.test import TestCase

from recipe import models


class ModelTests(TestCase):

    def test_recipe_str(self):
        recipe = models.Recipe.objects.create(
            name='Steak and mushroom sauce',
            description='Meat and shrooms'
        )

        self.assertEqual(str(recipe), recipe.name)

    def test_ingredient_str(self):
        recipe = models.Recipe.objects.create(
            name='Steak and mushroom sauce',
            description='Meat and shrooms'
        )
        ingredient = models.Ingredient.objects.create(
            name='Cucumber',
            recipe=recipe

        )
        self.assertEqual(str(ingredient), ingredient.name)
