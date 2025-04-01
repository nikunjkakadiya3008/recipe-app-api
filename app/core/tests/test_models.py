from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models
from unittest.mock import patch

class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        email = "test@example.com"
        password = "test123"

        user = get_user_model().objects.create_user(
            email=email ,
            password= password
        )

        self.assertEqual(user.email , email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        Sample = [
            ["test1@EXAMPLE.COM" , "test1@example.com"],
            ["test2@EXAmPLE.COM" , "test2@example.com"],
            ["TeSt3@EXAmPLE.COM" , "test3@example.com"],
        ]
        for email , expected in Sample:
            user = get_user_model().objects.create_user(email , "sample123")

            self.assertEqual(user.email , expected)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("" , "sample123")

    def test_super_user(self):
        user = get_user_model().objects.create_superuser(email="test@example.com" ,password="sample123")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        user = get_user_model().objects.create_user(email = 'test@email.com' , password='sample123')

        recipe = models.Recipe.objects.create(
            user = user,
            title = 'sample recipe name',
            time_minutes = 5,
            price = Decimal('5.50') ,
            description = 'Sample Recipe description'
        )

        self.assertEqual(str(recipe) , recipe.title)

    def test_create_ingredient(self):
        user = get_user_model().objects.create_user(email='test@example.com' , password='12345')

        ingredient = models.Ingredient.objects.create(
            user = user,
            name= 'ingredient1'
        )
        self.assertEqual(str(ingredient) , 'ingredient1')

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')