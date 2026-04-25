from rest_framework import serializers
from django.db.models import Avg
from .models import Tag, Recipe, Ingredient, RecipeStep, Bookmark, Rating


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tag
        fields = ['id', 'name', 'slug', 'tag_type']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Ingredient
        fields = ['id', 'name', 'quantity', 'order']


class RecipeStepSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RecipeStep
        fields = ['id', 'step_number', 'instruction', 'image']


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model  = Rating
        fields = ['id', 'user', 'score', 'review', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class RecipeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views — no nested steps/ingredients"""
    author     = serializers.StringRelatedField(read_only=True)
    tags       = TagSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()

    class Meta:
        model  = Recipe
        fields = [
            'id', 'title', 'author', 'description', 'difficulty',
            'prep_time', 'cook_time', 'total_time', 'servings',
            'image', 'is_public', 'tags', 'view_count',
            'avg_rating', 'bookmark_count', 'created_at',
        ]

    def get_avg_rating(self, obj):
        result = obj.ratings.aggregate(avg=Avg('score'))['avg']
        return round(result, 2) if result else None

    def get_bookmark_count(self, obj):
        return obj.bookmarks.count()


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Full serializer — includes nested ingredients and steps"""
    author      = serializers.StringRelatedField(read_only=True)
    tags        = TagSerializer(many=True, read_only=True)
    tag_ids     = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True,
        source='tags', required=False,
    )
    ingredients = IngredientSerializer(many=True, read_only=True)
    steps       = RecipeStepSerializer(many=True, read_only=True)
    avg_rating  = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()
    is_bookmarked  = serializers.SerializerMethodField()

    class Meta:
        model  = Recipe
        fields = [
            'id', 'title', 'author', 'description', 'difficulty',
            'prep_time', 'cook_time', 'total_time', 'servings',
            'image', 'is_public', 'tags', 'tag_ids',
            'ingredients', 'steps', 'view_count',
            'avg_rating', 'bookmark_count', 'is_bookmarked',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'view_count', 'created_at', 'updated_at']

    def get_avg_rating(self, obj):
        result = obj.ratings.aggregate(avg=Avg('score'))['avg']
        return round(result, 2) if result else None

    def get_bookmark_count(self, obj):
        return obj.bookmarks.count()

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False


class IngredientWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Ingredient
        fields = ['id', 'name', 'quantity', 'order']


class RecipeStepWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RecipeStep
        fields = ['id', 'step_number', 'instruction', 'image']


class BookmarkSerializer(serializers.ModelSerializer):
    recipe = RecipeListSerializer(read_only=True)
    user   = serializers.StringRelatedField(read_only=True)

    class Meta:
        model  = Bookmark
        fields = ['id', 'user', 'recipe', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']