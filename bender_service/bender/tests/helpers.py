from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from bender.models import Experiment, Algo, Trial, Parameter
from django.db import transaction
import random
import uuid

User = get_user_model()


class BenderTestCase(APITestCase):

    @transaction.atomic
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="Toto1",
            password="123456",
            email="toto1@gmail.com"
        )

        for _ in range(2):
            experiment = Experiment.objects.create(
                name="This is my experiment {}".format(uuid.uuid4()),
                metrics={"metric_name": "lol", "type": "gain"},
                owner=self.user1,
            )
            for _ in range(3):
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
                    category=Parameter.UNIFORM,
                    search_space={"high": 5, "low": -3},
                )
                Parameter.objects.create(
                    name="gamma",
                    algo=algo,
                    category=Parameter.UNIFORM,
                    search_space={"high": 5, "low": -3},
                )
                for _ in range(4):
                    Trial.objects.create(
                        experiment=experiment,
                        algo=algo,
                        owner=self.user1,
                        parameters={"alpha": random.random(), "beta": random.random(),
                                    "gamma": random.random()},
                        comment="izi trial",
                        results={"lol": random.random()}
                    )
        self.user2 = User.objects.create_user(
            username="Toto2",
            password="123456",
            email="toto2@gmail.com",
        )

        for _ in range(3):
            experiment = Experiment.objects.create(
                name="This is my experiment {}".format(uuid.uuid4()),
                metrics=[{'metric_name': 'lol', "type": "loss"},
                         {'metric_name': 'lal', "type": "reward"}],
                owner=self.user2,
            )
            for _ in range(3):
                algo = Algo.objects.create(
                    experiment=experiment,
                    owner=self.user2,
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
                    category=Parameter.UNIFORM,
                    search_space={"high": 5, "low": -3},
                )
                Parameter.objects.create(
                    name="gamma",
                    algo=algo,
                    category=Parameter.UNIFORM,
                    search_space={"high": 5, "low": -3},
                )
                for _ in range(3):
                    Trial.objects.create(
                        experiment=experiment,
                        algo=algo,
                        owner=self.user2,
                        parameters={"alpha": random.random(), "beta": random.random(),
                                    "gamma": random.random()},
                        comment="izi trial",
                        results={"lol": random.random(), "lal": "a"}
                    )
        experiment = Experiment.objects.create(
            name="This is my experiment 5",
            metrics=[{"metric_name": 'lole', "type": "loss"}],
            owner=self.user1,
        )
        experiment.shared_with.add(self.user2)
        for _ in range(2):
            algo = Algo.objects.create(
                experiment=experiment,
                owner=self.user1,
                name="mon algo {}".format(uuid.uuid4()),
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
                category=Parameter.UNIFORM,
                search_space={"high": 5, "low": -3},
            )
            Parameter.objects.create(
                name="gamma",
                algo=algo,
                category=Parameter.UNIFORM,
                search_space={"high": 5, "low": -3},
            )
            for _ in range(4):
                Trial.objects.create(
                    experiment=experiment,
                    owner=self.user1,
                    algo=algo,
                    parameters={"alpha": random.random(), "beta": random.random(),
                                "gamma": random.random()},
                    comment="izi trial",
                    results={"lole": random.random()}
                )
        for _ in range(2):
            algo = Algo.objects.create(
                experiment=experiment,
                owner=self.user2,
                name="mon algo {}".format(uuid.uuid4()),
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
                category=Parameter.UNIFORM,
                search_space={"high": 5, "low": -3},
            )
            Parameter.objects.create(
                name="gamma",
                algo=algo,
                category=Parameter.UNIFORM,
                search_space={"high": 5, "low": -3},
            )
            for _ in range(5):
                Trial.objects.create(
                    experiment=experiment,
                    algo=algo,
                    owner=self.user2,
                    parameters={"alpha": random.random(), "beta": random.random(),
                                "gamma": random.random()},
                    comment="izi trial",
                    results={"lole": random.random()}
                )

        self.user_admin = User.objects.create_superuser(
            username="admin",
            password="123456",
            email="admin@gmail.com"
        )
