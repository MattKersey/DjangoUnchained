from django.contrib import admin
from django.urls import include, re_path
# from api import views
# from api import views

# from django.conf.urls import include


urlpatterns = [
    re_path(r'^api/', include('api.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
