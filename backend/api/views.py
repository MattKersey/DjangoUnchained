# Complete Me :)
from api.models import User
from rest_framework import generics
from api.serializers import UserSerializer
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope


class UserViewSet(generics.ListAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    serializer_class = UserSerializer
    queryset = User.objects.all()
