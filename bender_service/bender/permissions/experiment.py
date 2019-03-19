from rest_framework import permissions


class ExperimentPermission(permissions.BasePermission):
    """Experiment custom permission

    User need to be authenticated
    If super user True

    Else adding protections for classic user.
        - list: Need to ask for user own list (owner = request.user)
                Cannot ask anotheer user list
        - create: Cannot create for another user
    """

    def has_permission(self, request, view):
        user = request.user

        if user.is_authenticated():
            if view.action == "list":
                owner = request.GET.get("owner")
                if owner == request.user.username:
                    return True

                shared_with = request.GET.get("shared_with")
                if shared_with and shared_with == request.user.username:
                    return True

            else:
                return True

        return False

    def has_object_permission(self, request, view, experiment):
        user = request.user

        if user.is_authenticated():

            if experiment.owner == request.user:
                return True

            if view.action in ["algos", "trials", "latest_algo", "retrieve"]:
                if request.user in experiment.shared_with.all():
                    return True

        return False
