from django.urls import path, include
from rest_framework import routers
from .views import (UserProfileListAPIView, UserProfileDetailAPIView,CategoryListAPIView, CategoryDetailAPIView, CountryListAPIView, CountryDetailAPIView, DirectorListAPIView, DirectorDetailAPIView, ActorDetailAPIView, ActorListAPIView,GenreListAPIView,
                    MovieListAPIView, MovieDetailAPIView, RatingViewSet, ReviewCreateAPIView, ReviewLikeViewSet, GenreDetailAPIView,
                    FavoriteViewSet, FavoriteMovieViewSet, HistoryViewSet, RegisterView, LogoutView, LoginView)

router = routers.SimpleRouter()
router.register("ratings", RatingViewSet)
router.register("review-likes", ReviewLikeViewSet)
router.register("favorites", FavoriteViewSet)
router.register("favorite-movies", FavoriteMovieViewSet)
router.register("history", HistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('user/', UserProfileListAPIView.as_view(), name='user_list'),
    path('user/<int:pk>/', UserProfileDetailAPIView.as_view(), name='user_detail'),
    path('category/', CategoryListAPIView.as_view(), name='category_list'),
    path('category/<int:pk>/', CategoryDetailAPIView.as_view(), name='category_detail'),
    path('genre/', GenreListAPIView.as_view(), name='genre_list'),
    path('genre/<int:pk>', GenreDetailAPIView.as_view(), name='genre_detail'),
    path('country/', CountryListAPIView.as_view(), name='country_list'),
    path('country/<int:pk>', CountryDetailAPIView.as_view(), name='country_detail'),
    path('director/', DirectorListAPIView.as_view(), name='director_list'),
    path('director/<int:pk>', DirectorDetailAPIView.as_view(), name='director_detail'),
    path('actor/', ActorListAPIView.as_view(), name='actor_list'),
    path('actor/<int:pk>', ActorDetailAPIView.as_view(), name='actor_detail'),
    path('movie/', MovieListAPIView.as_view(), name='movie_list'),
    path('movie/<int:pk>', MovieDetailAPIView.as_view(), name='movie_detail'),
    path('reviews', ReviewCreateAPIView.as_view(), name='review_create')
]