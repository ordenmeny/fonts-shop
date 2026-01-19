# Описание проекта: онлайн-магазин шрифтов с настраиваемыми лицензиями.

# FontLicenses Store

FontLicenses Store - это концепт онлайн магазина шрифтов, где покупка лицензии превращается из переписки с менеджером в
понятный и быстрый сценарий: выбрал семейство, выбрал начертание, указал тип лицензии и оформил заказ.

Проект решает две практические задачи:

- Упрощает выбор и покупку шрифтов за счет прозрачной конфигурации лицензий и моментального расчета цены.
- Автоматизирует процесс заказа, сохраняя историю покупок и предоставляя администрирование каталога и цен.

---

## Стек технологий

**Backend**

- Python 3.13
- Django 5.2
- Django REST Framework 3.16
- PostgreSQL 16
- SimpleJWT (djangorestframework-simplejwt)

**Frontend**

- React 18

**Инфраструктура**

- Docker, docker-compose
- Nginx (reverse proxy)

**Аналитика**

- Добавлена аналитика заказов лицензий на основе pandas и визуализация на matplotlib.
Данные собираются из OrderItem: дата заказа, тип лицензии, цена, шрифт и начертание. На pandas считаются агрегаты: общее число купленных лицензий, суммарная выручка, распределения по шрифтам, типам лицензий и начертаниям, а также динамика по месяцам (количество и выручка). Для наглядности результаты строятся в виде PNG графиков через matplotlib (bar, pie, line) с поддержкой top N и объединением остальных категорий в "Other".


---

## Демонстрация (Скриншоты)

Главная / каталог:
![Главная страница](https://github.com/ordenmeny/fonts-shop/blob/main/images-for-readme/Снимок%20экрана%202026-01-15%20в%2023.52.18.png)

Карточка шрифта и выбор лицензии:
![Карточка шрифта](https://github.com/ordenmeny/fonts-shop/blob/main/images-for-readme/Снимок%20экрана%202026-01-15%20в%2023.52.39.png)

Корзина:
![Корзина](https://github.com/ordenmeny/fonts-shop/blob/main/images-for-readme/Снимок%20экрана%202026-01-15%20в%2023.52.48.png)

Заказы пользователя:
![Мои заказы](https://github.com/ordenmeny/fonts-shop/blob/main/images-for-readme/Снимок%20экрана%202026-01-19%20в%2022.16.32.png)
---

## Установка и запуск

### Запуск Django-проекта локально

1. Клонируйте репозиторий:

```http
https://github.com/ordenmeny/fonts-shop.git
```

Перейдите в директорию проекта:

```http
cd fonts-shop
```

Положите .env на уровень выше текущей директории.
Задайте, следующие переменные:

```http
DB_NAME=devdb
DB_USER=devuser
DB_PASS=devpassword
DB_HOST=localhost
DB_PORT=5432

PGADMIN_DEFAULT_EMAIL=admin@yandex.ru
PGADMIN_DEFAULT_PASSWORD=1234

SECRET_KEY=asdkjhgfjkasdhgfjasdgfk
DEBUG=True
```

2. Установите uv (пакетный менеджер python):
   На Linux/Mac OS (через curl):

```http
   curl -LsSf https://astral.sh/uv/install.sh | sh
```

На Windows (через PowerShell):

```http   
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Установите версию python:

```http
uv python pin 3.13
```

4. Установите зависимости:

```http
uv sync
```

5. Выполните миграции:

```http
uv run python manage.py makemigrations
uv run python manage.py migrate
```

6. Создайте суперпользователя:

```http
uv run python manage.py createsuperuser
```

7. Запуск сервера:

```http
uv run python manage.py runserver
```

---

### Запуск React-проекта (frontend) локально.

1) Требования
   Обязательное
   Node.js (рекомендуется LTS версия)
   npm (идет вместе с Node.js) или yarn/pnpm (если проект использует их)
   Проверка версий:

```http
node -v
npm -v
```

2) На уровне выше django-проекта склонируйте репозиторий:

```http
git clone https://github.com/ordenmeny/fonts-shop-frontend.git
cd fonts-shop-frontend
```

3) npm install
4) Создайте .env файл (рядом с package.json) и заполните его следующими переменными:

```http
VITE_API_ORIGIN=http://127.0.0.1:8000
```

5) Запуск

```http
npm run dev
```

## Ссылка на деплой

```http
https://fonts.unimatch.ru
```

## Запустить matplotlib
```bash
python manage.py plot_user_orders_analytics --user-id 1 --out-dir analytics_plots --top-n 12
```


