from django.db import models


class Recipe(models.Model):
    name = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.TextField()
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )

    def __str__(self):
        return self.name
