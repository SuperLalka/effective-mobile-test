<!-- PROJECT LOGO -->
<div align="center">
  <h2>effective-mobile-test</h2>

  <h3 align="center">README тестового задания</h3>

  <p align="center">
    Django-приложение: Платформа для обмена вещами
  </p>
</div>

<a name="readme-top"></a>

<hr>

<!-- ABOUT THE PROJECT -->
## About The Project

Разработать монолитное веб-приложение на Django для организации обмена вещами между пользователями.
Пользователи смогут размещать объявления о товарах для обмена, просматривать чужие объявления и отправлять предложения на обмен. 

### Функциональные требования:

#### Создание объявления
* Входные данные:
  - Пользователь (user_id или данные авторизации через стандартную систему Django).
  - Заголовок объявления (title).
  - Описание товара (description).
  - URL изображения (image_url) – опционально.
  - Категория товара (category).
  - Состояние товара (например, «новый», «б/у»).

* Автоматизация:
  - Генерация уникального идентификатора (id) для объявления (автоинкрементное поле).
  - Автоматическая фиксация даты публикации (created_at).

* Вывод: Подтверждение создания объявления с его данными.

#### Редактирование объявления
- Возможность обновления полей (title, description, image_url, category, condition).
- Ограничение: только автор объявления может редактировать запись.
- Обработка ошибок: уведомление, если объявление не найдено или пользователь не является автором.

#### Удаление объявления
- Удаление объявления по его уникальному идентификатору.
- Корректная обработка ошибок (например, при отсутствии объявления с указанным id).

#### Поиск и фильтрация объявлений
- Поиск по ключевым словам в заголовке и описании.
- Фильтрация по категории и состоянию товара.
- Реализация пагинации для возврата ограниченного числа результатов за один запрос.

#### Обмен предложениями
* Создание предложения обмена:
  - Пользователь отправляет предложение обмена, указывая:
    - id объявления, инициирующего предложение (ad_sender_id).
    - id объявления получателя (ad_receiver_id).
    - Комментарий (comment).
  - Автоматическая установка статуса предложения: «ожидает».

* Обновление предложения:
  - Возможность изменения статуса предложения (например, «принята» или «отклонена»).

* Просмотр предложений:
  - Фильтрация по отправителю, получателю или статусу.

#### Отображение объявлений
* Веб-страница или API для получения списка всех объявлений с основными данными:
  - id, user, title, description, image_url, category, condition, created_at

 
### Технологический стек
* Язык: Python 3.8+
* Веб-фреймворк: Django 4+ (с использованием встроенной ORM)
* Шаблонизация: Django Templates для создания HTML-страниц
* База данных: SQLite или PostgreSQL (на выбор)
* REST API: Django REST Framework (опционально, для расширения функционала)
* Документация:
  - README.md с инструкциями по установке, настройке и запуску проекта
  - Автоматическая документация API (при использовании Django REST Framework)
* Тестирование: Unittest или Pytest для проверки ключевых функций приложения


### Built With

* [![Django][Django-badge]][Django-url]
* [![Postgres][Postgres-badge]][Postgres-url]
* [![Docker][Docker-badge]][Docker-url]


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

Скопировать проект в репозиторий на локальной машине (HTTPS или SSH)
  ```sh
  git clone https://github.com/SuperLalka/effective-mobile-test.git
  ```
  ```sh
  git clone git@github.com:SuperLalka/effective-mobile-test.git
  ```

### Installation

Для запуска проекта достаточно собрать и запустить контейнеры Docker.
Миграция базы данных и загрузка фикстур будут применены автоматически.

```sh
docker-compose -f docker-compose.yml up -d --build
```

Запуск тестов:
```sh
docker-compose -f test.yml up --build
```

### Notes

> <b>Креды администратора: admin 123456w</b>
> 
> <b>Пароль всех обычных пользователей: qSgKVgzZWGIFpU3OE34h</b>


### Documentation

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Django-badge]: https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white
[Django-url]: https://docs.djangoproject.com/
[Postgres-badge]: https://img.shields.io/badge/postgresql-%234169E1.svg?style=for-the-badge&logo=postgresql&logoColor=white
[Postgres-url]: https://www.postgresql.org/
[Docker-badge]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
