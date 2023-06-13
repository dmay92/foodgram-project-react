![workflow](https://github.com/dmay92/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)

Проект реализован на `Django` и `DjangoRestFramework`, доступен по [адресу](http://51.250.101.113).
Документация доступна по [адресу](http://51.250.101.113/api/docs/redoc).

# Продуктовый помощник Foodrgam
Дипломный проект курса Backend-разработки Яндекс.Практикум.
Проект представляет собой сайт-сервис для публикации рецептов различных блюд.

### Кратко о фнукционале сервиса:
- Публикация собственного рецепта
- Добавление другого автора в подписки, что позволяет следить за его рецептами
- Добавление рецептов в избранное
- Добавление рецептов в корзину, а также возможность скачать список продуктов-ингредиентов и их количества


## Особенности реализации

- Проект собирается из образов docker;
- Frontend предоставлен командой Яндекс.Практикум;
- Автором подготовлен Backend;
- База данных - postgress.
- Связь backend - frontend реализована через nginx+gunicorn.
- Образы foodgram-frontend и foodgram-backend запушены на DockerHub;
- Реализован action workflow, а автоматическим деплоем на удалённый сервер, осуществлением необходимых миграций и финальным уведомлением в Telegram.

## Описание страниц проекта

### - Главная страница
Отображает список всех рецептов опубликованных в сервисе отсортированных по дате публикации, по 6 на страницу, от новых к старым.

### - Страница пользователя
Отображение имя пользователя, все опубликованные им рецепты, а также включает возможность подписаться на него.

### - Страница рецепта
Отображает полное описание рецепта, его изображение, все его ингредиенты. Включает в себя возможность добавить рецепт в избранное и/или добавить рецепт в корзину, а так же возможно перейти к редактированию рецепта, если пользовать является его автором.

### - Страница подписок
Отображает список авторов на которых подписан пользователь, а также список их рецептов с краткой информацией. Возможно перейти на страницу автора или отписаться от него, перейти к конкретному рецепту.

### - Страница избранного
Отображает список рецептов добавленных пользователем и краткую информацию о них. Возможно убрать рецепт из избранного, а также добавить или убрать рецепт из корзины(списка покупок).

### - Корзина (список покупок)
Отображает список рецептов с краткой информацией. Возможно удалить рецепт из списка, а также скачать текстовый файл-список ингредиентов по добавленным в список рецептам. Список агрегированный, что удобно для того, чтобы использовать его для покупки продуктов перед готовкой.

#### Фильтрация
На главной странице и странице избранного доступна фильтрация по тегам, которыми помечаются рецепты.

## Запуск проекта
Для запуска проекта необходимо:

- Склонировать проект из репозитория:

```sh
$ git clone https://github.com/dmay92/foodgram-project-react.git
```

- Выполните вход на удаленный сервер

- Установите DOCKER на сервер:
```sh
apt install docker.io 
```

- Установить docker-compose на сервер:
```sh
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

- Отредактируйте конфигурацию сервера NGNIX:
```sh
Локально изменить файл ..infra/nginx.conf - заменить данные в строке server_name на IP-адрес удаленного сервера
```

- Создать переменные окружения (указаны в файле ../infra/env.sample) и добавить их в Secrets GitHub Actions

Полный необходимый список полей в Secrets GitHub Actions
* SECRET_KEY - секретный ключ django проекто из settings.py
* ENGINE - движок бд (postgresql) - django.db.backends.postgresql
* DB_NAME - имя бд
* POSTGRES_USER - логин для подключения к бд
* POSTGRES_PASSWORD - пароль для подключения к бд
* DB_HOST - название сервиса (контейнера)
* DB_PORT - порт для подключения к бд
* HOST - публичный ip вашего сервера
* USER - ваш пользователь на сервере
* SSH_KEY - ваш ssh ключ для подключения к серверу
* PASSPHRASE - ваш пароль для подтверждения ssh ключа
* DOCKER_USERNAME - имя пользователя на Dockerhub
* DOCKER_PASSWORD - пароль пользователя на Dockerhub
* TELEGRAM_TO - id пользователя в telegram куда должно отправляться уведопление об успешном выполнении Action на github
* TELEGRAM_TOKEN - токен бота в telegram, от которого будет отправляться уведомление

### Управление проектом
Для администрирования проекта на сервере необходимо создать суперпользователя
```sh
sudo docker-compose exec backend python manage.py createsuperuser
```

Админка доступна по адресу - http://ip_вашего_сервера/admin

Загрузка подготовленного списка ингредиентов для работы проекта
```sh
sudo docker-compose exec backend python manage.py load_ingredients
```

## Автор
Майоров Дмитрий Антонович
Студент Яндекс.Практикум
51-я когорта
Python Backend-разработка
Email - unic1992@yandex.ru
Telegram - @dmayd92