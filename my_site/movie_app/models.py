from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


STATUS_CHOICES = (
    ('pro', 'pro'),
    ('simple', 'simple')
)

class UserProfile(AbstractUser):
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(16), MaxValueValidator(80)],
                                           null=True, blank=True)
    phone_number = PhoneNumberField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='simple')
    avatar = models.ImageField(upload_to='profile_photo/', null=True, blank=True)
    date_register = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.username}'


class Category(models.Model):
    category_name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.category_name


class Country(models.Model):
    country_name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.country_name

class Director(models.Model):
    director_name = models.CharField(max_length=32)
    bio = models.TextField(null=True, blank=True)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)],
                                           null=True, blank=True)
    director_image = models.ImageField(upload_to='director_photo/', null=True, blank=True)

    def __str__(self):
        return self.director_name


class Actor(models.Model):
    actor_name = models.CharField(max_length=32)
    bio = models.TextField(null=True, blank=True)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                           null=True, blank=True)
    actor_image = models.ImageField(upload_to='actor_photo/', null=True, blank=True)

    def __str__(self):
        return self.actor_name

class Genre(models.Model):
    genre_name = models.CharField(max_length=32)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='genre_category')

    def __str__(self):
        return self.genre_name


class Movie(models.Model):
    TYPES_CHOICES = (
    (144, 144),
    (360, 360),
    (480, 480),
    (720, 720),
    (1080, 1080),
    )
    movie_name = models.CharField(max_length=100)
    year = models.DateTimeField()
    country = models.ManyToManyField(Country, related_name='country_movie')
    director = models.ManyToManyField(Director, related_name='director_movie')
    actor = models.ManyToManyField(Actor, related_name='actor_movie')
    genre = models.ManyToManyField(Genre, related_name='genre_movie')
    types = models.PositiveSmallIntegerField(choices=TYPES_CHOICES, default=720)
    movie_time = models.PositiveSmallIntegerField()
    description = models.TextField()
    movie_trailer = models.URLField()
    movie_image = models.ImageField(upload_to='movie_photo/')
    slogan = models.CharField(max_length=100)
    status_movie = models.CharField(max_length=32, choices=STATUS_CHOICES)

    def __str__(self):
        return self.movie_name

    def get_avg_rating(self):
        rating = self.star_movie.all()
        if rating.exists():
            return round(sum([i.star for i in rating]) / rating.count(), 2)
        return 0

    def get_count_people(self):
        return self.star_movie.count()




class MovieLanguages(models.Model):
    language = models.CharField(max_length=64)
    video = models.FileField(upload_to='language_video/')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='language_movie')

    def __str__(self):
        return self.language


class Moments(models.Model):
  movie = models.ForeignKey(Movie,on_delete=models.CASCADE, related_name='moment_review')
  movie_moments = models.ImageField(upload_to='moments/')

  def __str__(self):
      return self.movie.movie_name


class Rating(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='star_movie')
    star = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 11)],
                                            null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} {self.star}'


class Review(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_review')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} {self.movie.movie_name}'

    def get_count_like(self):
        like = self.review_like.all()
        if like.exists():
            return like.count()
        return 0


class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='review_like')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} {self.like}'


class Favorite(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username}'


class FavoriteMovie(models.Model):
    favorite = models.ForeignKey(Favorite, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.movie.movie_name}'


class History(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.viewed_at

