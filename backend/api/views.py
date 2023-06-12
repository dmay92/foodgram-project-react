from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import Subscribe, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, RecipeSubscribeSerializer,
                          SubscribeSerializer, TagSerializer)


class UserViewSet(UserViewSet):
    """Класс viewset пользователя."""

    @action(
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        methods=['POST', 'DELETE']
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if self.request.method == 'POST':
            if Subscribe.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = Subscribe.objects.create(user=user, author=author)
            serializer = SubscribeSerializer(
                follow, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if Subscribe.objects.filter(user=user, author=author).exists():
            follow = get_object_or_404(Subscribe, user=user, author=author)
            follow.delete()
            return Response(
                'Подписка успешно удалена',
                status=status.HTTP_204_NO_CONTENT
            )
        if user == author:
            return Response(
                {'errors': 'Нельзя отписаться от самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'errors': 'Вы не подписаны на данного пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        methods=['GET']
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс viewset тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс viewset ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Класс viewset избранного."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            return Response(
                data={'detail': 'Рецепт уже добавлен в избранное!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                data={'detail': 'Рецепт ещё не добавлен в избранное!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Класс viewset корзины."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                data={'detail': 'Вы уже добавили этот рецепт!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                data={'detail': 'Вы ещё не добавили этот рецепт!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс viewset рецептов."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = ShoppingCart.objects.filter(
            user=request.user
        ).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(amount=Sum('recipe__recipe_ingredient__amount'))
        user = request.user.get_full_name()
        shopping_cart = f'{user}, вот ваш список покупок:\n\n'
        for ingredient in ingredients:
            shopping_cart += (
                f'* {ingredient["recipe__ingredients__name"]} '
                f'- {ingredient["amount"]} '
                f'({ingredient["recipe__ingredients__measurement_unit"]})\n'
            )
        shopping_cart += '\n\n@Продуктовый помощник Foodgram'
        filename = f'{user}_shopping_list.txt'
        response = HttpResponse(
            shopping_cart,
            content_type='text.txt; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
