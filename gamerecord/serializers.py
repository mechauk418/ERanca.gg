
from .models import *
from rest_framework import serializers
from character.models import Character
from django.utils import timezone
from datetime import datetime, timedelta, date
import math

now_time = timezone.localtime(timezone.now())


class GameDetailSerializer(serializers.ModelSerializer):


    playcharacter = serializers.SerializerMethodField()

    def get_playcharacter(self,obj):
        ch = Character.objects.get(id=obj.character)
        
        return ch.name


    class Meta:
        model = Record
        fields = '__all__'


class GameuserSerializer(serializers.ModelSerializer):

    averageDamage = serializers.SerializerMethodField()

    def get_averageDamage(self,obj):

        games = Record.objects.filter(user = obj)
        sumDamage = 0
        for game in games:
            sumDamage += game.damageToPlayer

        avgD = int(sumDamage/len(games))

        
        return avgD


    class Meta:
        model = Gameuser
        fields = '__all__'

class RecordSerializer(serializers.ModelSerializer):

    gamedetail = serializers.SerializerMethodField()
    
    playcharacter = serializers.SerializerMethodField()

    def get_playcharacter(self,obj):
        ch = Character.objects.get(id=obj.character)
        
        return ch.name

    def get_gamedetail(self,obj):
        data = Record.objects.filter(gamenumber = obj.gamenumber).order_by('gamerank')

        return GameDetailSerializer(instance=data, many=True, context = self.context).data


    whenplay = serializers.SerializerMethodField()

    def get_whenplay(self,obj):

        t = str(obj.startDtm+timedelta(hours=9))
        
        gametime = datetime(int(t[0:4]),int(t[5:7]),int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19])  )
        gametime_aware = timezone.make_aware(gametime)
        when = (now_time - gametime_aware) # 분단위

        if when.days >= 1:
            return str(when.days) + '일 전'
        
        elif when.seconds < 3600:
            when = str(math.floor((when.seconds)/60)) + '분 전'
            return when
        else:
            when = str(math.floor((when.seconds)/3600)) + '시간 전'
            return when


    class Meta:
        model = Record
        fields = '__all__'


class UserUseSerializer(serializers.ModelSerializer):

    usech = serializers.SerializerMethodField()

    def get_usech(self,obj):
        userlist = []
        checklist = [] # 중복 체크
        qs = Record.objects.filter(user = obj.nickname).order_by('character')
        for i in qs:
            temt = Character.objects.get(id=i.character)
            if temt.pk not in checklist:
                checklist.append(temt.pk)
                userlist.append( {'chname': temt.koreanname, 'chnumber':temt.pk} )

            else:
                continue

                

        return userlist

    class Meta:
        model = Gameuser
        fields = ['usech']