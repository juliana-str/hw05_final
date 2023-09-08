# "Социальная сеть Yatube" (hw05_final)

## 1. [Описание](#1)
## 2. [Установка](#2)
## 3. [Создание виртуального окружения](#3)
## 4. [Команды для запуска](#4)
## 5. [Примеры запросов](#5)
## 6. [Об авторе](#6)

---
## 1. Описание <a id=1></a>

Социальная сеть блогеров Yatube, в ней пользователи могут: 
  - регистрироваться
  - публиковать посты и управлять ими (корректировать\удалять).
  - оставлять свои комментарии к постам пользователей и управлять ими (корректировать\удалять).
  - просматривать комментарии других пользователей.
  - подписываться на любимых авторов.
  - отмечать понравившиеся записи.

---
## 2. Установка <a id=2></a>

Перед запуском необходимо склонировать проект:
```bash
git clone git@github.com:juliana-str/hw05_final.git
```
```
cd hw05_final/
```

---
## 3. Создание виртуального окружения <a id=3></a>

Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```

---
## 4. Команды для запуска <a id=4></a>

И установить зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```
```bash
python3 manage.py makemigrations
```
```bash
python3 manage.py migrate
```
```bash
python3 manage.py runserver
```

Проект использует базу данных sqlite3.  

---
## 5. Примеры запросов <a id=5></a>

Просмотр постов всех авторов:

```
www.julianka.pythonanywhere.com/posts/
```

Просмотр профайла автора

```
www.julianka.pythonanywhere.com/profile/username/
```
Просмотр существующих тем публикаций:

```
www.julianka.pythonanywhere.com/group/
```

Запрос на создание нового поста:

```
www.julianka.pythonanywhere.com/create/
```
---

Запрос на создание нового комментария к посту:

```
www.julianka.pythonanywhere.com/posts/post_id/comment/
```

---
## 6. Об авторе <a id=6></a>

Стрельникова Юлиана Сергеевна  
Python-разработчик (Backend)  
Россия, г. Санкт-Петербург
E-mail: julianka.str@yandex.ru  
Telegram: @JulianaStr