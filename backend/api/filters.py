from django.db.models import Q
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Класс фильтрации игредиентов."""

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

    author = filters.AllValuesFilter(field_name='author')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def _filter(self, queryset, name, value, param):
        if value and self.request.user.is_authenticated:
            return queryset.filter(**{f'{param}__user': self.request.user})
        if not value and self.request.user.is_authenticated:
            return queryset.filter(~Q(**{f'{param}__user': self.request.user}))
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        return self._filter(queryset, name, value, param='favorite')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._filter(queryset, name, value, param='cart')
