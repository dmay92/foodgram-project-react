from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class IngredientFilter(FilterSet):
    """Класс фильтрации игредиентов по имени."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = (
            'name',
            'measurement_unit',
        )


class RecipeFilter(FilterSet):
    """Класс фильтрации рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    in_favorites = filters.BooleanFilter(
        method='favorited_filter'
    )
    in_shopping_cart = filters.BooleanFilter(
        method='shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'in_favorites',
            'in_shopping_cart',
        )

    def favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping__user=user)
        return queryset
