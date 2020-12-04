from api import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"stores", views.StoreViewSet, basename="store")
router.register(r"items", views.ItemViewSet, basename="item")
router.register(r"register", views.RegisterUserViewSet, basename="register")
router.register(r"ping", views.PingViewSet, basename="ping")

urlpatterns = router.urls
