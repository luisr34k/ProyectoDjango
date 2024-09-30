# serializers.py
from rest_framework import serializers
from .models import Marca

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = '__all__'  # Incluye todos los campos de Marca