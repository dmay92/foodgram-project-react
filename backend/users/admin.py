from django.contrib import admin
from foodgram.settings import EMPTY_VALUE

from .models import Subscribe, User


class UserAdmin(admin.ModelAdmin):
    """Класс администрирования пользователей."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'date_joined',
    )
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_filter = (
        'username',
        'email',
        'is_staff',
        'date_joined',
    )
    empty_value_display = EMPTY_VALUE


class SubscribeAdmin(admin.ModelAdmin):
    """Класс администрирования подписок."""

    list_display = (
        'id',
        'user',
        'author',
    )
    search_fields = (
        'user',
        'author',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
