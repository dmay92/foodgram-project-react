from django.contrib import admin
from foodgram.settings import EMPTY_VALUE

from .models import (Favorite, Ingredient, Recipe, Recipe_ingredient,
                     Shopping_cart, Tag)

admin.site.site_header = 'Администрирование Foodgram'


class Recipe_IngredientsInline(admin.TabularInline):
    """Inline класс администрирования ингредиентов определенного рецепта."""

    model = Recipe_ingredient
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс администрирования ингредиентов."""

    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
        'measurement_unit',
    )
    ordering = ('id',)
    inlines = (Recipe_IngredientsInline,)
    empty_value_display = EMPTY_VALUE


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс администрирования тегов."""

    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = (
        'name',
        'color',
        'slug',
    )
    list_filter = (
        'name',
        'color',
        'slug',
    )
    ordering = ('name',)
    empty_value_display = EMPTY_VALUE


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс администрирования рецептов."""

    list_display = (
        'id',
        'name',
        'author',
        'text',
        'cooking_time',
        'favorites_amount',
        'pub_date',
    )
    search_fields = (
        'name',
        'author',
        'cooking_time',
        'text',
    )
    readonly_fields = (
        'favorites_amount',
    )
    list_filter = (
        'name',
        'pub_date',
        'author',
        'tags',
    )
    inlines = (Recipe_IngredientsInline,)
    ordering = ('name',)
    empty_value_display = EMPTY_VALUE

    @admin.display(description='Всего в избранном')
    def favorites_amount(self, obj):
        return obj.favorites.count()


@admin.register(Recipe_ingredient)
class Recipe_IngredientsAdmin(admin.ModelAdmin):
    """Класс администрирования ингредиентов определенного рецепта."""

    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = (
        'recipe',
        'ingredient',
    )
    list_filter = (
        'recipe',
        'ingredient',
    )
    ordering = ('id',)
    empty_value_display = EMPTY_VALUE


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Класс администрирования избранных рецептов."""

    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = (
        'user',
        'recipe',
    )
    list_filter = (
        'user',
        'recipe',
    )
    ordering = ('id',)
    empty_value_display = EMPTY_VALUE


@admin.register(Shopping_cart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Класс администрирования пользовательских корзин."""

    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = (
        'user',
        'recipe',
    )
    list_filter = (
        'user',
        'recipe',
    )
    ordering = ('id',)
    empty_value_display = EMPTY_VALUE
