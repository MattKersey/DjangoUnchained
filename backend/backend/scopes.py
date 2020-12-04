from django.core.exceptions import ImproperlyConfigured
from oauth2_provider.scopes import BaseScopes
from oauth2_provider.contrib.rest_framework import TokenHasScope
from api.models import Store


def getPK(path):
    elements = path.split("/")
    for i in range(len(elements)):
        if elements[i].upper() == "STORES":
            if i + 1 < len(elements) and elements[i + 1].isdigit():
                return elements[i + 1]
        elif elements[i].upper() == "ITEMS":
            if i + 1 < len(elements) and elements[i + 1].isdigit():
                store = Store.objects.filter(items__id=int(elements[i + 1])).first()
                if store is not None:
                    pk = str(store.pk)
                    return pk

    return ""


class CustomScopes(BaseScopes):
    def get_common_scopes(self):
        scopes = {"read": "custom reading scope", "write": "custom writing scope"}
        for store in Store.objects.all():
            scopes["store_" + str(store.pk) + ":employee"] = (
                "Employee scope for " + store.name
            )
            scopes["store_" + str(store.pk) + ":manager"] = (
                "Manager scope for " + store.name
            )
            scopes["store_" + str(store.pk) + ":vendor"] = (
                "Vendor scope for " + store.name
            )
        return scopes

    def get_all_scopes(self):
        return self.get_common_scopes()

    def get_available_scopes(self, application=None, request=None, *args, **kwargs):
        return list(self.get_common_scopes().keys())

    def get_default_scopes(self, application=None, request=None, *args, **kwargs):
        return list(self.get_common_scopes().keys())


class TokenHasStoreScope(TokenHasScope):
    def get_scopes(self, request, view, type):
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
        required_scopes.append("store_" + pk + ":" + type)
        return required_scopes


class TokenHasStoreEmployeeScope(TokenHasStoreScope):
    def get_scopes(self, request, view):
        return super().get_scopes(request, view, "employee")


class TokenHasStoreManagerScope(TokenHasStoreScope):
    def get_scopes(self, request, view):
        return super().get_scopes(request, view, "manager")


class TokenHasStoreVendorScope(TokenHasStoreScope):
    def get_scopes(self, request, view):
        return super().get_scopes(request, view, "vendor")
