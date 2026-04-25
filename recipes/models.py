from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User


class Tag(models.Model):
    """Cuisine types and dietary tags e.g. Italian, Vegan, Gluten-Free"""
    class TagType(models.TextChoices):
        CUISINE  = 'cuisine',  'Cuisine'
        DIETARY  = 'dietary',  'Dietary'
        GENERAL  = 'general',  'General'

    name     = models.CharField(max_length=50, unique=True)
    slug     = models.SlugField(max_length=50, unique=True)
    tag_type = models.CharField(
        max_length=10,
        choices=TagType.choices,
        default=TagType.GENERAL,
    )

    def __str__(self):
        return f"{self.name} ({self.tag_type})"

    class Meta:
        ordering = ['name']


class Recipe(models.Model):
    """Core recipe model — owned by a Creator"""

    class Difficulty(models.TextChoices):
        EASY   = 'easy',   'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD   = 'hard',   'Hard'

    # Ownership
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        limit_choices_to={'role': 'creator'},
    )

    # Basic info
    title       = models.CharField(max_length=200)
    description = models.TextField()
    difficulty  = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
    )

    # Time fields (in minutes)
    prep_time  = models.PositiveIntegerField(help_text='Preparation time in minutes')
    cook_time  = models.PositiveIntegerField(help_text='Cooking time in minutes')
    servings   = models.PositiveIntegerField(default=1)

    # Media
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=True,
    )

    # Visibility
    is_public = models.BooleanField(default=True)

    # Tags (cuisine, dietary, etc.)
    tags = models.ManyToManyField(Tag, blank=True, related_name='recipes')

    # Tracking
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Helper property — total time
    @property
    def total_time(self):
        return self.prep_time + self.cook_time

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    class Meta:
        ordering = ['-created_at']


class Ingredient(models.Model):
    """Each ingredient line belongs to one recipe"""
    recipe   = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )
    name     = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)  # e.g. "2 cups", "1 tbsp"
    order    = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.quantity} {self.name}"

    class Meta:
        ordering = ['order']


class RecipeStep(models.Model):
    """Ordered step-by-step instructions for a recipe"""
    recipe      = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='steps',
    )
    step_number = models.PositiveIntegerField()
    instruction = models.TextField()
    image       = models.ImageField(
        upload_to='steps/',
        null=True,
        blank=True,
        help_text='Optional image for this step',
    )

    def __str__(self):
        return f"Step {self.step_number} of {self.recipe.title}"

    class Meta:
        ordering  = ['step_number']
        unique_together = ['recipe', 'step_number']


class Bookmark(models.Model):
    """Visitors save recipes they like"""
    user   = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookmarks',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='bookmarks',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bookmarked {self.recipe.title}"

    class Meta:
        # A user can only bookmark a recipe once
        unique_together = ['user', 'recipe']
        ordering        = ['-created_at']


class Rating(models.Model):
    """Visitors rate and review recipes 1-5"""
    user   = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    score  = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review     = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title} {self.score}/5"

    class Meta:
        # A user can only rate a recipe once
        unique_together = ['user', 'recipe']
        ordering        = ['-created_at']