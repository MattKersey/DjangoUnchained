from django.core.exceptions import ImproperlyConfigured
from oauth2_provider.scopes import BaseScopes
from oauth2_provider.contrib.rest_framework import TokenHasScope
from api.models import Store


def getPK(path):
    elements = path.split("/")
    for i in range(len(elements)):
        if elements[i].upper() == "STORES":
            if i + 1 < len(elements) and elements[i+1].isdigit():
                return elements[i+1]
    return ""


class CustomScopes(BaseScopes):
    def get_all_scopes(self):
        scopes = {"read": "custom reading scope", "write": "custom writing scope"}
        for store in Store.objects.all():
            scopes["store_" + str(store.pk) + ":employee"] = "Employee scope for " + store.name
            scopes["store_" + str(store.pk) + ":manager"] = "Manager scope for " + store.name
            scopes["store_" + str(store.pk) + ":vendor"] = "Vendor scope for " + store.name
        return scopes

    def get_available_scopes(self, application=None, request=None, *args, **kwargs):
        scopes = ["read", "write"]
        for store in Store.objects.all():
            scopes.append("store_" + str(store.pk) + ":employee")
            scopes.append("store_" + str(store.pk) + ":manager")
            scopes.append("store_" + str(store.pk) + ":vendor")
        return scopes

    def get_default_scopes(self, application=None, request=None, *args, **kwargs):
        scopes = ["read", "write"]
        for store in Store.objects.all():
            scopes.append("store_" + str(store.pk) + ":employee")
            scopes.append("store_" + str(store.pk) + ":manager")
            scopes.append("store_" + str(store.pk) + ":vendor")
        return scopes


class TokenHasStoreEmployeeScope(TokenHasScope):
    def get_scopes(self, request, view):
        try:
            required_scopes = super().get_scopes(request, view)
        except ImproperlyConfigured:
            required_scopes = []
        pk = ""
        if request.data.get("store_id"):
            pk = str(request.data.get("store_id"))
        elif getPK(request.path) != "":
            pk = getPK(request.path)
        else:
            return required_scopes
        # TODO: Add in method switches
        required_scopes.append("store_" + pk + ":employee")
        return required_scopes


class TokenHasStoreManagerScope(TokenHasScope):
    def get_scopes(self, request, view):
        try:
            required_scopes = super().get_scopes(request, view)
        except ImproperlyConfigured:
            required_scopes = []
        pk = ""
        if request.data.get("store_id"):
            pk = str(request.data.get("store_id"))
        elif getPK(request.path) != "":
            pk = getPK(request.path)
        else:
            return required_scopes
        # TODO: Add in method switches
        required_scopes.append("store_" + pk + ":manager")
        return required_scopes


class TokenHasStoreVendorScope(TokenHasScope):
    def get_scopes(self, request, view):
        try:
            required_scopes = super().get_scopes(request, view)
        except ImproperlyConfigured:
            required_scopes = []
        pk = ""
        if request.data.get("store_id"):
            pk = str(request.data.get("store_id"))
        elif getPK(request.path) != "":
            pk = getPK(request.path)
        else:
            return required_scopes
        # TODO: Add in method switches
        required_scopes.append("store_" + pk + ":vendor")
        return required_scopes
