from django.contrib import admin
from django.urls import re_path
# from django.conf.urls import include


urlpatterns = [
    # re_path("", include("api.urls")),
    re_path("admin/", admin.site.urls),
]
