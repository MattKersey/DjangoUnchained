# If Necessary, Complete Me :)
from api import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'list', views.UserViewSet, basename='user')

urlpatterns = router.urls
