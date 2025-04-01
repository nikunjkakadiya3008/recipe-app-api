from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_test(self):
        payload = {
            'email':'abc@example.com',
            'password' :'12345',
            'name':'Test'
        }
        res =self.client.post(CREATE_USER_URL , payload)

        user = get_user_model().objects.get(email = payload['email'])
        self.assertEqual(res.status_code , status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password' , res.data)

    def test_user_exist(self):
        payload = {
            'email':'abc@example.com',
            'password' :'1234',
            'name':'Test'
        }
        user = create_user(**payload)
        res = self.client.post(CREATE_USER_URL , payload)
        self.assertEqual(res.status_code , status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        payload = {
            'email':'abc@example.com',
            'password' :'1234',
            'name':'Test'
        }
        login = {
            'email':'abc@example.com',
            'password' :'1234'
        }
        user = create_user(**payload)
        res = self.client.post(TOKEN_URL , login)
        self.assertIn('token',res.data)
        self.assertEqual(res.status_code , status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        payload = {
            'email':'abc@example.com',
            'password' :'1234',
            'name':'Test'
        }
        login = {
            'email':'abc@example.com',
            'password' :'123'
        }
        user = create_user(**payload)
        res = self.client.post(TOKEN_URL , login)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code , status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        payload = {
            'email':'abc@example.com',
            'password' :'1234',
            'name':'Test'
        }
        login = {
            'email':'abc@example.com',
            'password' :''
        }
        user = create_user(**payload)
        res = self.client.post(TOKEN_URL , login)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code , status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code , status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    def setUp(self):
        self.user = create_user(
            email = 'abc@example.com' ,
            name ='Test',
            password='test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user = self.user)

    def test_retrieve_profile_succesfully(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code , status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name':self.user.name,
            'email':self.user.email,
        } )
    def test_post_me_not_allowed(self):
        res = self.client.post(ME_URL ,{'name' :'Test'})

        self.assertEqual(res.status_code , status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        payload = {
            'name':'Test2',
            'password':'Test321'
        }
        res = self.client.patch(ME_URL , payload)

        self.user.refresh_from_db()
        self.assertEqual(payload['name'] , self.user.name)
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code , status.HTTP_200_OK)