from django.urls import path
from .views import (
    TagListView,
    RecipeListCreateView, RecipeDetailView,
    IngredientListCreateView, IngredientDetailView,
    RecipeStepListCreateView, RecipeStepDetailView,
    BookmarkToggleView, BookmarkListView,
    RatingListCreateView, RatingDetailView,
    CreatorDashboardView,
)

urlpatterns = [
    # Tags
    path('tags/',                        TagListView.as_view(),             name='tag-list'),

    # Recipes
    path('recipes/',                     RecipeListCreateView.as_view(),    name='recipe-list'),
    path('recipes/<int:pk>/',            RecipeDetailView.as_view(),        name='recipe-detail'),

    # Ingredients (nested under recipe)
    path('recipes/<int:recipe_pk>/ingredients/',          IngredientListCreateView.as_view(), name='ingredient-list'),
    path('recipes/<int:recipe_pk>/ingredients/<int:pk>/', IngredientDetailView.as_view(),     name='ingredient-detail'),

    # Steps (nested under recipe)
    path('recipes/<int:recipe_pk>/steps/',          RecipeStepListCreateView.as_view(), name='step-list'),
    path('recipes/<int:recipe_pk>/steps/<int:pk>/', RecipeStepDetailView.as_view(),     name='step-detail'),

    # Bookmarks
    path('recipes/<int:recipe_pk>/bookmark/', BookmarkToggleView.as_view(), name='bookmark-toggle'),
    path('bookmarks/',                        BookmarkListView.as_view(),   name='bookmark-list'),

    # Ratings
    path('recipes/<int:recipe_pk>/ratings/',          RatingListCreateView.as_view(), name='rating-list'),
    path('recipes/<int:recipe_pk>/ratings/<int:pk>/', RatingDetailView.as_view(),     name='rating-detail'),

    # Creator Dashboard
    path('dashboard/', CreatorDashboardView.as_view(), name='creator-dashboard'),
]