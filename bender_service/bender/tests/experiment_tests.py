from rest_framework import status
from bender.models import Experiment, Trial, Algo
from django.db import transaction
from django.conf import settings
from .helpers import BenderTestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class ExperimentViewsTests(BenderTestCase):

    """Logging"""

    def test_experiment_not_logged(self):
        response = self.client.get("/api/experiments/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    """ LIST """

    def test_list_experiment(self):
        self.client.login(username="Toto1", password="123456")

        response = self.client.get("/api/experiments/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_experiment_with_owner(self):
        self.client.login(username=self.user1.username, password="123456")

        response = self.client.get("/api/experiments/?owner={}".format(self.user1.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"],
                         self.user1.experiments.count())

    def test_list_experiment_with_wrong_owner(self):
        self.client.login(username=self.user1.username, password="123456")

        response = self.client.get("/api/experiments/?owner={}".format(self.user2.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_experiment_shared_with(self):
        self.client.login(username=self.user2.username, password="123456")
        self.assertEqual(Experiment.objects.filter(shared_with=self.user2).count() >= 1, True)
        response = self.client.get("/api/experiments/?shared_with={}".format(self.user2.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"],
                         Experiment.objects.filter(shared_with=self.user2).count())

    def test_list_experiment_shared_with_wrong_owner(self):
        self.client.login(username=self.user1.username, password="123456")
        self.assertEqual(Experiment.objects.filter(shared_with=self.user2).count() >= 1, True)
        response = self.client.get("/api/experiments/?shared_with={}".format(self.user2.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    """ CREATE """

    def test_create_experiment(self):
        self.client.login(username="Toto1", password="123456")
        n = self.user1.experiments.count()
        data = {
            'name': "This is my experiment 6",
            'metrics': [{'metric_name': 'lol', 'type': 'reward'}, {'metric_name': 'lol2', 'type': 'reward'}],
        }
        response = self.client.post("/api/experiments/", data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Experiment.objects.filter(owner=self.user1).count(), n + 1)
        self.user1.refresh_from_db()

    def test_create_experiment_throttling(self):
        self.client.login(username="Toto1", password="123456")
        with transaction.atomic():
            for i in range(settings.BENDER_MAX_EXPERIMENT_PER_USER):
                Experiment.objects.create(
                    name="This is my experiment {}".format(i + 4561),
                    metrics=[{"metric_name": "lol", "type": "reward"}],
                    owner=self.user1,
                )

        data = {
            'name': "This is my experiment 6",
            'metrics': [{'metric_name': 'lol', 'type': 'reward'}, {'metric_name': 'lol2', 'type': 'reward'}],
        }
        response = self.client.post("/api/experiments/", data=data)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_create_experiment_no_metrics(self):
        self.client.login(username="Toto1", password="123456")
        data = {
            'name': "This is my experiment 6",
            'metrics': [],
        }
        response = self.client.post("/api/experiments/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_experiment_bad_metrics(self):
        self.client.login(username="Toto1", password="123456")
        data = {
            'name': "This is my experiment 6",
            'metrics': {"lol"},
        }
        response = self.client.post("/api/experiments/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'name': "This is my experiment 6",
            'metrics': ["lol"],
        }
        response = self.client.post("/api/experiments/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'name': "This is my experiment 6",
            'metrics': [{"lol": "2"}],
        }
        response = self.client.post("/api/experiments/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'name': "This is my experiment 6",
            'metrics': [{"metric_name": "accuracy", "type": "lol"}],
        }
        response = self.client.post("/api/experiments/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'name': "This is my experiment 6",
            'metrics': [{"metric_name": "accuracy", "type": "reward"},
                        {"metric_name": "accuracy", "type": "reward"}]
        }
        response = self.client.post("/api/experiments/", data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_experiment_same_name(self):
        self.client.login(username="Toto1", password="123456")
        data = {
            'name': "This is my experiment 5",
            'metrics': [{'metric_name': 'lol', 'type': 'reward'}, {'metric_name': 'lol2', 'type': 'reward'}],
        }
        response = self.client.post("/api/experiments/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    """ UPDATE """

    def test_update_experiment(self):
        self.client.login(username="Toto1", password="123456")
        experiment = self.user1.experiments.all().first()
        n = self.user1.experiments.count()
        data = {
            'description': "This is my experiment 6",
            'dataset': "Really cool",
            'dataset_parameters': {'lol': 1},
            'shared_with': [self.user2.username],
        }
        response = self.client.patch("/api/experiments/{}/".format(experiment.pk),
                                     data=data,
                                     )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user1.experiments.count(), n)
        experiment.refresh_from_db()
        self.assertEqual(experiment.description, "This is my experiment 6")
        self.assertEqual(experiment.dataset, "Really cool")
        self.assertEqual(experiment.dataset_parameters, {'lol': 1})
        self.assertEqual([user.username for user in experiment.shared_with.all()], [self.user2.username])

    def test_update_experiment_owner_in_shared_with(self):
        self.client.login(username="Toto1", password="123456")
        data = {
            'description': "This is my experiment 6",
            'dataset': "Really cool",
            'shared_with': [self.user1.username]
        }
        response = self.client.patch("/api/experiments/{}/".format(
            self.user1.experiments.all()[0].pk), data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_experiment_shared_with_throttling(self):
        self.client.login(username="Toto1", password="123456")
        with transaction.atomic():
            usernames = []
            for i in range(settings.BENDER_MAX_SHARED_WITH_PER_EXPERIMENT + 1):
                usernames.append(User.objects.create_user(
                    username="Toto{}".format(i + 1000),
                    password="123456",
                    email="toto{}@gmail.com".format(i + 1000)
                ).username)
        data = {
            'shared_with': usernames
        }
        response = self.client.patch("/api/experiments/{}/".format(
            self.user1.experiments.all()[0].pk), data=data)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_update_experiment_owner_in_shared_with_unknown_user(self):
        self.client.login(username="Toto1", password="123456")
        data = {
            'description': "This is my experiment 6",
            'dataset': "Really cool",
            'shared_with': ["babar"]
        }
        response = self.client.patch("/api/experiments/{}/".format(
            self.user1.experiments.all()[0].pk), data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_experiment_try_to_force_owner(self):
        self.client.login(username="Toto1", password="123456")
        data = {
            'description': "This is my experiment 6",
            'dataset': "Really cool",
        }
        response = self.client.patch("/api/experiments/{}/".format(
            self.user2.experiments.all()[0].pk), data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_experiment_delete_user_from_shared_with(self):
        """ Scenario when one active user is deleted from shared_with. """
        self.client.login(username="Toto1", password="123456")
        experiment = self.user1.experiments.filter(shared_with=self.user2).first()
        algo_pks = experiment.algos.filter(owner=self.user2).values_list("pk", flat=True)
        trials_pks = experiment.trials.filter(owner=self.user2).values_list("pk", flat=True)
        self.assertEqual(len(algo_pks) > 0, True)
        self.assertEqual(len(trials_pks) > 0, True)
        data = {
            "shared_with": []
        }
        response = self.client.patch("/api/experiments/{}/".format(experiment.pk), data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Algo.objects.filter(pk__in=algo_pks).count() == 0, True)
        self.assertEqual(Trial.objects.filter(pk__in=trials_pks).count() == 0, True)

    def test_update_experiment_user_in_shared_with(self):
        self.client.login(username="Toto2", password="123456")
        experiment = self.user1.experiments.filter(shared_with=self.user2).first()
        data = {
            "name": "lol"
        }
        response = self.client.patch("/api/experiments/{}/".format(experiment.pk),
                                     data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    """ DELETE """

    def test_delete_experiment(self):
        self.client.login(username="Toto1", password="123456")

        n = self.user1.experiments.count()
        response = self.client.delete("/api/experiments/{}/".format(
            self.user1.experiments.all()[0].pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user1.experiments.count(), n - 1)

    def test_delete_experiment_try_to_force_owner(self):
        self.client.login(username="Toto1", password="123456")

        n = self.user2.experiments.count()
        response = self.client.delete("/api/experiments/{}/".format(
            self.user2.experiments.all()[0].pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.user2.experiments.count(), n)

    def test_delete_experiment_user_in_shared_with(self):
        self.client.login(username="Toto2", password="123456")
        experiment = self.user1.experiments.filter(shared_with=self.user2).first()

        response = self.client.delete("/api/experiments/{}/".format(experiment.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    """ RETRIEVE """

    def test_retrieve_experiment(self):
        self.client.login(username="Toto1", password="123456")

        response = self.client.get("/api/experiments/{}/".format(
            self.user1.experiments.all()[0].pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_experiment_try_to_force_owner(self):
        self.client.login(username="Toto1", password="123456")

        response = self.client.get("/api/experiments/{}/".format(
            self.user2.experiments.all()[0].pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_experiment_user_in_shared_with(self):
        self.client.login(username="Toto2", password="123456")
        experiment = self.user1.experiments.filter(shared_with=self.user2).first()

        response = self.client.get("/api/experiments/{}/".format(experiment.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ExperimentModelTests(BenderTestCase):

    def test_repr(self):
        experiment = Experiment.objects.all()[0]
        self.assertEqual(str(experiment), experiment.name)
