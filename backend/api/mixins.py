from rest_framework import mixins, viewsets


class FavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Миксин модель для Избранного."""
    pass
