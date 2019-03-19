from rest_framework import status
from .helpers import BenderTestCase


class UserViewsTests(BenderTestCase):

    """Logging"""

    def test_user_not_logged(self):
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    """ LIST """

    def test_list_user(self):
        self.client.login(username="Toto1", password="123456")

        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.json()["results"][0].keys()), ["username"])

    def test_list_user_admin(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("id" in set(response.json()["results"][0].keys()), True)
        self.assertEqual("username" in set(response.json()["results"][0].keys()), True)
        self.assertEqual("email" in set(response.json()["results"][0].keys()), True)

    """ UPDATE """

    def test_update_user(self):
        self.client.login(username=self.user2.username, password="123456")
        n_experiments = self.user2.shared_experiments.count()
        self.assertEqual(n_experiments >= 1, True)
        n_algos_total = self.user2.algos.count()
        n_algos_to_delete = sum([experiment.algos.filter(owner=self.user2).count()
                                 for experiment in self.user2.shared_experiments.all()])
        self.assertEqual(n_algos_total >= 1, True)
        self.assertEqual(n_algos_total > n_algos_to_delete, True)
        data = {
            'username': "Toto3",
            'email': "lol@toto.com",
            'shared_experiments': [],
        }
        response = self.client.patch("/api/users/{}/".format(self.user2.pk),
                                     data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.shared_experiments.count(), 0)
        self.assertEqual(self.user2.username, "Toto3")
        self.assertEqual(self.user2.email, "lol@toto.com")
        self.assertEqual(self.user2.algos.count(), n_algos_total - n_algos_to_delete)

    def test_update_user_username_already_exist(self):
        self.client.login(username=self.user1.username, password="123456")

        data = {
            'username': "Toto2",
        }
        response = self.client.patch("/api/users/{}/".format(self.user1.pk),
                                     data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_email_already_exist(self):
        self.client.login(username=self.user1.username, password="123456")

        data = {
            'email': "toto2@gmail.com",
        }
        response = self.client.patch("/api/users/{}/".format(self.user1.pk),
                                     data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_other_user(self):
        self.client.login(username=self.user1.username, password="123456")
        data = {
            'username': "Toto3",
            'email': "lol@toto.com",
            'shared_experiments': [],
        }
        response = self.client.patch("/api/users/{}/".format(self.user2.pk),
                                     data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_add_shared_experiment(self):
        self.client.login(username=self.user1.username, password="123456")
        data = {
            'shared_experiments': [self.user2.experiments.exclude(shared_with=self.user1)[0].pk],
        }
        response = self.client.patch("/api/users/{}/".format(self.user1.pk),
                                     data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_add_own_shared_experiment(self):
        self.client.login(username=self.user1.username, password="123456")
        data = {
            'shared_experiments': [self.user1.experiments.all()[0].pk],
        }
        response = self.client.patch("/api/users/{}/".format(self.user1.pk),
                                     data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # """ DELETE """

    def test_delete_user(self):
        self.client.login(username="Toto1", password="123456")

        response = self.client.delete("/api/users/{}/".format(self.user1.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get("/api/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.login(username="Toto1", password="123456")

        response = self.client.get("/api/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_other_user(self):
        """This would not be nice."""
        self.client.login(username="Toto1", password="123456")

        response = self.client.delete("/api/users/{}/".format(self.user2.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # """ DELETE """

    def test_retrieve_user(self):
        self.client.login(username="Toto1", password="123456")

        response = self.client.get("/api/users/{}/".format(self.user1.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_other_user(self):
        self.client.login(username="Toto1", password="123456")

        response = self.client.get("/api/users/{}/".format(self.user2.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_other_user_admin(self):
        self.client.login(username="admin", password="123456")

        response = self.client.get("/api/users/{}/".format(self.user2.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contact(self):
        self.client.login(username="Toto1", password="123456")

        response = self.client.post("/api/users/contact/", {
            'title': "Some title",
            'content': "Some content",
            'email': "jus@an.email"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)