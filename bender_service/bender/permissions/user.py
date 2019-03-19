from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """USer custom permission

    User need to be authenticated.

    Need to be user or superuser to use object.
        * update: shared experiments update can only be done to remove shared experiment
                  (only owner of experiment can add a new shared with)
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated():
                return True

        return False

    def has_object_permission(self, request, view, user):

        if request.user.is_authenticated():
            if user == request.user or request.user.is_superuser:
                if view.action in ("update", "partial_update"):
                    shared_experiments_data = set(request.data.get("shared_experiments", []))
                    shared_experiments = set(user.shared_experiments.values_list("pk", flat=True))
                    if shared_experiments_data.issubset(shared_experiments):
                        return True
                else:
                    return True

        return False
