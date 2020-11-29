from oauth2_provider.scopes import BaseScopes
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
