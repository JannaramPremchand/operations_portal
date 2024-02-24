from pyexpat import model
from rest_framework import serializers
from.models import Createmeetings
from .models import *

class CreatemeetingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = 'Createmeetings'
        fileds = '__all__'


