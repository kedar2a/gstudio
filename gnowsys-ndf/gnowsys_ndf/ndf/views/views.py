from django.contrib.auth.models import User
from rest_framework import viewsets
from gnowsys_ndf.serializers import UserSerializer, FileHiveSerializer
from gnowsys_ndf.ndf.models import Filehive
from gnowsys_ndf.ndf.models import filehive_collection


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer


# class FileHiveViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = filehive_collection.find()
#     serializer_class = FileHiveSerializer


# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer