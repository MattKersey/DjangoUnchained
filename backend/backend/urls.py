from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path(r"", include(router.urls)),
    url(r"^admin/", admin.site.urls),
    path(r"api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
