from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscribe, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateUserSerializer, CustomPasswordSerializer,
                          CustomUserSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          RecipeSubscribeSerializer, SubscribeSerializer,
                          TagSerializer)


class UserVS(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Класс viewset для модели пользователя."""

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return CustomUserSerializer

    @action(detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page,
            many=True,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        subscription = Subscribe.objects.filter(
            user=request.user, author=author)
        if request.method == 'DELETE' and not subscription:
            return Response(
                {'errors': 'Невозможно удалить несуществующую подписку.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            subscription.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        if subscription:
            return Response(
                {'errors': 'Подписка на пользователя уже совершена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if author == request.user:
            return Response(
                {'errors': 'Подписка на самого себя запрещена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscribe.objects.create(user=request.user, author=author)
        serializer = SubscribeSerializer(
            author,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserSelfView(views.APIView):
    """Класс view для отображения текущего пользователя."""

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = CustomUserSerializer(
            request.user,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSetPasswordView(views.APIView):
    """Класс view для изменения пароля пользователя."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = CustomPasswordSerializer(
            data=request.data,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        if serializer.is_valid():
            self.request.user.set_password(serializer.data['new_password'])
            self.request.user.save()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class TagVS(viewsets.ReadOnlyModelViewSet):
    """Класс viewset для отображения тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientsVS(viewsets.ReadOnlyModelViewSet):
    """Класс viewset для отображения ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeVS(viewsets.ModelViewSet):
    """Класс viewset для рецептов."""

    http_method_names = ('get', 'post', 'patch', 'delete',)
    queryset = Recipe.objects.all()
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in (
            'create',
            'partial_update',
        ):
            return RecipeCreateSerializer
        return RecipeSerializer

    def create_update_delete(self, model, recipe, request):
        instance = model.objects.filter(recipe=recipe, user=request.user)
        if not instance and request.method == 'DELETE':
            return Response(
                {'errors': 'Рецепт отсутствует, удалять нечего.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if instance:
            return Response(
                {'errors': 'Рецепт уже добавлен.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeSubscribeSerializer(
            recipe,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.create_update_delete(
            Favorite,
            recipe,
            request
        )

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.create_update_delete(
            ShoppingCart,
            recipe,
            request
        )

    @action(
        methods=('get',),
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping.exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        today = datetime.today()
        shopping_list = (
            f'Список покупок пользователя {user.get_full_name()} '
            f'на {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'* {ingredient["ingredient__name"]} '
            f'- {ingredient["amount"]} '
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(
            shopping_list,
            content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = (
            f'attachment; filename={filename}'
        )
        return response
