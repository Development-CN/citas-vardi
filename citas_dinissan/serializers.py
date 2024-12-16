from rest_framework import serializers

from .models import AgenciaTablero, VCitasUsuarios


class AgenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgenciaTablero
        fields = "__all__"


class AsesorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VCitasUsuarios
        fields = "__all__"
