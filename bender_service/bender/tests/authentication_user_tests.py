from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from mock import patch
from django.core import mail
import re
User = get_user_model()


class AuthenticationTests(APITestCase):

    # TESTS DJANGO REST AUTH

    def setUp(self):
        self.user = User.objects.create_user(
            username="Toto",
            password="123456",
            email="toto@gmail.com"
        )

    def test_authentication_api(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_admin(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_login_with_username(self):
        data = {
            "username": "Toto",
            "password": "123456",
        }
        response = self.client.post("/login/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_jwt(self):
        data = {
            "username": "Toto",
            "password": "123456",
        }

        response = self.client.post("/login/", data=data)
        token = response.json()['token']
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

        response = self.client.get("/api/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.credentials(HTTP_AUTHORIZATION="JWT {}".format(token))
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_email(self):
        data = {
            "email": "toto@gmail.com",
            "password": "123456",
        }
        response = self.client.post("/login/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout(self):
        login = self.client.login(username="Toto", password="123456")
        self.assertEqual(login, True)

        response = self.client.post("/logout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset(self):
        data = {
            "email": "toto@gmail.com"
        }
        response = self.client.post("/password/reset/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Catch email and parse it
        confirmation_email_body = mail.outbox[0].body
        r = re.compile('password/reset/(.*?)/(.*?)/\\n\\nYour')
        uid, token = r.search(confirmation_email_body).groups(1)

        # Test verify email
        data = {
            "uid": uid,
            "token": token,
            "new_password1": "123456",
            "new_password2": "123456",
        }
        response = self.client.post("/password/reset/confirm/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_change(self):
        login = self.client.login(username="Toto", password="123456")
        self.assertEqual(login, True)

        data = {
            "new_password1": "654321",
            "new_password2": "654321",
            "old_password": "123456",
        }
        response = self.client.post("/password/change/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

        login = self.client.login(username="Toto", password="123456")
        self.assertEqual(login, False)

        login = self.client.login(username="Toto", password="654321")
        self.assertEqual(login, True)

    def test_user_get(self):
        login = self.client.login(username="Toto", password="123456")
        self.assertEqual(login, True)

        response = self.client.get("/user/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_patch(self):
        login = self.client.login(username="Toto", password="123456")
        self.assertEqual(login, True)

        data = {
            "username": "Toto",
            "first_name": "roger",
        }
        response = self.client.put("/user/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "roger")


class AuthenticationRegistrationTests(APITestCase):

    # TESTS DJANGO REST AUTH REGISTRATION

    def setUp(self):
        self.user = User.objects.create_user(
            username="Toto",
            password="123456",
            email="toto@gmail.com"
        )

    def test_registration_verify_email_and_login(self):
        data = {
            "username": "Toto_bis",
            "email": "toto_bis@gmail.com",
            "password1": "lol123456",
            "password2": "lol123456",
            "tos_accepted": True,
        }
        response = self.client.post("/registration/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Find mail and get key
        confirmation_email_body = mail.outbox[0].body
        r = re.compile('/confirm-email/(.*?)/\\n\\nThank')
        key = r.search(confirmation_email_body).group(1)

        # Test verify email
        data = {
            "key": key
        }
        response = self.client.post("/registration/verify-email/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "username": "Toto_bis",
            "password": "lol123456",
        }
        response = self.client.post("/login/", data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_registration_and_login_fails(self):
        data = {
            "username": "Toto_bis",
            "email": "toto_bis@gmail.com",
            "password1": "lol123456",
            "password2": "lol123456",
            "tos_accepted": True,
        }
        response = self.client.post("/registration/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            "username": "Toto_bis",
            "password": "lol123456",
        }
        response = self.client.post("/login/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_without_tos_fails(self):
        data = {
            "username": "Toto_bis",
            "email": "toto_bis@gmail.com",
            "password1": "lol123456",
            "password2": "lol123456",
        }
        response = self.client.post("/registration/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_same_adress(self):
        data = {
            "username": "Toto_fake",
            "email": "toto@gmail.com",
            "password1": "lol123456",
            "password2": "lol123456",
        }
        response = self.client.post("/registration/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_verify_email_bad_key_no_key(self):
        data = {
            # "key": "123456"
        }
        response = self.client.post("/registration/verify-email/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            "key": "123456"
        }
        response = self.client.post("/registration/verify-email/", data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AuthenticationSocialTests(APITestCase):

    # TESTS DJANGO REST AUTH REGISTRATION

    def setUp(self):
        self.site = Site.objects.get_current()

        # Facebook
        self.site.socialapp_set.create(
            provider="facebook",
            name="facebook",
            client_id="1234567890",
            secret="0987654321",
        )

        # Google
        self.site.socialapp_set.create(
            provider="google",
            name="google",
            client_id="1234567890",
            secret="0987654321",
        )

    # TESTS DJANGO REST AUTH SOCIAL
    def test_registration_facebook(self):
        data = {
            "access_token": "lol",
            "code": "lol",
        }
        response = self.client.post("/facebook/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_google(self):
        data = {
            "access_token": "lol",
            "code": "lol",
        }
        response = self.client.post("/google/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DemoTests(APITestCase):

    @patch('bender.signals.helpers.settings')
    def test_demo_loaded(self, mock_settings):
        mock_settings.BENDER_LOAD_DEMO = True
        self.user = User.objects.create_user(
            username="Toto",
            password="123456",
            email="toto@gmail.com"
        )

        user = User.objects.get(username="Toto")
        self.assertEqual(user.experiments.count(), 1)
        self.assertEqual(user.algos.count(), 2)


class UserTests(APITestCase):

    @patch('bender.signals.helpers.settings')
    def test_demo_loaded(self, mock_settings):
        try:
            self.user = User.objects.create_user(
                password="123456",
                email="toto@gmail.com"
            )
        except Exception as e:
            self.assertEqual(type(e), ValueError)

        try:
            self.user = User.objects.create_superuser(
                password="123456",
                email="toto@gmail.com"
            )
        except Exception as e:
            self.assertEqual(type(e), ValueError)
