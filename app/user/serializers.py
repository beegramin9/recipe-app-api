from django.contrib.auth import get_user_model, authenticate
# Output 되는 message를 언어에 맞춰 자동 번역
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the users object """
    class Meta:
        # serializer가 어떤 모델을 대상으로 하는지 configure
        model = get_user_model()
        # API에서 accessible한 /DTO 할 field configure
        fields = ('email','password','name')
        extra_kwargs = {
            'password' : {'write_only':True, 'min_length': 5},
        }

    def create(self, validated_data):
        """ Create a new user with encrypted password and return it """
        # User가 생성될 때 data를 validate해서 인자에 전달
        # 즉, Data validation이 이미 된 create/update funciton
        return get_user_model().objects.create_user(**validated_data)

# Model로 들어가는 데이터를 관리하는게 아니라 기본 Serializer        
class AuthTokenSerializer(serializers.Serializer):
    """ Serializer for the user authentication object """
    email = serializers.CharField()
    password = serializers.CharField(
        style = {'input_type':'password'},
        # space 제거 안함
        trim_whitespace = False
    )

    # attrs는 해당 serializer의 모든 Field
    # validate함수를 override할 땐 반드시 attrs를 리턴해야 함
    def validate(self, attrs):
        """ Validate and authenticate the user """
        email = attrs.get('email')
        password = attrs.get('password')
        # authenticate request
        user = authenticate(
            # authenticate 하고싶은 request
            # request가 만들어지면 View셋은 context를 serializer에 pass하는데
            # 이 request가 만들어진 context에서 request를 뽑아 인자로 넣는다
            request = self.context.get('request'),
            # 파라미터 그래도 써야함
            username = email,
            password = password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs