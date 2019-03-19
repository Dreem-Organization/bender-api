from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .views import experiment as experiment_views
from .views import algo as algo_views
from .views import trial as trial_views
from .views import user as user_views

router = DefaultRouter()

router.register(r'experiments', experiment_views.ExperimentViewSet, base_name="experiments")
router.register(r'algos', algo_views.AlgoViewSet, base_name="algos")
router.register(r'trials', trial_views.TrialViewSet, base_name="trials")
router.register(r'users', user_views.UserViewSet, base_name="users")

urlpatterns = [
    url(r'^', include(router.urls)),
]
