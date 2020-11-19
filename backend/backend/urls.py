from django.contrib import admin
from django.urls import include, re_path, path
from django.conf.urls.static import static
from django.conf import settings
from .views import OAuthCallbackViewSet, GoogleLogin


urlpatterns = [
    re_path(r"^api/", include("api.urls")),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^authredirect/", OAuthCallbackViewSet.as_view({"get": "list"})),
    re_path(r"^o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    re_path(r"^accounts/", include('allauth.urls')),
    path('rest-auth/google/', GoogleLogin.as_view(), name='google_login')

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
