from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(
    'ingredients',
    views.IngredientsVS,
    basename='ingredients'
)
router.register(
    'recipes',
    views.RecipeVS,
    basename='recipes'
)
router.register(
    'tags',
    views.TagVS,
    basename='tags'
)
router.register(
    'users',
    views.UserVS,
    basename='users'
)

urlpatterns = [
    path(
        'users/me/',
        views.UserSelfView.as_view()
    ),
    path(
        'users/set_password/',
        views.UserSetPasswordView.as_view()
    ),
    path(
        '',
        include(router.urls)
    ),
    path(
        'auth/',
        include('djoser.urls.authtoken')
    )
]
