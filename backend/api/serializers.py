from django.shortcuts import get_object_or_404
from djoser.serializers import (CurrentPasswordSerializer, PasswordSerializer,
                                UserCreateSerializer, UserSerializer)
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, Recipe_ingredient, Tag
from rest_framework import serializers
from users.models import User


class CustomUserSerializer(UserSerializer):
    """Сериализатор отображения информации о пользователях."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = '__all__',

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous or not request:
            return False
        return obj.following.filter(user=request.user).exists()


class CreateUserSerializer(UserCreateSerializer):
    """Сериализатор регистрации новых пользователей."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = '__all__',


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения рецептов на странице подписок."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения ингредиентов рецепта."""

    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = Recipe_ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
        read_only_fields = '__all__',


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор отображения рецептов."""

    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous or not request:
            return False
        return obj.is_favorited(request.user)

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous or not request:
            return False
        return obj.is_in_shopping_cart(request.user)


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор отображения ингредиентов при создании рецепта."""

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(required=True)
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = Recipe_ingredient
        fields = (
            'id',
            'amount',
            'name',
            'measurement_unit',
        )

    def get_name(self, obj):
        name = obj.ingredient.name
        return name

    def get_measurement_unit(self, obj):
        measurement_unit = obj.ingredient.measurement_unit
        return measurement_unit


class RecipeCreateSerializer(RecipeSerializer):
    """Сериализатор создания и обновления рецептов."""

    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = IngredientRecipeCreateSerializer(
        source='recipe_ingredients', many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate(self, obj):
        for field in (
            'name',
            'text',
            'cooking_time',
        ):
            if not obj.get(field):
                raise serializers.ValidationError(
                    f'{field} - обязательное поле.'
                )
        if not obj.get('tags'):
            raise serializers.ValidationError(
                'Должен быть указан минимум 1 тег.'
            )
        if not obj.get('ingredients'):
            raise serializers.ValidationError(
                'Должен быть указан минимум 1 ингредиент.'
            )
        for object in (
            obj.get('ingredients'),
            obj.get('tags'),
        ):
            object_id_list = [item['id'] for item in object]
            unique_object_id_list = set(object_id_list)
            if len(object_id_list) != len(unique_object_id_list):
                raise serializers.ValidationError(
                    'Теги и ингредиенты должны быть уникальны.'
                )
        return obj

    def set_recipe_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            ing, _ = Recipe_ingredient.objects.get_or_create(
                ingredient=get_object_or_404(
                    Ingredient.objects.filter(id=ingredient['id'])
                ),
                amount=ingredient['amount'],
            )
            recipe.ingredients.add(ing.id)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.set_recipe_ingredient(
            ingredients=ingredients,
            recipe=recipe
        )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.set_recipe_ingredient(
            ingredients=ingredients,
            recipe=instance
        )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(
            instance,
            context=context).data


class CustomPasswordSerializer(
    PasswordSerializer, CurrentPasswordSerializer
):
    """Сериализатор для изменения пароля пользователя."""

    pass


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор для подписок на авторов рецептов."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'username',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        serialized_result = RecipeSubscribeSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serialized_result.data
