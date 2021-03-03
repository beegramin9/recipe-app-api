from rest_framework import serializers
# Meta 클래스에서 model을 맞춰줘야 하기 때문에 대상 model import함
from core.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """ Serializer for tag objects """
    
    class Meta:
        model = Tag
        fields = ('id', 'name')
        extra_kwargs = {
            'id' : {'read_only':True},
        }