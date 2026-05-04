# РаботаРФ — Деплой на Render

## Шаг 1 — GitHub
1. Создай новый репозиторий на github.com
2. Закинь все файлы из этой папки в репозиторий

## Шаг 2 — Render (бэкенд + база данных)
1. Зайди на render.com, зарегистрируйся через GitHub
2. Нажми **New** → **Blueprint**
3. Выбери свой репозиторий
4. Render сам прочитает `render.yaml` и создаст:
   - Веб-сервис `rabota-rf-backend` (FastAPI)
   - PostgreSQL базу данных `rabota-rf-db`
5. Нажми **Apply** — подожди 3-5 минут
6. После деплоя скопируй URL бэкенда (вида `https://rabota-rf-backend.onrender.com`)

## Шаг 3 — Подключить фронтенд
1. Открой `frontend/rabotaSajt.html`
2. Найди строку: `var BEKEND_URL = "https://rabota-rf-backend.onrender.com";`
3. Замени URL на свой из шага 6
4. Открой файл в браузере — всё работает!

## Структура проекта
```
project/
├── backend/
│   ├── main.py          — все эндпоинты API
│   ├── models.py        — таблицы базы данных
│   ├── database.py      — подключение к БД
│   ├── seed.py          — заполнение начальными данными
│   └── requirements.txt — зависимости Python
├── frontend/
│   └── rabotaSajt.html  — весь сайт в одном файле
├── render.yaml          — конфиг для Render
└── README.md
```

## API эндпоинты
| Метод | URL | Описание |
|-------|-----|----------|
| POST | /registratsiya | Регистрация |
| POST | /vhod | Вход |
| GET | /vakansii | Все вакансии |
| GET | /vakansii?poisk=python | Поиск вакансий |
| GET | /vakansii/{id} | Одна вакансия |
| GET | /kompanii | Все компании |
| POST | /otkliki | Откликнуться (нужен токен) |
| GET | /otkliki/moi | Мои отклики (нужен токен) |
| POST | /rezyume | Сохранить резюме (нужен токен) |
| GET | /rezyume/moe | Моё резюме (нужен токен) |
| POST | /otzyvy | Добавить отзыв (нужен токен) |
| GET | /profil | Профиль (нужен токен) |
