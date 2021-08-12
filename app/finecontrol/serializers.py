from rest_framework import serializers
from .models import Method_Db, ZeroPosition_Db, PlateSizeSettings_Db, OffsetSettings_Db


class MethodSerializer(serializers.ModelSerializer):
    auth = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Method_Db
        fields = ['id', 'filename', 'auth']
        read_only_fields = ['id']


class ZeroPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZeroPosition_Db
        exclude = ('id',)


class PlateSizesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlateSizeSettings_Db
        exclude = ('id',)


class OffsetSerializer(serializers.ModelSerializer):
    class Meta:
        model = OffsetSettings_Db
        exclude = ('id',)


class OcLabControlSerializer(serializers.Serializer):
    method = serializers.CharField(required=True, allow_blank=False, max_length=100)
