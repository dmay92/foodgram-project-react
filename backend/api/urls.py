from django.urls import include, path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('ingredients',
                views.IngredientViewSet, basename='ingredients')
router.register('recipes',
                views.RecipeViewSet, basename='recipes')
router.register('tags',
                views.TagViewSet, basename='tags')
router.register('users',
                views.UserViewSet, basename='users')
router.register(r'^recipes/(?P<recipe_id>\d+)/favorite',
                views.FavoriteViewSet, basename='favorite')
router.register(r'^recipes/(?P<recipe_id>\d+)/shopping_cart',
                views.ShoppingCartViewSet, basename='shopping_cart')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
