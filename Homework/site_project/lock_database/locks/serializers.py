from rest_framework import serializers
from .models import Lock

class LockSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    company = serializers.CharField(required=False)
    model = serializers.CharField(required=False)
    lock_type = serializers.CharField(required=False)
    core = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    image = serializers.FileField(required=False)
    image_link = serializers.URLField(required=False)

    def create(self, validated_data):
        instance = Lock()
        instance.name = validated_data.get('name', None)
        instance.company = validated_data.get('company', None)
        instance.model = validated_data.get('model', None)
        instance.lock_type = validated_data.get('lock_type', None)
        instance.core = validated_data.get('core', None)
        instance.description = validated_data.get('description', None)
        instance.image = validated_data.get('image', None)
        instance.image_link = validated_data.get('image_link', None)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.company = validated_data.get('company', instance.company)
        instance.model = validated_data.get('model', instance.model)
        instance.lock_type = validated_data.get('lock_type', instance.lock_type)
        instance.core = validated_data.get('core', instance.core)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.image_link = validated_data.get('image_link', None)
        instance.save()
        return instance