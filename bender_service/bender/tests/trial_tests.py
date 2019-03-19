from rest_framework import status
from bender.models import Trial
from django.db import transaction
from django.conf import settings
from .helpers import BenderTestCase
from django.contrib.auth import get_user_model
import numpy as np
User = get_user_model()


class TrialViewsTests(BenderTestCase):

    """Loging"""

    def test_trials_not_logged(self):
        response = self.client.get("/api/trials/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # """ LIST """

    def test_trials_list(self):
        self.client.login(username=self.user1.username, password="123456")
        response = self.client.get("/api/trials/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_trials_list_owner(self):
        self.client.login(username=self.user1.username, password="123456")
        response = self.client.get("/api/trials/?owner={}".format(self.user1.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], self.user1.trials.count())

    def test_trials_list_wrong_owner(self):
        self.client.login(username=self.user1.username, password="123456")
        response = self.client.get("/api/trials/?owner={}".format(self.user2.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_trials_list_experiment(self):
        self.client.login(username=self.user1.username, password="123456")
        experiment = self.user1.experiments.all()[0]
        self.assertEqual(experiment.trials.count() > 0, True)
        response = self.client.get("/api/trials/?experiment={}".format(experiment.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], experiment.trials.count())

    def test_trials_list_experiment_wrong_owner(self):
        self.client.login(username=self.user1.username, password="123456")
        experiment = self.user2.experiments.exclude(shared_with=self.user1)[0]
        response = self.client.get("/api/trials/?experiment={}".format(experiment.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_trials_list_experiment_wrong_owner_but_shared_with(self):
        self.client.login(username=self.user2.username, password="123456")
        experiment = self.user1.experiments.filter(shared_with=self.user2)[0]
        self.assertEqual(experiment.trials.count() > 0, True)
        response = self.client.get("/api/trials/?experiment={}".format(experiment.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], experiment.trials.count())

    def test_trials_list_algo(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user1.algos.all()[0]
        self.assertEqual(algo.trials.count() > 0, True)
        response = self.client.get("/api/trials/?algo={}".format(algo.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], algo.trials.count())

    def test_trials_list_algo_wrong_owner(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user2.algos.exclude(experiment__shared_with=self.user1)[0]
        response = self.client.get("/api/trials/?algo={}".format(algo.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_trials_list_algo_wrong_owner_but_shared_with(self):
        self.client.login(username=self.user2.username, password="123456")
        algo = self.user1.algos.filter(experiment__shared_with=self.user2)[0]
        self.assertEqual(algo.trials.count() > 0, True)
        response = self.client.get("/api/trials/?algo={}".format(algo.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], algo.trials.count())

    def test_trials_list_experiment_order_results(self):
        self.client.login(username=self.user1.username, password="123456")
        experiment = self.user1.experiments.all()[0]
        key = experiment.metrics[0]["metric_name"]
        response = self.client.get(
            "/api/trials/?experiment={}&o_results={}".format(experiment.pk, key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = [trial_data["results"][key] for trial_data in data["results"]]
        self.assertEqual(results, sorted(results))

    def test_trials_list_experiment_revert_order_results(self):
        self.client.login(username=self.user1.username, password="123456")
        experiment = self.user1.experiments.all()[0]
        key = experiment.metrics[0]["metric_name"]
        response = self.client.get(
            "/api/trials/?experiment={}&o_results=-{}".format(experiment.pk, key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = [trial_data["results"][key] for trial_data in data["results"]]
        self.assertEqual(results, sorted(results)[::-1])

    def test_trials_list_algo_order_parameters(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user1.algos.all()[0]
        key = algo.parameters.all()[0].name
        response = self.client.get("/api/trials/?algo={}&o_parameters={}".format(algo.pk, key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = [trial_data["parameters"][key] for trial_data in data["results"]]
        self.assertEqual(results, sorted(results))

    def test_trials_list_algo_revert_order_parameters(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user1.algos.all()[0]
        key = algo.parameters.all()[0].name
        response = self.client.get("/api/trials/?algo={}&o_parameters=-{}".format(algo.pk, key))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = [trial_data["parameters"][key] for trial_data in data["results"]]
        self.assertEqual(results, sorted(results)[::-1])

    # """ CREATE """

    def test_create_trials(self):
        self.client.login(username=self.user1.username, password="123456")
        n = self.user1.trials.count()
        algo = self.user1.algos.first()
        data = {
            'algo': algo.pk,
            'parameters': {'alpha': 10, 'beta': 20, 'gamma': 'kik'},
            'results': {metric["metric_name"]: 15 for metric in algo.experiment.metrics},
            'comment': {"text": "cool results"}
        }
        response = self.client.post("/api/trials/", data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trial.objects.get(pk=response.json()['id']).owner, self.user1)
        self.assertEqual(Trial.objects.get(pk=response.json()['id']).experiment, algo.experiment)
        self.assertEqual(self.user1.trials.count(), n + 1)

    def test_create_trials_throttling(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user1.algos.first()
        with transaction.atomic():
            for i in range(settings.BENDER_MAX_TRIALS_PER_ALGO):
                Trial.objects.create(
                    algo=algo,
                    owner=self.user1,
                    experiment=algo.experiment,
                    results={metric["metric_name"]: 15 for metric in algo.experiment.metrics},
                    parameters={parameter: 15
                                for parameter in algo.parameters.values_list("name", flat=True)},
                )

        data = {
            'algo': algo.pk,
            'parameters': {'alpha': 10, 'beta': 20, 'gamma': 'kik'},
            'results': {metric["metric_name"]: 15 for metric in algo.experiment.metrics},
            'comment': {"text": "cool results"}
        }
        response = self.client.post("/api/trials/", data=data)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_create_trials_none(self):
        self.client.login(username=self.user1.username, password="123456")

        algo = self.user1.algos.first()
        data = {
            'algo': algo.pk,
            'parameters': {'alpha': None, 'beta': 20, 'gamma': 'kik'},
            'results': {metric["metric_name"]: 15 for metric in algo.experiment.metrics},
            'comment': {"text": "cool results"}
        }

        response = self.client.post("/api/trials/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_trials_nan(self):
        self.client.login(username=self.user1.username, password="123456")

        algo = self.user1.algos.first()
        data = {
            'algo': algo.pk,
            'parameters': {'alpha': np.nan, 'beta': 20, 'gamma': 'kik'},
            'results': {metric["metric_name"]: 15 for metric in algo.experiment.metrics},
            'comment': {"text": "cool results"}
        }

        response = self.client.post("/api/trials/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_trials_none_results(self):
        self.client.login(username=self.user1.username, password="123456")

        algo = self.user1.algos.first()
        data = {
            'algo': algo.pk,
            'parameters': {'alpha': 3, 'beta': 20, 'gamma': 'kik'},
            'results': {metric["metric_name"]: None for metric in algo.experiment.metrics},
            'comment': {"text": "cool results"}
        }

        response = self.client.post("/api/trials/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_trials_nan_results(self):
        import numpy as np
        self.client.login(username=self.user1.username, password="123456")

        algo = self.user1.algos.first()
        data = {
            'algo': algo.pk,
            'parameters': {'alpha': 4, 'beta': 20, 'gamma': 'kik'},
            'results': {metric["metric_name"]: np.nan for metric in algo.experiment.metrics},
            'comment': {"text": "cool results"}
        }

        response = self.client.post("/api/trials/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_trials_wrong_algo(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user1.algos.first()
        data = {
            'algo': "lol",
            'parameters': {'alpha': 10, 'beta': 20, 'gamma': 'kik'},
            'results': {metric["metric_name"]: 15 for metric in algo.experiment.metrics},
            'comment': {"text": "cool results"}
        }
        response = self.client.post("/api/trials/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_trials_missing_parameters(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user1.algos.first()
        data = {
            'algo': algo.pk,
            'parameters': {'alpha': 10, 'beta': 20},
            'results': {metric["metric_name"]: 15 for metric in algo.experiment.metrics},
            'comment': {"text": "cool results"}
        }
        response = self.client.post("/api/trials/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_trials_missing_results(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user1.algos.first()
        data = {
            'algo': algo.pk,
            'parameters': {'alpha': 10, 'beta': 20, 'gamma': 'lol'},
            'results': {metric["metric_name"]: 15 for metric in algo.experiment.metrics[:-1]},
            'comment': {"text": "cool results"}
        }
        response = self.client.post("/api/trials/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_trials_other_user_algo(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user2.algos.first()
        data = {
            'algo': algo.pk,
            'parameters': {'alpha': 10, 'beta': 20},
            'results': {metric["metric_name"]: 15 for metric in algo.experiment.metrics[:-1]},
            'comment': {"text": "cool results"}
        }
        response = self.client.post("/api/trials/", data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_trials_no_algo(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user1.algos.first()
        data = {
            'parameters': {'alpha': 10, 'beta': 20, 'gamma': 'lol'},
            'results': {metric["metric_name"]: 15 for metric in algo.experiment.metrics[:-1]},
            'comment': {"text": "cool results"}
        }
        response = self.client.post("/api/trials/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # # """ DELETE """

    def test_delete_trials(self):
        self.client.login(username=self.user1.username, password="123456")

        n = self.user1.trials.count()
        response = self.client.delete("/api/trials/{}/".format(
            self.user1.trials.all()[0].pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user1.trials.count(), n - 1)

    def test_delete_trials_try_to_force_owner(self):
        self.client.login(username=self.user1.username, password="123456")

        n = self.user2.trials.count()
        response = self.client.delete("/api/trials/{}/".format(
            self.user2.trials.all()[0].pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.user2.trials.count(), n)

    # # """ RETRIEVE """

    def test_retrieve_trials(self):
        self.client.login(username=self.user1.username, password="123456")

        response = self.client.get("/api/trials/{}/".format(
            self.user1.trials.all()[0].pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_trials_wrong_owner(self):
        self.client.login(username=self.user1.username, password="123456")

        response = self.client.get("/api/trials/{}/".format(
            self.user2.trials.all()[0].pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TrialModelTests(BenderTestCase):

    def test_repr(self):
        str(self.user1.trials.all()[0])
