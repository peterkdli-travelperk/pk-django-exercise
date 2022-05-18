from django.contrib import admin

# Register your models here.
from recipe.models import Ingredient, Recipe

admin.site.register(Recipe)
admin.site.register(Ingredient)
