
from .models import *
from rest_framework import serializers
from character.models import Character
from django.utils import timezone
from datetime import datetime, timedelta, date
import math

now_time = timezone.localtime(timezone.now())

tiervalue = {
    0:"아이언",
    1:'브론즈',
    2:'실버',
    3:'골드',
    4:'플래티넘',
    5:'다이아몬드',
}

gradevalue = {
    0:"4",
    1:'3',
    2:'2',
    3:'1',
}

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
    tier = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    rp = serializers.SerializerMethodField()

    def get_averageDamage(self,obj):

        games = Record.objects.filter(user = obj)
        sumDamage = 0
        for game in games:
            sumDamage += game.damageToPlayer

        avgD = int(sumDamage/len(games))
        
        return avgD
    
    def get_tier(self,obj):

        tiers = obj.mmr

        if tiers < 6000:
            return tiervalue[tiers//1000]
        else:
            if obj.rank<=200:
                return '이터니티'
            elif obj.rank<=700:
                return '데미갓'
            else:
                return '미스릴'
            
    def get_grade(self,obj):

        tiers = obj.mmr

        if tiers < 6000:
            return gradevalue[(tiers%1000)//250]

        else:
            return ''
            
    def get_rp(self,obj):

        tiers = obj.mmr

        if tiers < 6000:
            return str(tiers%250)
        else:
            return str(tiers-6000)


    class Meta:
        model = Gameuser
        fields = '__all__'


class RecordSerializer(serializers.ModelSerializer):
    
    playcharacter = serializers.SerializerMethodField()

    def get_playcharacter(self,obj):
        ch = Character.objects.get(id=obj.character)
        
        return ch.name

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

# 유저가 사용한 캐릭터 목록
class UserUseSerializer(serializers.ModelSerializer):

    usechrank = serializers.SerializerMethodField()

    def get_usechrank(self,obj):
        useruselist = []
        checklist = [] # 중복 체크
        qs = Record.objects.filter(user = obj.nickname, season=obj.season, matchingMode=3).order_by('character')
        for i in qs:
            temt = Character.objects.get(id=i.character)
            if temt.pk not in checklist:
                checklist.append(temt.pk)
                useruselist.append( {'chname': temt.koreanname, 'chnumber':temt.pk} )

            else:
                continue

        return useruselist

    class Meta:
        model = Gameuser
        fields = ['usechrank']