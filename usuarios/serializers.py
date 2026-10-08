from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegistroSerializer(serializers.ModelSerializer):
    # La contraseña: solo se escribe, nunca se devuelve. Se valida con los validadores de Django.
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    # El email obligatorio
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def validate_email(self, value):
        # Verifica que no exista otro usuario con ese email
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese correo.")
        return value

    def validate_username(self, value):
        # Verifica que no exista otro usuario con ese nombre
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese nombre.")
        return value

    def create(self, validated_data):
        # create_user hashea la contraseña automáticamente (NUNCA la guarda en texto plano)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user