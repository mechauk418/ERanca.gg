from rest_framework import serializers
from .models import Character, Item



class CharacterSerializers(serializers.ModelSerializer):

    class Meta:
        model = Character
        fields = '__all__'


class CharacterRPSerializers(serializers.ModelSerializer):

    class Meta:
        model = Character
        fields = ['name','trygame7days','rpfor7days' , 'rpeff','koreanname'  ]


class ItemSerializers(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = '__all__'