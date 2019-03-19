from rest_framework import status
from django.contrib.auth import get_user_model
from bender.models import Algo, Parameter
from django.db import transaction
from django.conf import settings
from django.db.models import Count
from .helpers import BenderTestCase
import uuid

User = get_user_model()


class AlgoViewsTests(BenderTestCase):

    """Loging"""

    def test_algos_not_logged(self):
        response = self.client.get("/api/algos/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # """ LIST """

    def test_algos_list(self):
        self.client.login(username=self.user1.username, password="123456")
        response = self.client.get("/api/algos/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_algos_list_owner(self):
        self.client.login(username=self.user1.username, password="123456")
        n = self.user1.algos.count()
        self.assertEqual(n >= 1, True)
        response = self.client.get("/api/algos/?owner={}".format(self.user1.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], n)

    def test_algos_list_wrong_owner(self):
        self.client.login(username=self.user1.username, password="123456")
        response = self.client.get("/api/algos/?owner={}".format(self.user2.username))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_algos_list_experiment(self):
        self.client.login(username=self.user1.username, password="123456")
        experiment = self.user1.algos.all()[0].experiment

        response = self.client.get("/api/algos/?experiment={}".format(experiment.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], experiment.algos.count())

    def test_algos_list_experiment_wrong_owner(self):
        self.client.login(username=self.user1.username, password="123456")
        experiment = self.user2.experiments.exclude(shared_with=self.user1)[0]

        response = self.client.get("/api/algos/?experiment={}".format(experiment.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_algos_list_experiment_wrong_owner_but_shared_with(self):
        self.client.login(username=self.user2.username, password="123456")
        experiment = self.user1.experiments.filter(shared_with=self.user2)[0]

        response = self.client.get("/api/algos/?experiment={}".format(experiment.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], experiment.algos.count())

    def test_algos_get_last_algo_of_experiment(self):
        self.client.login(username=self.user2.username, password="123456")
        experiment = self.user1.experiments.annotate(Count('algos')).filter(algos__count__gte=2)[0]

        response = self.client.get(
            "/api/algos/?experiment={}&limit=1&o=-date".format(experiment.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["results"][0]["id"], experiment.algos.order_by('-created')[0].pk)

    # """ CREATE """

    def test_create_algos(self):
        self.client.login(username=self.user1.username, password="123456")
        n = self.user1.algos.count()
        data = {
            'experiment': str(self.user1.experiments.all()[0].pk),
            'parameters': [
                {"name": 'alpha', "category": "normal", "search_space": {"mu": 2, "sigma": 3}},
                {"name": 'beta', "category": "normal", "search_space": {"mu": 2, "sigma": 3}},
                {"name": 'gamma', "category": "normal", "search_space": {"mu": 2, "sigma": 3}}
            ],
            'name': "Brand new algorithm."
        }
        response = self.client.post("/api/algos/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Algo.objects.get(name=data["name"]).owner, self.user1)
        self.assertEqual(self.user1.algos.count(), n + 1)
        self.assertEqual(response.json()["is_search_space_defined"], True)

    def test_create_algos_undefined_search_space(self):
        self.client.login(username=self.user1.username, password="123456")
        n = self.user1.algos.count()
        data = {
            'experiment': str(self.user1.experiments.all()[0].pk),
            'parameters': [
                {"name": 'alpha', "category": "normal", "search_space": {"mu": 2, "sigma": 3}},
                {"name": 'beta', "category": "normal", "search_space": {"mu": 2, "sigma": 3}},
                {"name": 'gamma', "category": "normal", "mu": 2, "sigma": 3}
            ],
            'name': "Brand new algorithm."
        }
        response = self.client.post("/api/algos/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Algo.objects.get(name=data["name"]).owner, self.user1)
        self.assertEqual(self.user1.algos.count(), n + 1)
        self.assertEqual(response.json()["is_search_space_defined"], False)

    def test_create_algos_defined_search_space(self):
        self.client.login(username=self.user1.username, password="123456")
        n = self.user1.algos.count()
        data = {
            'experiment': str(self.user1.experiments.all()[0].pk),
            'parameters': [
                {"name": 'alpha', "category": "normal", "search_space": {"mu": 2, "sigma": 3}},
                {"name": 'beta', "category": "normal", "search_space": {"mu": 2, "sigma": 3}},
                {"name": 'gamma', "category": "descriptive"},
            ],
            'name': "Brand new algorithm."
        }
        response = self.client.post("/api/algos/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Algo.objects.get(name=data["name"]).owner, self.user1)
        self.assertEqual(self.user1.algos.count(), n + 1)
        self.assertEqual(response.json()["is_search_space_defined"], True)

    def test_create_algos_throttling(self):
        self.client.login(username=self.user1.username, password="123456")
        experiment = self.user1.experiments.all()[0]
        with transaction.atomic():
            for i in range(settings.BENDER_MAX_ALGO_PER_EXPERIMENT):
                algo = Algo.objects.create(
                    experiment=experiment,
                    owner=self.user1,
                    name="algo {}".format(i + 456)
                )
                Parameter.objects.create(
                    name="alpha",
                    algo=algo,
                )
                Parameter.objects.create(
                    name="beta",
                    algo=algo,
                )
                Parameter.objects.create(
                    name="gamma",
                    algo=algo,
                )
        data = {
            'experiment': str(experiment.pk),
            'parameters': [{"name": 'alpha'}, {"name": 'beta'}, {"name": 'gamma'}],
            'name': "Brand new algorithm."
        }
        response = self.client.post("/api/algos/", data=data)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_create_algos_param_same_name(self):
        self.client.login(username=self.user1.username, password="123456")
        data = {
            'experiment': str(self.user1.experiments.all()[0].pk),
            'parameters': [
                {"name": 'alpha', "category": "normal", "search_space": {"mu": 2, "sigma": 3}},
                {"name": 'alpha', "category": "normal", "search_space": {"mu": 2, "sigma": 3}},
            ],
            'name': "Brand new algorithm."
        }
        response = self.client.post("/api/algos/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_algos_with_owner(self):
        self.client.login(username=self.user1.username, password="123456")
        data = {
            'experiment': str(self.user1.experiments.all()[0].pk),
            'parameters': [{"name": 'alpha'}, {"name": 'beta'}, {"name": 'gamma'}],
            'name': "Brand new algorithm.",
            'owner': self.user1.username,
        }
        response = self.client.post("/api/algos/", data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user1.algos.get(name=data["name"]).owner, self.user1)

    def test_create_algos_shared_with(self):
        self.client.login(username=self.user2.username, password="123456")
        data = {
            'experiment': str(self.user1.experiments.all()[0].pk),
            'parameters': [{"name": 'alpha'}, {"name": 'beta'}, {"name": 'gamma'}],
            'name': "Brand new algorithm."
        }
        # Assert experiment is shared with user 2
        self.assertEqual(
            self.user2 in self.user1.experiments.get(
                name="This is my experiment 5").shared_with.all(),
            True)

        response = self.client.post("/api/algos/", data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user2.algos.get(name=data["name"]).owner, self.user2)

    def test_create_algos_experiment_does_not_exist(self):
        self.client.login(username=self.user1.username, password="123456")
        data = {
            'experiment': str(uuid.uuid4()),
            'parameters': [{"name": 'alpha'}, {"name": 'beta'}, {"name": 'gamma'}],
            'name': "Brand new algorithm."
        }
        response = self.client.post("/api/algos/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_algos_try_to_force_other_user_experiment(self):
        self.client.login(username=self.user1.username, password="123456")
        data = {
            'experiment': str(self.user2.experiments.all()[0].pk),
            'parameters': [{"name": 'alpha'}, {"name": 'beta'}, {"name": 'gamma'}],
            'name': "Brand new algorithm."
        }
        response = self.client.post("/api/algos/", data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_algos_experiment_no_experiment(self):
        self.client.login(username=self.user1.username, password="123456")
        data = {
            'parameters': [{"name": 'alpha'}, {"name": 'beta'}, {"name": 'gamma'}],
            'name': "Brand new algorithm."
        }
        response = self.client.post("/api/algos/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_algos_wrong_params(self):
        self.client.login(username=self.user1.username, password="123456")
        data = {
            'experiment': str(self.user1.experiments.all()[0].pk),
            'parameters': [
                {"name": 'alpha', "category": "normal", "search_space": {"lol": 2, "sigma": 3}},
                {"name": 'beta', "category": "normal", "search_space": {"mu": 2, "sigma": 3}},
                {"name": 'gamma', "category": "normal", "search_space": {"mu": 2, "sigma": 3}}
            ],
            'name': "Brand new algorithm."
        }
        response = self.client.post("/api/algos/", data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # """ UPDATE """

    def test_update_algos(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user1.algos.first()
        new_name = algo.name + " blob"
        data = {
            'name': new_name,
            'parameter': []
        }
        n = self.user1.algos.count()
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user1.algos.count(), n)
        algo.refresh_from_db()
        self.assertEqual(algo.name, new_name)

    def test_update_parameters(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = Algo.objects.create(
            owner=self.user1,
            experiment=self.user1.experiments.all()[0],
            name="new_algo",
        )
        Parameter.objects.create(
            name="uniform_param1",
            algo=algo,
        )
        Parameter.objects.create(
            name="uniform_param2",
            algo=algo,
        )
        Parameter.objects.create(
            name="normal_param1",
            algo=algo,
        )
        Parameter.objects.create(
            name="normal_param2",
            algo=algo,
        )
        Parameter.objects.create(
            name="categorical_param",
            algo=algo,
        )
        data = {
            'parameters': [
                {
                    "name": "categorical_param",
                    "category": "categorical",
                    "search_space": {
                        "values": ["lol", "kol"],
                        "probabilities": [0.4, 0.6],
                    }
                },
                {
                    "name": "normal_param1",
                    "category": "normal",
                    "search_space": {
                        "mu": 3,
                        "sigma": 0.2,
                    }
                },
                {
                    "name": "normal_param2",
                    "category": "lognormal",
                    "search_space": {
                        "mu": 1e3,
                        "sigma": 1e2,
                        "step": 1
                    }
                },
                {
                    "name": "uniform_param1",
                    "category": "uniform",
                    "search_space": {
                        "low": 3,
                        "high": 10,
                        "step": 0.15
                    }
                },
                {
                    "name": "uniform_param2",
                    "category": "loguniform",
                    "search_space": {
                        "low": 1e2,
                        "high": 1e5,
                    }
                },
            ]
        }
        n = self.user1.algos.count()
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user1.algos.count(), n)
        algo.refresh_from_db()
        self.assertEqual(algo.is_search_space_defined(), True)

    def test_update_parameters_after_trial(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = Algo.objects.create(
            owner=self.user1,
            experiment=self.user1.experiments.all()[0],
            name="new_algo",
        )
        Parameter.objects.create(
            name="uniform_param1",
            algo=algo,
        )
        data = {
            'parameters': [
                {
                    "name": "uniform_param1",
                    "category": "normal",
                    "search_space": {
                        "mu": 3,
                        "sigma": 0.2,
                    }
                },
                {
                    "name": "lol",
                    "category": "categorical",
                    "search_space": {
                        "values": ["lol", "kol"],
                        "probabilities": [0.4, 0.6],
                    }
                }
            ]
        }
        self.assertEqual(algo.is_search_space_defined(), False)
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        n = self.user1.algos.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user1.algos.count(), n)
        algo.refresh_from_db()
        self.assertEqual(algo.is_search_space_defined(), True)
        self.assertEqual(algo.parameters.count(), len(data["parameters"]))

        # Edit category
        data = {
            'parameters': [
                {
                    "name": "uniform_param1",
                    "category": "uniform",
                    "search_space": {
                        "low": 3,
                        "high": 10,
                        "step": 0.15
                    }
                }
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(algo.parameters.get(name="uniform_param1").category, "uniform")
        self.assertEqual(algo.parameters.get(name="uniform_param1").search_space["low"], 3)

        # upload a trial and try to change search space
        data = {
            'algo': algo.pk,
            'parameters': {'uniform_param1': 5, 'lol': "lol"},
            'results': {metric["metric_name"]: 15 for metric in algo.experiment.metrics},
            'comment': {"text": "cool results"}
        }
        response = self.client.post("/api/trials/", data=data)
        self.assertEqual(response.status_code, 201)

        data = {
            'parameters': [
                {
                    "name": "uniform_param1",
                    "category": "uniform",
                    "search_space": {
                        "low": 6,
                        "high": 10,
                        "step": 0.15
                    }
                }
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(algo.parameters.get(name="uniform_param1").search_space["low"], 6)

        # Try suggestion
        data = {
            "metric": algo.experiment.metrics[0]["metric_name"]
        }
        response = self.client.post("/api/algos/{}/suggest/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, 200)

        # Change category after trial
        data = {
            'parameters': [
                {
                    "name": "uniform_param1",
                    "category": "normal",
                    "search_space": {
                        "mu": 3,
                        "sigma": 0.2,
                    }
                }
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, 400)

        # Change param after trial
        data = {
            'parameters': [
                {
                    "name": "lol2",
                    "category": "normal",
                    "search_space": {
                        "mu": 3,
                        "sigma": 0.2,
                    }
                }
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, 400)

    def test_update_parameters_invalid_params(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = Algo.objects.create(
            owner=self.user1,
            experiment=self.user1.experiments.all()[0],
            name="new_algo",
        )
        Parameter.objects.create(
            name="uniform_param1",
            algo=algo,
        )
        Parameter.objects.create(
            name="uniform_param2",
            algo=algo,
        )
        Parameter.objects.create(
            name="normal_param1",
            algo=algo,
        )
        Parameter.objects.create(
            name="normal_param2",
            algo=algo,
        )
        Parameter.objects.create(
            name="categorical_param",
            algo=algo,
        )
        data = {
            'parameters': [
                {"name": "categorical_param", "category": "categorical", "search_space": 2},
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "categorical_param", "category": "categorical", "search_space": {"values": 2}},
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "categorical_param", "category": "categorical", "search_space": {"values": [2, 2],
                                                                                          "probabilities": 1}},
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "categorical_param", "category": "categorical", "search_space": {"values": [2, 2],
                                                                                          "probabilities": [1]}},
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "categorical_param", "category": "categorical", "search_space": {"values": [2, 2],
                                                                                          "probabilities": [1, 2]}},
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "uniform_param2", "category": "uniform", "search_space": {"high": 0.2}}
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "uniform_param2", "category": "uniform", "search_space": 2}
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "uniform_param2", "category": "uniform", "search_space": {"low": 0.2}}
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "uniform_param2", "category": "uniform", "search_space": {
                    "low": 0.2,
                    "high": 0.2,
                    "log": 3,
                }}
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "uniform_param2", "category": "uniform", "search_space": {
                    "low": 0.2,
                    "high": 0.2,
                    "step": True,
                }}
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "normal_param2", "category": "normal", "search_space": 3}
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "normal_param2", "category": "normal", "search_space": {"mu": 0.2}}
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "normal_param2", "category": "normal", "search_space": {"sigma": 0.2}}
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "normal_param2", "category": "lognormal", "search_space": {
                    "sigma": 0.2,
                    "mu": 0.2,
                }}
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'parameters': [
                {"name": "normal_param2", "category": "normal", "search_space": {
                    "sigma": 0.2,
                    "mu": 0.2,
                    "step": True,
                }}
            ]
        }
        response = self.client.patch("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_algos_put(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user1.algos.first()
        new_name = algo.name + " blob"
        data = {
            'name': new_name,
            'parameters': [],
        }
        n = self.user1.algos.count()
        response = self.client.put("/api/algos/{}/".format(algo.pk), data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user1.algos.count(), n)
        algo.refresh_from_db()
        self.assertEqual(algo.name, new_name)

    def test_update_algos_with_invalid_args(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user1.algos.first()
        new_name = algo.name + " blob"
        data = {
            'name': new_name,
            'parameters': [{"name": 'new_params1'}, {"name": 'new_params2'}],
        }

        response = self.client.patch("/api/algos/{}/".format(algo.pk), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        algo.refresh_from_db()
        self.assertEqual(set(algo.parameters.values_list("name", flat=True)),
                         set(['alpha', 'beta', 'gamma']))

    def test_update_algos_try_to_force_owner(self):
        self.client.login(username=self.user1.username, password="123456")
        algo = self.user2.algos.first()
        new_name = algo.name + " blob"
        data = {
            'name': new_name,
        }

        response = self.client.patch("/api/algos/{}/".format(algo.pk), data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_algos_wrong_owner_but_shared_with(self):
        self.client.login(username=self.user2.username, password="123456")
        algo = self.user1.algos.filter(experiment__shared_with=self.user2)[0]
        new_name = algo.name + " blob"
        data = {
            'name': new_name,
        }

        response = self.client.patch("/api/algos/{}/".format(algo.pk), data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # """ DELETE """

    def test_delete_algos(self):
        self.client.login(username=self.user1.username, password="123456")

        n = self.user1.algos.count()
        response = self.client.delete("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user1.algos.count(), n - 1)

    def test_delete_algos_try_to_force_owner(self):
        self.client.login(username=self.user1.username, password="123456")

        n = self.user2.algos.count()
        response = self.client.delete("/api/algos/{}/".format(
            self.user2.algos.all()[0].pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.user2.algos.count(), n)

    def test_delete_algos_try_to_force_owner_shared_with(self):
        self.client.login(username=self.user2.username, password="123456")

        response = self.client.delete("/api/algos/{}/".format(
            self.user1.algos.filter(experiment__shared_with=self.user2)[0].pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # """ RETRIEVE """

    def test_retrieve_algos(self):
        self.client.login(username=self.user1.username, password="123456")

        response = self.client.get("/api/algos/{}/".format(
            self.user1.algos.all()[0].pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_algos_wrong_owner(self):
        self.client.login(username=self.user1.username, password="123456")

        response = self.client.get("/api/algos/{}/".format(
            self.user2.algos.all()[0].pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_algos_wrong_owner_but_shared_with(self):
        self.client.login(username=self.user2.username, password="123456")

        response = self.client.get("/api/algos/{}/".format(
            self.user1.algos.filter(experiment__shared_with=self.user2)[0].pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # """ Suggest """

    def test_suggest(self):
        self.client.login(username=self.user1.username, password="123456")

        experiment = self.user1.experiments.all()[0]
        algo = Algo.objects.create(
            experiment=experiment,
            owner=self.user1,
            name="algo {}".format(uuid.uuid4())
        )
        Parameter.objects.create(
            name="alpha",
            algo=algo,
            category=Parameter.UNIFORM,
            search_space={"high": 5, "low": -3},
        )
        Parameter.objects.create(
            name="beta",
            algo=algo,
            category=Parameter.CATEGORICAL,
            search_space={"values": ["a", "b"]},
        )

        data = {
            "metric": experiment.metrics[0]["metric_name"],
            "optimizer": "random"
        }
        response = self.client.post("/api/algos/{}/suggest/".format(algo.pk),
                                    data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "metric": experiment.metrics[0]["metric_name"],
            "optimizer": "parzen_estimator"
        }
        response = self.client.post("/api/algos/{}/suggest/".format(algo.pk),
                                    data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_suggest_no_search_space(self):
        self.client.login(username=self.user1.username, password="123456")

        experiment = self.user1.experiments.all()[0]
        algo = Algo.objects.create(
            experiment=experiment,
            owner=self.user1,
            name="algo {}".format(uuid.uuid4())
        )
        Parameter.objects.create(
            name="alpha",
            algo=algo,
            # category=Parameter.UNIFORM,
            # search_space={"high": 5, "low": -3},
        )
        Parameter.objects.create(
            name="beta",
            algo=algo,
            # category=Parameter.CATEGORICAL,
            # search_space={"values": ["a", "b"]},
        )

        data = {
            "metric": experiment.metrics[0]["metric_name"],
            "optimizer": "random"
        }
        response = self.client.post("/api/algos/{}/suggest/".format(algo.pk),
                                    data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_suggest_bad_optimizer(self):
        self.client.login(username=self.user1.username, password="123456")

        algo = self.user1.algos.all()[0]
        data = {
            "metric": algo.experiment.metrics[0]["metric_name"],
            "optimizer": "eve"
        }
        response = self.client.post("/api/algos/{}/suggest/".format(algo.pk),
                                    data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_suggest_bad_metric(self):
        self.client.login(username=self.user1.username, password="123456")

        algo = self.user1.algos.all()[0]
        data = {
            "metric": "this is a bad metric",
            "optimizer": "random"
        }
        response = self.client.post("/api/algos/{}/suggest/".format(algo.pk),
                                    data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_suggest_no_params(self):
        self.client.login(username=self.user1.username, password="123456")

        algo = self.user1.algos.all()[0]
        data = {
        }
        response = self.client.post("/api/algos/{}/suggest/".format(algo.pk),
                                    data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AlgoParametersModelTests(BenderTestCase):

    def test_repr(self):
        algo = self.user1.algos.all()[0]
        self.assertEqual(str(algo), algo.name)

    def test_repr_param(self):
        parameter = Parameter.objects.all()[0]
        self.assertEqual(str(parameter), parameter.name)

    def test_is_search_space_defined(self):
        algo = Algo.objects.create(
            owner=self.user1,
            experiment=self.user1.experiments.all()[0],
            name="algo",
        )
        parameter = Parameter.objects.create(
            name="lol",
            algo=algo,
        )
        self.assertEqual(algo.is_search_space_defined(), False)
        parameter.category = "categorical"
        parameter.search_space = {"values": ["haha", "joei"]}
        parameter.save()

        algo.refresh_from_db()
        self.assertEqual(algo.is_search_space_defined(), True)

    def test_get_optimization_problem(self):
        algo = Algo.objects.all()[0]
        algo.get_optimization_problem(algo.experiment.metrics[0])
