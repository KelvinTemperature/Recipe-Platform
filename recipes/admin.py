from django.contrib import admin
from .models import Tag, Recipe, Ingredient, RecipeStep, Bookmark, Rating


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display  = ['title', 'author', 'difficulty', 'is_public',
                     'prep_time', 'cook_time', 'view_count', 'created_at']
    list_filter   = ['difficulty', 'is_public', 'tags']
    search_fields = ['title', 'author__username']
    inlines       = [IngredientInline, RecipeStepInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug', 'tag_type']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'created_at']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe', 'score', 'created_at']