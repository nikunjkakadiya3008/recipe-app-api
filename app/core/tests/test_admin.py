from django.test import TestCase , Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='abc@example.com',
            password="1234"
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='12345',
            name='pankaj'
        )

    def test_user_list(self):
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
        self.assertEqual(res.status_code, 200)

    def test_edit_user(self):
        url = reverse("admin:core_user_change" , args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code , 200)

    def test_create_user_page(self):
        url = reverse("admin:core_user_add")
        res = self.client.get(url)
        self.assertEqual(res.status_code , 200)