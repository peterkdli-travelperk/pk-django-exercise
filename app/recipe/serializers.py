from rest_framework import serializers

from recipe.models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name',)
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'description',
            'ingredients'
        )
        read_only_field = ('id',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', [])

        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            Ingredient.objects.create(name=ingredient['name'], recipe=recipe)

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)

        instance.ingredients.all().delete()

        ingredients = validated_data.get('ingredients', [])
        for ingredient in ingredients:
            ingredient_obj = Ingredient.objects.create(name=ingredient['name'], recipe=instance)
            instance.ingredients.add(ingredient_obj)

        instance.save()
        return instance






