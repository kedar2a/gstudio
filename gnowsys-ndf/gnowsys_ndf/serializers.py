from django.contrib.auth.models import User
from rest_framework import serializers

from gnowsys_ndf.ndf.models.filehive import Filehive

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email')


class FileHiveSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Filehive
        fields = ('_id', 'md5', 'name')
