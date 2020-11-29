from django.core.exceptions import ImproperlyConfigured
from oauth2_provider.scopes import BaseScopes
from oauth2_provider.contrib.rest_framework import TokenHasScope
from api.models import Store


class CustomScopes(BaseScopes):
    def get_all_scopes(self):
        scopes = {"read": "custom reading scope", "write": "custom writing scope"}
        for store in Store.objects.all():
            scopes["store_" + str(store.pk) + ":read"] = "Reading scope for " + store.name
            scopes["store_" + str(store.pk) + ":write"] = "Writing scope for " + store.name
        return scopes

    def get_available_scopes(self, application=None, request=None, *args, **kwargs):
        scopes = ["read", "write"]
        for store in Store.objects.all():
            scopes.append("store_" + str(store.pk) + ":read")
            scopes.append("store_" + str(store.pk) + ":write")
        return scopes

    def get_default_scopes(self, application=None, request=None, *args, **kwargs):
        scopes = ["read", "write"]
        for store in Store.objects.all():
            scopes.append("store_" + str(store.pk) + ":read")
            scopes.append("store_" + str(store.pk) + ":write")
        return scopes


class TokenHasStoreScope(TokenHasScope):
    def getPK(path):
        elements = path.split("/")
        for i in range(len(elements)):
            if elements[i].upper() == "STORES":
                if i + 1 < len(elements) and elements[i+1].isdigit():
                    return elements[i+1]
        return ""

    def get_scopes(self, request, view):
        print(view)
        try:
            required_scopes = super().get_scopes(request, view)
        except ImproperlyConfigured:
            required_scopes = []
        pk = ""
        if request.data.get("store_id"):
            pk = str(request.data.get("store_id"))
        elif self.getPK(request.path) != "":
            pk = self.getPK(request.path)
        else:
            return required_scopes
        # TODO: Add in method switches
        required_scopes.append("store_" + pk + ":read")
        required_scopes.append("store_" + pk + ":write")
