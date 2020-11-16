# If Necessary, Complete Me :)
from api import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'stores', views.StoreViewSet, basename='store')
router.register(r'ping', views.PingViewSet, basename='ping')

urlpatterns = router.urls
