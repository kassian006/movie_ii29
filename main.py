import os
import sys
import random
from pathlib import Path
from datetime import timedelta

# ---------------------------
# Django bootstrap
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent  # там где manage.py
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_site.settings")  # у тебя ROOT_URLCONF = 'my_site.urls'

import django  # noqa: E402
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.core.files.base import ContentFile  # noqa: E402
from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402

from movie_app.models import (  # noqa: E402
    Category, Country, Director, Actor, Genre, Movie,
    MovieLanguages, Moments, Rating, Favorite, FavoriteMovie, History
)

User = get_user_model()

# У тебя Review.parent обязательный -> создавать корневые отзывы нельзя
CREATE_REVIEWS = False


# ---------------------------
# Helpers
# ---------------------------
def dummy_png(name="image.png"):
    # валидный 1x1 PNG
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\xdac\xf8\x0f\x00\x01\x01\x01\x00\x18\xdd\x8d\x18"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return ContentFile(png_bytes, name=name)


def dummy_video(name="video.mp4"):
    # для FileField достаточно любых байтов
    return ContentFile(b"FAKE_MP4_SEED_DATA", name=name)


def rand_phone():
    return f"+996{random.randint(500000000, 799999999)}"


def pick(seq):
    return random.choice(list(seq))


def pick_many(seq, k_min=1, k_max=3):
    seq = list(seq)
    k = random.randint(k_min, min(k_max, len(seq)))
    return random.sample(seq, k=k)


def dt_years_ago(y_min=1, y_max=20):
    return timezone.now() - timedelta(days=365 * random.randint(y_min, y_max))


# ---------------------------
# Seed
# ---------------------------
@transaction.atomic
def seed():
    random.seed(42)
    print("✅ Seeding (modeltranslation: en/ru) ...")

    # -------- Users --------
    admin, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@example.com",
            "first_name": "Admin",
            "last_name": "System",
            "age": 25,
            "phone_number": rand_phone(),
            "status": "pro",
        },
    )
    if created:
        admin.set_password("admin12345")
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

    users = [admin]
    for i in range(1, 11):
        u, created = User.objects.get_or_create(
            username=f"user{i}",
            defaults={
                "email": f"user{i}@example.com",
                "first_name": f"User{i}",
                "last_name": "Kassian",
                "age": random.randint(18, 35),
                "phone_number": rand_phone(),
                "status": "simple" if i % 3 else "pro",
            },
        )
        if created:
            u.set_password("password123")
            u.save()
        users.append(u)

    # -------- Categories (translated) --------
    categories_payload = [
        {"en": "Movies", "ru": "Фильмы"},
        {"en": "Series", "ru": "Сериалы"},
        {"en": "Documentary", "ru": "Документальные"},
        {"en": "Cartoons", "ru": "Мультфильмы"},
    ]
    categories = []
    for p in categories_payload:
        # у modeltranslation базовое поле category_name остаётся, но лучше заполнить en/ru явно
        c, _ = Category.objects.get_or_create(
            category_name=p["en"],  # базовое
            defaults={
                "category_name_en": p["en"],
                "category_name_ru": p["ru"],
            },
        )
        # на случай если уже был создан без переводов — дозаполним
        changed = False
        if not getattr(c, "category_name_en", None):
            c.category_name_en = p["en"]; changed = True
        if not getattr(c, "category_name_ru", None):
            c.category_name_ru = p["ru"]; changed = True
        if changed:
            c.save()
        categories.append(c)

    # -------- Countries (translated) --------
    countries_payload = [
        {"en": "Kyrgyzstan", "ru": "Кыргызстан"},
        {"en": "Kazakhstan", "ru": "Казахстан"},
        {"en": "USA", "ru": "США"},
        {"en": "UK", "ru": "Великобритания"},
        {"en": "Turkey", "ru": "Турция"},
        {"en": "South Korea", "ru": "Южная Корея"},
        {"en": "Japan", "ru": "Япония"},
        {"en": "France", "ru": "Франция"},
        {"en": "Germany", "ru": "Германия"},
    ]
    countries = []
    for p in countries_payload:
        co, _ = Country.objects.get_or_create(
            country_name=p["en"],
            defaults={
                "country_name_en": p["en"],
                "country_name_ru": p["ru"],
            },
        )
        changed = False
        if not getattr(co, "country_name_en", None):
            co.country_name_en = p["en"]; changed = True
        if not getattr(co, "country_name_ru", None):
            co.country_name_ru = p["ru"]; changed = True
        if changed:
            co.save()
        countries.append(co)

    # -------- Directors (translated: director_name, bio) --------
    directors_payload = [
        {"en": "Christopher Nolan", "ru": "Кристофер Нолан"},
        {"en": "Denis Villeneuve", "ru": "Дени Вильнёв"},
        {"en": "Guy Ritchie", "ru": "Гай Ричи"},
        {"en": "Bong Joon-ho", "ru": "Пон Джун-хо"},
        {"en": "Quentin Tarantino", "ru": "Квентин Тарантино"},
    ]
    directors = []
    for p in directors_payload:
        d, _ = Director.objects.get_or_create(
            director_name=p["en"],
            defaults={
                "director_name_en": p["en"],
                "director_name_ru": p["ru"],
                "bio_en": f"{p['en']} is known for distinctive directing style.",
                "bio_ru": f"{p['ru']} известен своим узнаваемым режиссёрским стилем.",
                "age": random.randint(40, 70),
            },
        )
        # дозаполнение если нужно
        if not getattr(d, "director_name_en", None): d.director_name_en = p["en"]
        if not getattr(d, "director_name_ru", None): d.director_name_ru = p["ru"]
        if not getattr(d, "bio_en", None): d.bio_en = f"{p['en']} is known for distinctive directing style."
        if not getattr(d, "bio_ru", None): d.bio_ru = f"{p['ru']} известен своим узнаваемым режиссёрским стилем."
        if not d.age: d.age = random.randint(40, 70)
        d.save()
        directors.append(d)

    # -------- Actors (translated: actor_name, bio) --------
    actors_payload = [
        {"en": "Leonardo DiCaprio", "ru": "Леонардо ДиКаприо"},
        {"en": "Cillian Murphy", "ru": "Киллиан Мёрфи"},
        {"en": "Margot Robbie", "ru": "Марго Робби"},
        {"en": "Brad Pitt", "ru": "Брэд Питт"},
        {"en": "Song Kang-ho", "ru": "Сон Кан-хо"},
        {"en": "Timothée Chalamet", "ru": "Тимоти Шаламе"},
        {"en": "Zendaya", "ru": "Зендея"},
    ]
    actors = []
    for p in actors_payload:
        a, _ = Actor.objects.get_or_create(
            actor_name=p["en"],
            defaults={
                "actor_name_en": p["en"],
                "actor_name_ru": p["ru"],
                "bio_en": f"{p['en']} has performed across multiple genres.",
                "bio_ru": f"{p['ru']} исполнял роли в разных жанрах.",
                "age": random.randint(20, 70),
            },
        )
        if not getattr(a, "actor_name_en", None): a.actor_name_en = p["en"]
        if not getattr(a, "actor_name_ru", None): a.actor_name_ru = p["ru"]
        if not getattr(a, "bio_en", None): a.bio_en = f"{p['en']} has performed across multiple genres."
        if not getattr(a, "bio_ru", None): a.bio_ru = f"{p['ru']} исполнял роли в разных жанрах."
        if not a.age: a.age = random.randint(20, 70)
        a.save()
        actors.append(a)

    # -------- Genres (translated: genre_name) --------
    # Категории на en как ключ (Movies/Series/..)
    genre_payload = {
        "Movies": [("Action", "Боевик"), ("Drama", "Драма"), ("Thriller", "Триллер"), ("Sci-Fi", "Фантастика")],
        "Series": [("Crime", "Криминал"), ("Mystery", "Детектив"), ("Drama", "Драма")],
        "Documentary": [("History", "История"), ("Science", "Наука"), ("Nature", "Природа")],
        "Cartoons": [("Kids", "Детские"), ("Adventure", "Приключения"), ("Fantasy", "Фэнтези")],
    }

    genres = []
    for cat in categories:
        key = getattr(cat, "category_name_en", cat.category_name)
        for en, ru in genre_payload.get(key, []):
            g, _ = Genre.objects.get_or_create(
                genre_name=en,
                category=cat,
                defaults={"genre_name_en": en, "genre_name_ru": ru},
            )
            if not getattr(g, "genre_name_en", None): g.genre_name_en = en
            if not getattr(g, "genre_name_ru", None): g.genre_name_ru = ru
            g.save()
            genres.append(g)

    # -------- Movies (translated: movie_name, description) --------
    movies_payload = [
        {
            "en_name": "Oppenheimer",
            "ru_name": "Оппенгеймер",
            "en_desc": "A dramatic story about science, responsibility, and history.",
            "ru_desc": "Драма о науке, ответственности и истории.",
            "slogan": "The world forever changes.",
            "time": 180,
            "types": 1080,
        },
        {
            "en_name": "Dune: Part One",
            "ru_name": "Дюна: Часть первая",
            "en_desc": "Sci-fi epic about politics, prophecy, and survival on Arrakis.",
            "ru_desc": "Фантастическая эпопея о политике, пророчестве и выживании на Арракисе.",
            "slogan": "Beyond fear, destiny awaits.",
            "time": 155,
            "types": 1080,
        },
        {
            "en_name": "Inception",
            "ru_name": "Начало",
            "en_desc": "A heist in dreams with layered realities.",
            "ru_desc": "Ограбление во сне с несколькими уровнями реальности.",
            "slogan": "Your mind is the scene of the crime.",
            "time": 148,
            "types": 720,
        },
        {
            "en_name": "Parasite",
            "ru_name": "Паразиты",
            "en_desc": "A dark comedy thriller about class conflict.",
            "ru_desc": "Чёрная комедия-триллер о классовом конфликте.",
            "slogan": "Act like you own the place.",
            "time": 132,
            "types": 1080,
        },
    ]

    movies = []
    for p in movies_payload:
        # movie_name базовый + переводные
        m, _ = Movie.objects.get_or_create(
            movie_name=p["en_name"],
            defaults={
                "movie_name_en": p["en_name"],
                "movie_name_ru": p["ru_name"],
                "description_en": p["en_desc"],
                "description_ru": p["ru_desc"],
                "year": dt_years_ago(),
                "types": p["types"],
                "movie_time": p["time"],
                "movie_trailer": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "slogan": p["slogan"],  # slogan у тебя НЕ переводится
                "status_movie": "pro" if random.random() > 0.5 else "simple",
            },
        )

        # обязательное изображение
        if not m.movie_image:
            m.movie_image.save(f"{p['en_name']}.png", dummy_png(f"{p['en_name']}.png"), save=True)

        # если уже был создан — дозаполним переводы
        if not getattr(m, "movie_name_en", None): m.movie_name_en = p["en_name"]
        if not getattr(m, "movie_name_ru", None): m.movie_name_ru = p["ru_name"]
        if not getattr(m, "description_en", None): m.description_en = p["en_desc"]
        if not getattr(m, "description_ru", None): m.description_ru = p["ru_desc"]
        if not m.slogan: m.slogan = p["slogan"]
        m.save()

        # M2M
        m.country.set(pick_many(countries, 1, 2))
        m.director.set([pick(directors)])
        m.actor.set(pick_many(actors, 2, 4))
        m.genre.set(pick_many(genres, 1, 3))

        movies.append(m)

    # -------- MovieLanguages (translated: language) --------
    langs = [("en", "English"), ("ru", "Russian")]
    for m in movies:
        for code, label in pick_many(langs, 1, 2):
            ml, _ = MovieLanguages.objects.get_or_create(
                movie=m,
                language=label,
                defaults={
                    "language_en": label,
                    "language_ru": "Русский" if code == "ru" else "Английский",
                }
            )
            if not ml.video:
                ml.video.save(f"{m.movie_name}_{code}.mp4", dummy_video(f"{m.movie_name}_{code}.mp4"), save=True)

    # -------- Moments --------
    for m in movies:
        for i in range(random.randint(2, 5)):
            mo = Moments.objects.create(movie=m)
            mo.movie_moments.save(f"{m.movie_name}_moment_{i}.png", dummy_png(f"{m.movie_name}_moment_{i}.png"), save=True)

    # -------- Favorites --------
    for u in users:
        fav, _ = Favorite.objects.get_or_create(user=u)
        for m in pick_many(movies, 1, min(3, len(movies))):
            FavoriteMovie.objects.get_or_create(favorite=fav, movie=m)

    # -------- Ratings --------
    for u in users:
        for m in pick_many(movies, 1, len(movies)):
            Rating.objects.get_or_create(
                user=u,
                movie=m,
                defaults={"star": random.randint(6, 10) if random.random() > 0.2 else random.randint(1, 7)},
            )

    # -------- History --------
    for u in users:
        for m in pick_many(movies, 1, len(movies)):
            History.objects.create(user=u, movie=m)

    print("✅ Done. Seed created:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Movies: {Movie.objects.count()}")
    print(f"   Ratings: {Rating.objects.count()}")
    print(f"   Favorites: {Favorite.objects.count()}")
    print("   (Reviews disabled because Review.parent is required)")


if __name__ == "__main__":
    seed()