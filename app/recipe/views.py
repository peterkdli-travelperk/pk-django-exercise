from django.shortcuts import render

from rest_framework import viewsets, mixins

from recipe import serializers
from recipe.models import Recipe


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """return specificly requested recipe or all if no request"""
        current_recipe_name = self.request.query_params.get('name', None)
        if current_recipe_name is None:
            return self.queryset

        return self.queryset.filter(name__icontains=current_recipe_name)

    serializer_class = serializers.RecipeSerializer
