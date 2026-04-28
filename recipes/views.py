from rest_framework import generics, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q

from .models import Tag, Recipe, Ingredient, RecipeStep, Bookmark, Rating
from .serializers import (
    TagSerializer, RecipeListSerializer, RecipeDetailSerializer,
    IngredientWriteSerializer, RecipeStepWriteSerializer,
    BookmarkSerializer, RatingSerializer,
)
from .permissions import IsCreatorOrReadOnly, IsOwnerOrReadOnly


# ─── Tags ────────────────────────────────────────────────────────────────────

class TagListView(generics.ListCreateAPIView):
    queryset         = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ─── Recipes ─────────────────────────────────────────────────────────────────

class RecipeListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsCreatorOrReadOnly]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'description', 'author__username']
    ordering_fields    = ['created_at', 'prep_time', 'cook_time', 'view_count']

    def get_serializer_class(self):
        return RecipeDetailSerializer if self.request.method == 'POST' else RecipeListSerializer

    def get_queryset(self):
        user = self.request.user
        qs   = Recipe.objects.select_related('author').prefetch_related('tags', 'ratings', 'bookmarks')

        # Unauthenticated users only see public recipes
        if not user.is_authenticated:
            qs = qs.filter(is_public=True)
        # Creators see their own private recipes + all public ones
        elif user.is_creator:
            qs = qs.filter(Q(is_public=True) | Q(author=user))
        # Visitors and admins see all public recipes
        else:
            qs = qs.filter(is_public=True)

        # --- Filters from query params ---
        tag_slug   = self.request.query_params.get('tag')
        cuisine    = self.request.query_params.get('cuisine')
        dietary    = self.request.query_params.get('dietary')
        max_time   = self.request.query_params.get('max_time')
        difficulty = self.request.query_params.get('difficulty')
        min_rating = self.request.query_params.get('min_rating')

        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        if cuisine:
            qs = qs.filter(tags__slug=cuisine, tags__tag_type='cuisine')
        if dietary:
            qs = qs.filter(tags__slug=dietary, tags__tag_type='dietary')
        if max_time:
            qs = qs.filter(prep_time__lte=int(max_time))
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        if min_rating:
            qs = qs.annotate(avg=Avg('ratings__score')).filter(avg__gte=float(min_rating))

        return qs.distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = RecipeDetailSerializer
    permission_classes = [IsCreatorOrReadOnly]

    def get_queryset(self):
        return Recipe.objects.select_related('author').prefetch_related(
            'tags', 'ingredients', 'steps', 'ratings', 'bookmarks'
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count on every retrieve
        Recipe.objects.filter(pk=instance.pk).update(view_count=instance.view_count + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ─── Ingredients ─────────────────────────────────────────────────────────────

class IngredientListCreateView(generics.ListCreateAPIView):
    serializer_class   = IngredientWriteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])

    def get_queryset(self):
        return Ingredient.objects.filter(recipe=self.get_recipe())

    def perform_create(self, serializer):
        recipe = self.get_recipe()
        # Only the recipe author can add ingredients
        if recipe.author != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not the author of this recipe.")
        serializer.save(recipe=recipe)


class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = IngredientWriteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Ingredient.objects.filter(recipe__pk=self.kwargs['recipe_pk'])


# ─── Steps ───────────────────────────────────────────────────────────────────

class RecipeStepListCreateView(generics.ListCreateAPIView):
    serializer_class   = RecipeStepWriteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_recipe(self):
        return get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'])

    def get_queryset(self):
        return RecipeStep.objects.filter(recipe=self.get_recipe())

    def perform_create(self, serializer):
        recipe = self.get_recipe()
        if recipe.author != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not the author of this recipe.")
        serializer.save(recipe=recipe)


class RecipeStepDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = RecipeStepWriteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return RecipeStep.objects.filter(recipe__pk=self.kwargs['recipe_pk'])


# ─── Bookmarks ───────────────────────────────────────────────────────────────

class BookmarkToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, recipe_pk):
        recipe   = get_object_or_404(Recipe, pk=recipe_pk, is_public=True)
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if not created:
            bookmark.delete()
            return Response({'status': 'removed'}, status=status.HTTP_200_OK)
        return Response({'status': 'bookmarked'}, status=status.HTTP_201_CREATED)


class BookmarkListView(generics.ListAPIView):
    serializer_class   = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('recipe')


# ─── Ratings ─────────────────────────────────────────────────────────────────

class RatingListCreateView(generics.ListCreateAPIView):
    serializer_class   = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Rating.objects.filter(recipe__pk=self.kwargs['recipe_pk'])

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_pk'], is_public=True)
        # Check if user already rated this recipe
        if Rating.objects.filter(user=self.request.user, recipe=recipe).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You have already rated this recipe.")
        serializer.save(user=self.request.user, recipe=recipe)


class RatingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = RatingSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Rating.objects.filter(recipe__pk=self.kwargs['recipe_pk'])


# ─── Creator Dashboard ────────────────────────────────────────────────────────

class CreatorDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_creator:
            return Response(
                {'detail': 'Only creators can access the dashboard.'},
                status=status.HTTP_403_FORBIDDEN
            )

        recipes = Recipe.objects.filter(author=request.user).annotate(
            avg_rating     = Avg('ratings__score'),
            bookmark_count = Count('bookmarks'),
        ).values(
            'id', 'title', 'image' 'is_public', 'view_count',
            'avg_rating', 'bookmark_count', 'created_at',
        )

        summary = {
            'total_recipes'    : Recipe.objects.filter(author=request.user).count(),
            'total_views'      : sum(r['view_count'] for r in recipes),
            'total_bookmarks'  : sum(r['bookmark_count'] or 0 for r in recipes),
            'recipes'          : list(recipes),
        }
        return Response(summary)