from oauth2_provider.scopes import BaseScopes


class CustomScopes(BaseScopes):
    def get_all_scopes(self):
        return {"read": "custom reading scope", "write": "custom writing scope"}

    def get_available_scopes(self, application=None, request=None, *args, **kwargs):
        return ["read", "write"]

    def get_default_scopes(self, application=None, request=None, *args, **kwargs):
        return ["read", "write"]
