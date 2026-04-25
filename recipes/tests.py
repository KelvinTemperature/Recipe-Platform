from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Tag, Recipe, Ingredient, RecipeStep, Bookmark, Rating
from accounts.models import User


# ─── Helpers ─────────────────────────────────────────────────────────────────

def create_user(username, role='visitor', password='Testpass123!'):
    return User.objects.create_user(
        username=username,
        email=f'{username}@test.com',
        password=password,
        role=role,
    )

def create_tag(name='Italian', tag_type='cuisine'):
    from django.utils.text import slugify
    return Tag.objects.create(name=name, slug=slugify(name), tag_type=tag_type)

def create_recipe(author, title='Test Recipe', is_public=True):
    return Recipe.objects.create(
        author=author,
        title=title,
        description='A test recipe description',
        difficulty='easy',
        prep_time=10,
        cook_time=20,
        servings=2,
        is_public=is_public,
    )

def get_token(client, username, password='Testpass123!'):
    response = client.post(reverse('login'), {
        'username': username,
        'password': password,
    }, format='json')
    return response.data['access']


# ─── Model Tests ─────────────────────────────────────────────────────────────

class UserModelTest(TestCase):
    """Test 1 — User role helper properties work correctly"""

    def test_role_properties(self):
        creator = create_user('creator1', role='creator')
        visitor = create_user('visitor1', role='visitor')
        admin   = create_user('admin1',   role='admin')

        self.assertTrue(creator.is_creator)
        self.assertFalse(creator.is_visitor)

        self.assertTrue(visitor.is_visitor)
        self.assertFalse(visitor.is_creator)

        self.assertTrue(admin.is_platform_admin)
        self.assertFalse(admin.is_creator)


class RecipeModelTest(TestCase):
    """Test 2 — Recipe total_time property is correct"""

    def test_total_time(self):
        creator = create_user('chef1', role='creator')
        recipe  = create_recipe(creator)
        self.assertEqual(recipe.total_time, 30)  # prep(10) + cook(20)

    """Test 3 — Recipe str representation is correct"""
    def test_str(self):
        creator = create_user('chef2', role='creator')
        recipe  = create_recipe(creator, title='Jollof Rice')
        self.assertEqual(str(recipe), 'Jollof Rice by chef2')


class BookmarkModelTest(TestCase):
    """Test 4 — A user cannot bookmark the same recipe twice"""

    def test_unique_bookmark(self):
        from django.db import IntegrityError
        creator = create_user('chef3', role='creator')
        visitor = create_user('visitor2', role='visitor')
        recipe  = create_recipe(creator)

        Bookmark.objects.create(user=visitor, recipe=recipe)

        with self.assertRaises(IntegrityError):
            Bookmark.objects.create(user=visitor, recipe=recipe)


class RatingModelTest(TestCase):
    """Test 5 — A user cannot rate the same recipe twice"""

    def test_unique_rating(self):
        from django.db import IntegrityError
        creator = create_user('chef4', role='creator')
        visitor = create_user('visitor3', role='visitor')
        recipe  = create_recipe(creator)

        Rating.objects.create(user=visitor, recipe=recipe, score=4)

        with self.assertRaises(IntegrityError):
            Rating.objects.create(user=visitor, recipe=recipe, score=5)


# ─── Auth & Permission Tests ──────────────────────────────────────────────────

class AuthPermissionTest(APITestCase):
    """Test 6 — Unauthenticated users cannot create recipes"""

    def test_unauthenticated_cannot_create_recipe(self):
        url      = reverse('recipe-list')
        response = self.client.post(url, {
            'title'      : 'Unauthorized Recipe',
            'description': 'Should fail',
            'prep_time'  : 10,
            'cook_time'  : 10,
            'servings'   : 2,
            'difficulty' : 'easy',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CreatorPermissionTest(APITestCase):
    """Test 7 — Only creators can create recipes, visitors cannot"""

    def setUp(self):
        self.creator = create_user('chef5', role='creator')
        self.visitor = create_user('visitor4', role='visitor')

    def test_visitor_cannot_create_recipe(self):
        token = get_token(self.client, 'visitor4')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url      = reverse('recipe-list')
        response = self.client.post(url, {
            'title'      : 'Visitor Recipe',
            'description': 'Should fail',
            'prep_time'  : 10,
            'cook_time'  : 10,
            'servings'   : 2,
            'difficulty' : 'easy',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_creator_can_create_recipe(self):
        token = get_token(self.client, 'chef5')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url      = reverse('recipe-list')
        response = self.client.post(url, {
            'title'      : 'Creator Recipe',
            'description': 'This should work',
            'prep_time'  : 15,
            'cook_time'  : 30,
            'servings'   : 4,
            'difficulty' : 'medium',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# ─── Recipe View Tests ────────────────────────────────────────────────────────

class RecipeVisibilityTest(APITestCase):
    """Test 8 — Private recipes are hidden from other users"""

    def setUp(self):
        self.creator = create_user('chef6', role='creator')
        self.visitor = create_user('visitor5', role='visitor')
        self.private = create_recipe(self.creator, title='Secret Recipe', is_public=False)
        self.public  = create_recipe(self.creator, title='Public Recipe',  is_public=True)

    def test_visitor_cannot_see_private_recipe(self):
        token = get_token(self.client, 'visitor5')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url      = reverse('recipe-list')
        response = self.client.get(url)
        titles   = [r['title'] for r in response.data['results']]
        self.assertNotIn('Secret Recipe', titles)
        self.assertIn('Public Recipe', titles)

    def test_creator_can_see_own_private_recipe(self):
        token = get_token(self.client, 'chef6')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url      = reverse('recipe-list')
        response = self.client.get(url)
        titles   = [r['title'] for r in response.data['results']]
        self.assertIn('Secret Recipe', titles)


class RecipeOwnershipTest(APITestCase):
    """Test 9 — Only the recipe author can edit or delete their recipe"""

    def setUp(self):
        self.author  = create_user('chef7', role='creator')
        self.other   = create_user('chef8', role='creator')
        self.recipe  = create_recipe(self.author, title='Author Recipe')

    def test_non_author_cannot_edit_recipe(self):
        token = get_token(self.client, 'chef8')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url      = reverse('recipe-detail', kwargs={'pk': self.recipe.pk})
        response = self.client.patch(url, {'title': 'Hacked Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_edit_recipe(self):
        token = get_token(self.client, 'chef7')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url      = reverse('recipe-detail', kwargs={'pk': self.recipe.pk})
        response = self.client.patch(url, {'title': 'Updated Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')


# ─── Bookmark Tests ───────────────────────────────────────────────────────────

class BookmarkTest(APITestCase):
    """Test 10 — Bookmark toggle works correctly"""

    def setUp(self):
        self.creator = create_user('chef9',    role='creator')
        self.visitor = create_user('visitor6', role='visitor')
        self.recipe  = create_recipe(self.creator)

    def test_bookmark_and_unbookmark(self):
        token = get_token(self.client, 'visitor6')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('bookmark-toggle', kwargs={'recipe_pk': self.recipe.pk})

        # First call — should bookmark
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'bookmarked')

        # Second call — should remove bookmark
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'removed')


# ─── Rating Tests ─────────────────────────────────────────────────────────────

class RatingTest(APITestCase):
    """Test 11 — Users can rate a recipe only once"""

    def setUp(self):
        self.creator = create_user('chef10',   role='creator')
        self.visitor = create_user('visitor7', role='visitor')
        self.recipe  = create_recipe(self.creator)

    def test_cannot_rate_twice(self):
        token = get_token(self.client, 'visitor7')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('rating-list', kwargs={'recipe_pk': self.recipe.pk})

        # First rating — should succeed
        self.client.post(url, {'score': 4, 'review': 'Great!'}, format='json')

        # Second rating — should fail
        response = self.client.post(url, {'score': 5, 'review': 'Amazing!'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ─── Dashboard Tests ──────────────────────────────────────────────────────────

class DashboardTest(APITestCase):
    """Test 12 — Visitors cannot access creator dashboard"""

    def setUp(self):
        self.visitor = create_user('visitor8', role='visitor')

    def test_visitor_cannot_access_dashboard(self):
        token = get_token(self.client, 'visitor8')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url      = reverse('creator-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DashboardCreatorTest(APITestCase):
    """Test 13 — Creator dashboard returns correct data"""

    def setUp(self):
        self.creator = create_user('chef11', role='creator')
        self.recipe1 = create_recipe(self.creator, title='Recipe One')
        self.recipe2 = create_recipe(self.creator, title='Recipe Two')

    def test_dashboard_returns_all_recipes(self):
        token = get_token(self.client, 'chef11')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url      = reverse('creator-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_recipes'], 2)


# ─── Search & Filter Tests ────────────────────────────────────────────────────

class SearchFilterTest(APITestCase):
    """Test 14 — Search by title works correctly"""

    def setUp(self):
        self.creator = create_user('chef12', role='creator')
        create_recipe(self.creator, title='Jollof Rice')
        create_recipe(self.creator, title='Egusi Soup')

    def test_search_by_title(self):
        url      = reverse('recipe-list')
        response = self.client.get(url, {'search': 'Jollof'})
        titles   = [r['title'] for r in response.data['results']]
        self.assertIn('Jollof Rice', titles)
        self.assertNotIn('Egusi Soup', titles)


class FilterByTagTest(APITestCase):
    """Test 15 — Filter recipes by tag slug works correctly"""

    def setUp(self):
        self.creator  = create_user('chef13', role='creator')
        self.tag      = create_tag(name='Nigerian', tag_type='cuisine')
        self.recipe   = create_recipe(self.creator, title='Pounded Yam')
        self.recipe.tags.add(self.tag)

    def test_filter_by_tag(self):
        url      = reverse('recipe-list')
        response = self.client.get(url, {'tag': 'nigerian'})
        titles   = [r['title'] for r in response.data['results']]
        self.assertIn('Pounded Yam', titles)