from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
# Create your views here.
from .models import *
from .serializers import *
import requests
from django.http import HttpResponse
import urllib.request as req

korean_list = ['재키','아야','피오라','매그너스','자히르','나딘','현우','하트','아이솔','리 다이린','유키','혜진','쇼우','키아라','시셀라','실비아','아드리아나','쇼이치','엠마','레녹스','로지','루크','캐시','아델라','버니스','바바라','알렉스','수아','레온','일레븐','리오','윌리엄','니키','나타폰','얀','이바','다니엘','제니','카밀로','클로에','요한','비앙카','셀린','에키온','마이','에이든','라우라','띠아','펠릭스','엘레나','프리야','아디나','마커스','칼라','에스텔','피올로','마르티나','헤이즈','아이작','타지아','이렘','테오도르','이안','바냐','데비&마를렌','아르다','아비게일']

class CharacterView(ModelViewSet):

    pagination_class = None

    queryset = Character.objects.all().order_by('id')
    serializer_class = CharacterSerializers

# alo3AXT2HC1SEa9MaVKOc10lHQ8LvYHr2SKf8zGU


class ItemView(ModelViewSet):

    pagination_class = None

    queryset = Item.objects.all().order_by('itemnumber')
    serializer_class = ItemSerializers



def Characterload(request):

    test = requests.get(
        'https://open-api.bser.io/v1/data/Character',
        headers={'x-api-key':'alo3AXT2HC1SEa9MaVKOc10lHQ8LvYHr2SKf8zGU'}
    )
    test_json = test.json()
    chlist = test_json['data']

    for i in chlist:
        try:
            tester_name = Character.objects.get(name=i['name'])
            tester_name.koreanname = korean_list[tester_name.id-1]
            tester_name.save()
            continue

        except:

            Character(
                name = i['name'],
                attack = i['attackPower'],
                hp = i['maxHp'],
                hpregen = i['hpRegen'],
                stamina = i['maxSp'],
                stregen = i['spRegen'],
                defense = i['defense'],
                atkspeed = i['attackSpeed'],
                speed = i['moveSpeed'],
            ).save()


    return HttpResponse(chlist)




class CharacterRPView(ModelViewSet):

    pagination_class = None

    queryset = Character.objects.all().order_by('-trygame7days')
    serializer_class = CharacterRPSerializers



def Itemload(request):

    test = requests.get(
        'https://open-api.bser.io/v1/data/ItemArmor',
        headers={'x-api-key':'alo3AXT2HC1SEa9MaVKOc10lHQ8LvYHr2SKf8zGU'}
    )
    test_json = test.json()
    itemlist = test_json['data']

    for i in itemlist:
        try:
            tester_name = Item.objects.get(name=i['name'])
            # save_path = f"C:/Users/LeeJinUk/Desktop/DRFBoard/DRFBoardfront/project/src/assets/Item/{i['code']}.png"
            # img_url = f'https://static.inven.co.kr/image_2011/site_image/er/dataninfo/itemicon/itemicon_{i["code"]}.png?v=230901a'
            # dwfile = req.urlretrieve(img_url, save_path)

            continue

        except:

            Item(
                itemnumber = i['code'],
                grade = i['itemGrade'],
                name = i['name']
            ).save()

    test2 = requests.get(
        'https://open-api.bser.io/v1/data/ItemWeapon',
        headers={'x-api-key':'alo3AXT2HC1SEa9MaVKOc10lHQ8LvYHr2SKf8zGU'}
    )
    test_json2 = test2.json()
    itemlist2 = test_json2['data']

    for i in itemlist2:
        try:
            tester_name2 = Item.objects.get(name=i['name'])
            # save_path = f"C:/Users/LeeJinUk/Desktop/DRFBoard/DRFBoardfront/project/src/assets/Item/{i['code']}.png"
            # img_url = f'https://static.inven.co.kr/image_2011/site_image/er/dataninfo/itemicon/itemicon_{i["code"]}.png?v=230901a'
            # dwfile = req.urlretrieve(img_url, save_path)
            continue

        except:

            Item(
                itemnumber = i['code'],
                grade = i['itemGrade'],
                name = i['name']
            ).save()


    return HttpResponse(itemlist)


