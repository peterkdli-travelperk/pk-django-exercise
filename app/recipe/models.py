from django.db import models


class Recipe(models.Model):
    name = models.TextField()
    description = models.TextField()
    ingredients = models.ManyToManyField('Ingredient')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name
