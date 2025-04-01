from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Recipe , Tag , Ingredient
from recipe.serializers import RecipeSerializer , RecipeDetailSerializer , IngredientSerializer
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
import tempfile
import os

from PIL import Image

RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    return reverse('recipe:recipe-detail' , args=[recipe_id])

def create_recipe(user , **params):
    default = {
            'title' : 'sample recipe name',
            'time_minutes' : 5,
            'price' : Decimal('5.50') ,
            'description' : 'Sample Recipe description',
            'link' :'http://example.com/recipe.pdf'
    }
    default.update(params)
    recipe = Recipe.objects.create(user = user , **default)
    return recipe

def create_user(email='Test@example.com' , password = '12345'):
    return get_user_model().objects.create_user(email , password)

def image_upload_url(recipe_id):
    """Create and return an image upload URL."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


class PublicRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code , status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user  = create_user(
            email  ='abc@example.com',
            password='sample123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        create_recipe(user = self.user)
        # create_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all()
        serializer= RecipeSerializer(recipes  , many = True)

        self.assertEqual(serializer.data , res.data)
        self.assertEqual(res.status_code , status.HTTP_200_OK)

    def test_recipe_list_limited_to_user(self):
        other_user = create_user(
            email = 'test1@example.com',
            password='12344'
        )

        create_recipe(user = self.user)
        create_recipe(user = other_user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user =self.user)
        serializer = RecipeSerializer(recipes , many = True)
        self.assertEqual(res.data , serializer.data)
        # self.assertEqual()

    def test_get_recipe_detail(self):
        recipe = create_recipe(user = self.user)

        url = detail_url(recipe.id)
        res =self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data , serializer.data)

    def test_create_recipe(self):
        payload = {
            'title':'Sample Recipe',
            'time_minutes':30,
            'price' :Decimal('5.50'),
        }
        res =self.client.post(RECIPE_URL , payload)

        self.assertEqual(res.status_code  , status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])

        for k , v in payload.items():
            self.assertEqual(getattr(recipe , k) , v)

        self.assertEqual(recipe.user , self.user)

    def test_partial_update(self):
        recipe = create_recipe(
            user = self.user,
            title = 'this is sample recipe',
            link = 'https://example.com/pankaj.pdf'
        )
        payload = {'title':'This is updated Title'}

        url = detail_url(recipe.id)
        res =self.client.patch(url , payload)
        self.assertEqual(res.status_code , status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(payload['title'] , recipe.title)
        self.assertEqual( 'https://example.com/pankaj.pdf', recipe.link)
        self.assertEqual(self.user , recipe.user)

    def test_full_update(self):
        recipe = create_recipe(
            user = self.user,
            title = 'this is sample recipe',
            description= 'this is description of sample recipe',
            time_minutes = 10,
            price = Decimal('5.50'),
            link = 'https://example.com/pankaj.pdf'
        )
        payload = {
            'user' : self.user,
            'title' : 'this is Updated recipe',
            'description': 'this is Updated description of sample recipe',
            'time_minutes' : 100,
            'price' : Decimal('7.5'),
            'link' : 'https://example.com/pankaj2.pdf'
        }
        url = detail_url(recipe.id)

        res =self.client.put(url , payload)

        self.assertEqual(res.status_code , status.HTTP_200_OK)

        recipe.refresh_from_db()

        for k , v in payload.items():
            self.assertEqual(getattr(recipe , k) , v)
        self.assertEqual(recipe.user , self.user)

    def test_update_user_returns_error(self):
        recipe = create_recipe(
            user = self.user,
            title = 'this is sample recipe',
            description= 'this is description of sample recipe',
            time_minutes = 10,
            price = Decimal('5.50'),
            link = 'https://example.com/pankaj.pdf'
        )
        Updated_user = create_user(email='abc1@example.com' , password='12345')
        payload ={'user':Updated_user}
        url = detail_url(recipe.id)
        res = self.client.patch(url , payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user , self.user)

    def test_delete_recipe(self):
        recipe = create_recipe(
            user = self.user,
            title = 'this is sample recipe',
            description= 'this is description of sample recipe',
            time_minutes = 10,
            price = Decimal('5.50'),
            link = 'https://example.com/pankaj.pdf'
        )
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code , status.HTTP_204_NO_CONTENT)

    def test_create_tag(self):
        user =create_user()
        tag = Tag.objects.create(
            name = 'Tag1',
            user = user
        )
        self.assertEqual(str(tag) , tag.name)

    def test_create_recipe_with_new_tags(self):
        payload ={
            'title':'pongal',
            'time_minutes':30,
            'price':Decimal('5.50'),
            'tags':[{'name':'break-fast'} , {'name':'Indian'}]
        }
        res = self.client.post(RECIPE_URL, payload , format='json')
        self.assertEqual(res.status_code , status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count() , 2)
        for tag in payload['tags']:
            exist = recipe.tags.filter(
                name = tag['name'],
                user = self.user
            ).exists()
            self.assertTrue(exist)

    def test_create_recipe_with_existing_tags(self):
        Indian = Tag.objects.create(name = 'Indian' , user= self.user)
        payload ={
            'title':'pongal',
            'time_minutes':30,
            'price':Decimal('5.50'),
            'tags':[{'name':'break-fast'} , {'name':'Indian'}]
        }
        res = self.client.post(RECIPE_URL , payload , format='json')
        self.assertEqual(res.status_code , status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count() , 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count() , 2)
        self.assertIn(Indian , recipe.tags.all())
        for tag in payload['tags']:
            exist = recipe.tags.filter(
                name = tag['name'],
                user = self.user
            ).exists()
            self.assertTrue(exist)

    def test_create_tag_on_update(self):
        recipe = create_recipe(user = self.user)

        payload = {'tags':[{'name':'lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url , payload , format='json')

        self.assertEqual(res.status_code , status.HTTP_200_OK)
        tag = Tag.objects.get(user = self.user , name='lunch')
        self.assertIn(tag,recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        lunch_tag = Tag.objects.create(name = 'lunch' , user = self.user)
        recipe = create_recipe(user = self.user)
        recipe.tags.add(lunch_tag)

        new_tag = Tag.objects.create(name= 'BreakFast' , user = self.user)
        payload = {'tags' :[{'name':'BreakFast'}]}
        url = detail_url(recipe.id)
        res= self.client.patch(url ,payload,format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag = Tag.objects.filter(user= self.user)

        self.assertIn(new_tag , recipe.tags.all())
        self.assertNotIn(lunch_tag , recipe.tags.all())

    def test_create_recipe_with_new_ingredients(self):
        payload ={
            'title' : 'sample recipe name',
            'time_minutes' : 5,
            'price' : Decimal('5.50') ,
            'description' : 'Sample Recipe description',
            'link' :'http://example.com/recipe.pdf',
            'ingredients':[{'name':'Cornflower'} , {'name':'Salt'}]
        }
        res = self.client.post(RECIPE_URL , payload , format = 'json')

        self.assertEqual(res.status_code , status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count() , 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count() , 2)

        for key in payload['ingredients']:
            exit = Ingredient.objects.filter(
                user = self.user,
                name= key['name']
            ).exists()
            self.assertTrue(exit)

    def test_create_recipe_with_existing_ingredients(self):
        ingredient = Ingredient.objects.create(name = 'Cornflower' , user = self.user)
        payload ={
            'title' : 'sample recipe name',
            'time_minutes' : 5,
            'price' : Decimal('5.50') ,
            'description' : 'Sample Recipe description',
            'link' :'http://example.com/recipe.pdf',
            'ingredients':[{'name':'Cornflower'} , {'name':'Salt'}]
        }
        res =self.client.post(RECIPE_URL , payload , format = 'json')
        recipes = Recipe.objects.filter(user = self.user)
        self.assertEqual(recipes.count() , 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count() , 2)
        self.assertIn(ingredient  , recipe.ingredients.all())
        for  key  in payload['ingredients']:
            exit = Ingredient.objects.filter(
                name = key['name'],
                user =self.user
            ).exists()
            self.assertTrue(exit)

    def test_create_ingredient_on_update(self):
        recipe = create_recipe(self.user)
        url = detail_url(recipe.id)
        payload = {'ingredients':[{'name':'lemon'},{'name':'milk'}]}
        res =self.client.patch(url , payload , format = 'json')

        self.assertEqual(res.status_code , status.HTTP_200_OK)
        ingredient =Ingredient.objects.get(user = self.user , name = 'lemon')
        self.assertIn( ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        ingredient = Ingredient.objects.create(user= self.user , name = 'lemon')
        recipe = create_recipe(self.user)
        recipe.ingredients.add(ingredient)
        ingredient_2 = Ingredient.objects.create(user = self.user , name = 'chilli')
        payload = {'ingredients':[{'name':'chilli'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url , payload , format='json')

        self.assertEqual(res.status_code , status.HTTP_200_OK)
        self.assertNotIn(ingredient , recipe.ingredients.all())
        self.assertIn(ingredient_2 , recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        ingredient = Ingredient.objects.create(user= self.user , name = 'lemon')
        recipe = create_recipe(self.user)
        recipe.ingredients.add(ingredient)
        payload = {'ingredients':[]}
        url = detail_url(recipe.id)
        res= self.client.patch(url , payload , format= 'json')

        self.assertEqual(res.status_code , status.HTTP_200_OK)
        self.assertEqual(0, recipe.ingredients.count())


class ImageUploadTests(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123',
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_tags(self):
        """Test filtering recipes by tags."""
        r1 = create_recipe(user=self.user, title='Thai Vegetable Curry')
        r2 = create_recipe(user=self.user, title='Aubergine with Tahini')
        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        tag2 = Tag.objects.create(user=self.user, name='Vegetarian')
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title='Fish and chips')

        params = {'tags': f'{tag1.id},{tag2.id}'}
        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_ingredients(self):
        """Test filtering recipes by ingredients."""
        r1 = create_recipe(user=self.user, title='Posh Beans on Toast')
        r2 = create_recipe(user=self.user, title='Chicken Cacciatore')
        in1 = Ingredient.objects.create(user=self.user, name='Feta Cheese')
        in2 = Ingredient.objects.create(user=self.user, name='Chicken')
        r1.ingredients.add(in1)
        r2.ingredients.add(in2)
        r3 = create_recipe(user=self.user, title='Red Lentil Daal')

        params = {'ingredients': f'{in1.id},{in2.id}'}
        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)
