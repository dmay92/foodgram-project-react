from csv import DictReader
from pathlib import Path

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

DATA_FILE_PATH = Path(
    Path(BASE_DIR), 'ingredients_for_upload.csv')


class Command(BaseCommand):
    """Служебная команда загрузки данных из csv."""

    help = 'Загрузка данных ингредиентов из csv'

    def handle(self, *args, **options):

        if Ingredient.objects.exists():
            self.stderr.write('Данные уже загружены... Завершение.')
            return

        self.stdout.write('Загрузка данных')

        for row in DictReader(open(DATA_FILE_PATH, encoding='utf-8')):
            data = Ingredient(
                name=row['name'], measurement_unit=row['measurement_unit'])
            data.save()
