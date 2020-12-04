from django.contrib import admin
from django.urls import include, re_path
from django.conf.urls.static import static
from django.conf import settings
from .views import OAuthCallbackViewSet, StoreAuthorizationView


urlpatterns = [
    re_path(r"^api/", include("api.urls")),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^authredirect/", OAuthCallbackViewSet.as_view({"get": "list"})),
    re_path(r"^o/authorize/", StoreAuthorizationView.as_view()),
    re_path(r"^o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
