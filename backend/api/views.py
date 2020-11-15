# Complete Me :)
from api.models import User
from rest_framework import viewsets
from rest_framework.response import Response
from api.serializers import UserSerializer
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasReadWriteScope


class UserViewSet(viewsets.ViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasReadWriteScope]

    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        data = request.data
        User.objects.create_staffuser(email=data["email"], password=data["password"])
        return Response(request.data)
