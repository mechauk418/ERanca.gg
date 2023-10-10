from django.shortcuts import render, get_list_or_404
from .models import *
from .serializers import *
from rest_framework.viewsets import ModelViewSet
# Create your views here.
import requests
from django.http import JsonResponse, HttpResponse
import time
from rest_framework.response import Response
from datetime import datetime, timedelta, date
from rest_framework.pagination import PageNumberPagination
from collections import defaultdict
from character.models import Character, Item
from django.utils import timezone
import json
from django_filters.rest_framework import DjangoFilterBackend
import os


apikey = os.getenv("X_API_KEY")

# 티어, 등급 딕셔너리
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


def refreshuser(nickname):
    time.sleep(0.02)
    userNum = requests.get(
        f'https://open-api.bser.io/v1/user/nickname?query={nickname}',
        headers={'x-api-key':apikey}
    )

    userNum_json = userNum.json()
    userNum = userNum_json['user']['userNum']
    
    # 유저 닉네임으로 유저 정보 받아옴
    time.sleep(0.02)
    userstats = requests.get(
        f'https://open-api.bser.io/v1/user/stats/{userNum}/19',
        headers={'x-api-key':apikey}
    ).json()['userStats'][0]

    user = Gameuser.objects.get(userNum = userstats['userNum'])
    user.mmr = userstats['mmr']
    user.rank = userstats['rank']
    user.totalGames = userstats['totalGames']
    user.winrate = round((userstats['totalWins']*100 / userstats['totalGames']),1)
    user.averageKills = userstats['averageKills']
    user.save()

    return JsonResponse(userNum_json)


def getusernum(nickname):
    sttime = time.time()
    now_time = timezone.localtime(timezone.now())
    # 유저 닉네임으로 유저 정보 받아옴
    
    time.sleep(0.02)
    userNum = requests.get(
        f'https://open-api.bser.io/v1/user/nickname?query={nickname}',
        headers={'x-api-key':apikey}
    )
    userNum_json = userNum.json()
    userNum = userNum_json['user']['userNum']
    
    
    
    # 이터니티, 데미갓 티어 커트라인 점수를 구함
    top1000 = requests.get(
    f'https://open-api.bser.io/v1/rank/top/19/3',
    headers={'x-api-key':apikey}).json()['topRanks']

    eternity = top1000[199]['mmr']
    demigod = top1000[799]['mmr']
    

    # 유저의 이번 시즌 정보를 받아옴, 19는 정규시즌1 번호
    time.sleep(0.02)
    userstats = requests.get(
        f'https://open-api.bser.io/v1/user/stats/{userNum}/19',
        headers={'x-api-key':apikey}
    ).json()['userStats'][0]

    # 처음 검색해서 DB에 유저가 없음
    if not Gameuser.objects.filter(nickname = userstats['nickname']):
        Gameuser.objects.create(
            userNum = userstats['userNum'],
            mmr = userstats['mmr'],
            nickname = userstats['nickname'],
            rank = userstats['rank'],
            totalGames = userstats['totalGames'],
            winrate = round((userstats['totalWins']*100 / userstats['totalGames']),1),
            averageKills = userstats['averageKills'],
        )
    
    refreshuser(nickname)

    search_user = Gameuser.objects.get(nickname = nickname)

    # 유저 넘버로 유저의 최근 90일 내의 전적을 모두 가져옴
    time.sleep(0.02)
    match = requests.get(
        f'https://open-api.bser.io/v1/user/games/{userNum}',
        headers={'x-api-key':apikey}
    ).json()
    matchdetail = match['userGames']
    
    # 가져온 전적을 등록하는 과정
    for game in matchdetail:
        t = game['startDtm']
        print(t)
        gametime = datetime(int(t[0:4]),int(t[5:7]),int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19]))
        gametime_aware = timezone.make_aware(gametime)
        if len(Record.objects.filter(gamenumber = game['gameId'])):
        
            continue

        elif game['matchingMode'] !=3:

            continue

        elif (now_time - gametime_aware).days >= 14:
            break

        else:
            time.sleep(0.02)
            gamepost = requests.get(
                f'https://open-api.bser.io/v1/games/{game["gameId"]}',
                headers={'x-api-key':apikey}
            )
            gamepost = gamepost.json()
            # if 'userGames' not in gamepost:
            #                    gamepost = requests.get(
            #     f'https://open-api.bser.io/v1/games/{game["gameId"]}',
            #     headers={'x-api-key':apikey}
            #     ).json()
            

            for g in gamepost['userGames']:
                

                if g['matchingMode'] !=3:
                    continue

                userrecord = Record.objects.create(
                    gamenumber = game['gameId'],
                    user = g['nickname'],
                    character = g['characterNum'],
                    beforemmr = g['mmrBefore'],
                    aftermmr = g['mmrAfter'],
                    gamerank = g['gameRank'],
                    playerkill = g['playerKill'],
                    playerAss = g['playerAssistant'],
                    mosterkill = g['monsterKill'],
                    startDtm = g['startDtm'],
                    mmrGain = g['mmrGain'],
                    damageToPlayer = g['damageToPlayer'],
                    damageToMonster  = g['damageToMonster'],
                    premaid  = g['preMade'],
                    useWard  = g['addSurveillanceCamera']+g['addTelephotoCamera'],
                )
                if '0' in g['equipment']:
                    userrecord.item0 = g['equipment']['0']
                    userrecord.item0_grade = Item.objects.get(itemnumber = userrecord.item0 ).grade
                if '1' in g['equipment']:
                    userrecord.item1 = g['equipment']['1']
                    userrecord.item1_grade = Item.objects.get(itemnumber = userrecord.item1 ).grade
                if '2' in g['equipment']:
                    userrecord.item2 = g['equipment']['2']
                    userrecord.item2_grade = Item.objects.get(itemnumber = userrecord.item2 ).grade
                if '3' in g['equipment']:
                    userrecord.item3 = g['equipment']['3']
                    userrecord.item3_grade = Item.objects.get(itemnumber = userrecord.item3 ).grade
                if '4' in g['equipment']:
                    userrecord.item4 = g['equipment']['4']
                    userrecord.item4_grade = Item.objects.get(itemnumber = userrecord.item4 ).grade
                

                if userrecord.beforemmr < 6000:
                    userrecord.tier = tiervalue[userrecord.beforemmr//1000]
                    userrecord.grade = gradevalue[(userrecord.beforemmr%1000)//250]
                    userrecord.RP = str(userrecord.beforemmr%250)
                else:
                    userrecord.RP = str(userrecord.beforemmr-6000)
                    if userrecord.beforemmr >= eternity:
                        userrecord.tier = '이터니티'
                    elif userrecord.beforemmr >= demigod:
                        userrecord.tier = '데미갓'
                    else:
                        userrecord.tier = '미스릴'

                    
                userrecord.save()


    if 'next' in match:
        next_number = match['next']

        while True:

            days_check = False
            time.sleep(0.02)
            match = requests.get(
                f'https://open-api.bser.io/v1/user/games/{userNum}?next={next_number}',
                headers={'x-api-key':apikey})
            match = match.json()
            # while 'userGames' not in match:
            #     match = requests.get(
            #     f'https://open-api.bser.io/v1/user/games/{userNum}?next={next_number}',
            #     headers={'x-api-key':apikey}).json()
            matchdetail = match['userGames']
            upt = matchdetail[0]['startDtm']
            test_time = datetime(int(upt[0:4]),int(upt[5:7]),int(upt[8:10]), int(upt[11:13]), int(upt[14:16]), int(upt[17:19])  )
            test_time_aware = timezone.make_aware(test_time)

            if search_user.updatedate is not None and \
                search_user.updatedate > test_time_aware:
                break


            # 가져온 전적을 등록하는 과정
            for game in matchdetail:
                
                t = game['startDtm']
                gametime = datetime(int(t[0:4]),int(t[5:7]),int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19])  )
                gametime_aware = timezone.make_aware(gametime)

                if len(Record.objects.filter(gamenumber = game['gameId'])):
                    
                    continue

                elif game['matchingMode'] !=3:
                    continue

                elif (now_time - gametime_aware).days >= 14:
                    days_check = True
                    break

                else:
                    time.sleep(0.02)
                    gamepost = requests.get(
                        f'https://open-api.bser.io/v1/games/{game["gameId"]}',
                        headers={'x-api-key':apikey}
                    )
                    gamepost = gamepost.json()
                    # while 'userGames' not in gamepost:
                    #                            gamepost = requests.get(
                    #     f'https://open-api.bser.io/v1/games/{game["gameId"]}',
                    #     headers={'x-api-key':apikey}
                    #     ).json()

                    for g in gamepost['userGames']:
                        
                        if g['matchingMode'] ==2:
                            continue

                        userrecord = Record.objects.create(
                            gamenumber = game['gameId'],
                            user = g['nickname'],
                            character = g['characterNum'],
                            beforemmr = g['mmrBefore'],
                            aftermmr = g['mmrAfter'],
                            gamerank = g['gameRank'],
                            playerkill = g['playerKill'],
                            playerAss = g['playerAssistant'],
                            mosterkill = g['monsterKill'],
                            startDtm = g['startDtm'],
                            mmrGain = g['mmrGain'],
                            damageToPlayer = g['damageToPlayer'],
                            damageToMonster  = g['damageToMonster'],
                            premaid  = g['preMade'],
                            useWard  = g['addSurveillanceCamera']+g['addTelephotoCamera'],
                        )
                        if '0' in g['equipment']:
                            userrecord.item0 = g['equipment']['0']
                            userrecord.item0_grade = Item.objects.get(itemnumber = userrecord.item0 ).grade
                        if '1' in g['equipment']:
                            userrecord.item1 = g['equipment']['1']
                            userrecord.item1_grade = Item.objects.get(itemnumber = userrecord.item1 ).grade
                        if '2' in g['equipment']:
                            userrecord.item2 = g['equipment']['2']
                            userrecord.item2_grade = Item.objects.get(itemnumber = userrecord.item2 ).grade
                        if '3' in g['equipment']:
                            userrecord.item3 = g['equipment']['3']
                            userrecord.item3_grade = Item.objects.get(itemnumber = userrecord.item3 ).grade
                        if '4' in g['equipment']:
                            userrecord.item4 = g['equipment']['4']
                            userrecord.item4_grade = Item.objects.get(itemnumber = userrecord.item4 ).grade
                        
                        if userrecord.beforemmr < 6000:
                            userrecord.tier = tiervalue[userrecord.beforemmr//1000]
                            userrecord.grade = gradevalue[(userrecord.beforemmr%1000)//250]
                            userrecord.RP = str(userrecord.beforemmr%250)
                        else:
                            userrecord.RP = str(userrecord.beforemmr-6000)
                            if userrecord.beforemmr >= eternity:
                                userrecord.tier = '이터니티'
                            elif userrecord.beforemmr >= demigod:
                                userrecord.tier = '데미갓'
                            else:
                                userrecord.tier = '미스릴'


                        userrecord.save()

            # 7일이 넘은 기록부터는 가져오지 않음
            if days_check:
                break

            if 'next' in match:
                next_number = match['next']
            else:
                break

    edtime = time.time()
    search_user.updatedate = now_time
    search_user.save()

    return JsonResponse(userNum_json)


# 전적 갱신
def refreshrecord(nickname):
    sttime = time.time()
    now_time = timezone.localtime(timezone.now())
    # 유저 닉네임으로 유저 정보 받아옴
    time.sleep(0.02)
    userNum = requests.get(
        f'https://open-api.bser.io/v1/user/nickname?query={nickname}',
        headers={'x-api-key':apikey}
    )
    userNum_json = userNum.json()
    userNum = userNum_json['user']['userNum']
    
    top1000 = requests.get(
    f'https://open-api.bser.io/v1/rank/top/19/3',
    headers={'x-api-key':apikey}).json()['topRanks']

    eternity = top1000[199]['mmr']
    demigod = top1000[799]['mmr']

    

    # 유저의 이번 시즌 정보를 받아옴, 19는 정규시즌1 번호
    time.sleep(0.02)
    userstats = requests.get(
        f'https://open-api.bser.io/v1/user/stats/{userNum}/19',
        headers={'x-api-key':apikey}
    ).json()['userStats'][0]

    # 처음 검색해서 DB에 유저가 없음
    if not Gameuser.objects.filter(nickname = userstats['nickname']):
        Gameuser.objects.create(
            userNum = userstats['userNum'],
            mmr = userstats['mmr'],
            nickname = userstats['nickname'],
            rank = userstats['rank'],
            totalGames = userstats['totalGames'],
            winrate = round((userstats['totalWins']*100 / userstats['totalGames']),1),
            averageKills = userstats['averageKills'],
        )
    
    refreshuser(nickname)

    search_user = Gameuser.objects.get(nickname = nickname)

    # 유저 넘버로 유저의 최근 90일 내의 전적을 모두 가져옴
    time.sleep(0.02)
    match = requests.get(
        f'https://open-api.bser.io/v1/user/games/{userNum}',
        headers={'x-api-key':apikey}
    ).json()
    matchdetail = match['userGames']
    
    # 가져온 전적을 등록하는 과정
    for game in matchdetail:
        t = game['startDtm']
        gametime = datetime(int(t[0:4]),int(t[5:7]),int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19]))
        gametime_aware = timezone.make_aware(gametime)

        if game['matchingMode'] !=3:

            continue

        elif (now_time - gametime_aware).days >= 14:
            break

        else:
            time.sleep(0.02)
            gamepost = requests.get(
                f'https://open-api.bser.io/v1/games/{game["gameId"]}',
                headers={'x-api-key':apikey}
            )
            gamepost = gamepost.json()
            # if 'userGames' not in gamepost:
            #                    gamepost = requests.get(
            #     f'https://open-api.bser.io/v1/games/{game["gameId"]}',
            #     headers={'x-api-key':apikey}
            #     ).json()
            

            for g in gamepost['userGames']:
                

                if g['matchingMode'] !=3:
                    continue

                try:
                    ingameuser = Record.objects.get(user=g['nickname'], gamenumber=game['gameId'])
                    continue

                except:
                    
                    userrecord = Record.objects.create(
                        gamenumber = game['gameId'],
                        user = g['nickname'],
                        character = g['characterNum'],
                        beforemmr = g['mmrBefore'],
                        aftermmr = g['mmrAfter'],
                        gamerank = g['gameRank'],
                        playerkill = g['playerKill'],
                        playerAss = g['playerAssistant'],
                        mosterkill = g['monsterKill'],
                        startDtm = g['startDtm'],
                        mmrGain = g['mmrGain'],
                        damageToPlayer = g['damageToPlayer'],
                        damageToMonster  = g['damageToMonster'],
                        premaid  = g['preMade'],
                        useWard  = g['addSurveillanceCamera']+g['addTelephotoCamera'],
                    )
                    if '0' in g['equipment']:
                        userrecord.item0 = g['equipment']['0']
                        userrecord.item0_grade = Item.objects.get(itemnumber = userrecord.item0 ).grade
                    if '1' in g['equipment']:
                        userrecord.item1 = g['equipment']['1']
                        userrecord.item1_grade = Item.objects.get(itemnumber = userrecord.item1 ).grade
                    if '2' in g['equipment']:
                        userrecord.item2 = g['equipment']['2']
                        userrecord.item2_grade = Item.objects.get(itemnumber = userrecord.item2 ).grade
                    if '3' in g['equipment']:
                        userrecord.item3 = g['equipment']['3']
                        userrecord.item3_grade = Item.objects.get(itemnumber = userrecord.item3 ).grade
                    if '4' in g['equipment']:
                        userrecord.item4 = g['equipment']['4']
                        userrecord.item4_grade = Item.objects.get(itemnumber = userrecord.item4 ).grade
                        

                    if userrecord.beforemmr < 6000:
                        userrecord.tier = tiervalue[userrecord.beforemmr//1000]
                        userrecord.grade = gradevalue[(userrecord.beforemmr%1000)//250]
                        userrecord.RP = str(userrecord.beforemmr%250)
                    else:
                        userrecord.RP = str(userrecord.beforemmr-6000)
                        if userrecord.beforemmr >= eternity:
                            userrecord.tier = '이터니티'
                        elif userrecord.beforemmr >= demigod:
                            userrecord.tier = '데미갓'
                        else:
                            userrecord.tier = '미스릴'                        


                    userrecord.save()


    if 'next' in match:
        next_number = match['next']

        while True:

            days_check = False
            time.sleep(0.02)
            match = requests.get(
                f'https://open-api.bser.io/v1/user/games/{userNum}?next={next_number}',
                headers={'x-api-key':apikey})
            match = match.json()
            # while 'userGames' not in match:
            #     match = requests.get(
            #     f'https://open-api.bser.io/v1/user/games/{userNum}?next={next_number}',
            #     headers={'x-api-key':apikey}).json()
            matchdetail = match['userGames']
            upt = matchdetail[0]['startDtm']
            test_time = datetime(int(upt[0:4]),int(upt[5:7]),int(upt[8:10]), int(upt[11:13]), int(upt[14:16]), int(upt[17:19])  )
            test_time_aware = timezone.make_aware(test_time)

            if search_user.updatedate is not None and \
                search_user.updatedate > test_time_aware:
                break


            # 가져온 전적을 등록하는 과정
            for game in matchdetail:
                
                t = game['startDtm']
                gametime = datetime(int(t[0:4]),int(t[5:7]),int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19])  )
                gametime_aware = timezone.make_aware(gametime)


                if game['matchingMode'] !=3:
                    continue

                elif (now_time - gametime_aware).days >= 14:
                    days_check = True
                    break

                else:
                    time.sleep(0.02)
                    gamepost = requests.get(
                        f'https://open-api.bser.io/v1/games/{game["gameId"]}',
                        headers={'x-api-key':apikey}
                    )
                    gamepost = gamepost.json()
                    # while 'userGames' not in gamepost:
                    #                            gamepost = requests.get(
                    #     f'https://open-api.bser.io/v1/games/{game["gameId"]}',
                    #     headers={'x-api-key':apikey}
                    #     ).json()

                    for g in gamepost['userGames']:
                        
                        if g['matchingMode'] ==2:
                            continue

                        try:
                            ingameuser = Record.objects.get(user=g['nickname'], gamenumber=game['gameId'])
                            continue
                        except:

                            userrecord = Record.objects.create(
                                gamenumber = game['gameId'],
                                user = g['nickname'],
                                character = g['characterNum'],
                                beforemmr = g['mmrBefore'],
                                aftermmr = g['mmrAfter'],
                                gamerank = g['gameRank'],
                                playerkill = g['playerKill'],
                                playerAss = g['playerAssistant'],
                                mosterkill = g['monsterKill'],
                                startDtm = g['startDtm'],
                                mmrGain = g['mmrGain'],
                                damageToPlayer = g['damageToPlayer'],
                                damageToMonster  = g['damageToMonster'],
                                premaid  = g['preMade'],
                                useWard  = g['addSurveillanceCamera']+g['addTelephotoCamera'],
                            )
                            if '0' in g['equipment']:
                                userrecord.item0 = g['equipment']['0']
                                userrecord.item0_grade = Item.objects.get(itemnumber = userrecord.item0 ).grade
                            if '1' in g['equipment']:
                                userrecord.item1 = g['equipment']['1']
                                userrecord.item1_grade = Item.objects.get(itemnumber = userrecord.item1 ).grade
                            if '2' in g['equipment']:
                                userrecord.item2 = g['equipment']['2']
                                userrecord.item2_grade = Item.objects.get(itemnumber = userrecord.item2 ).grade
                            if '3' in g['equipment']:
                                userrecord.item3 = g['equipment']['3']
                                userrecord.item3_grade = Item.objects.get(itemnumber = userrecord.item3 ).grade
                            if '4' in g['equipment']:
                                userrecord.item4 = g['equipment']['4']
                                userrecord.item4_grade = Item.objects.get(itemnumber = userrecord.item4 ).grade

                            if userrecord.beforemmr < 6000:
                                userrecord.tier = tiervalue[userrecord.beforemmr//1000]
                                userrecord.grade = gradevalue[(userrecord.beforemmr%1000)//250]
                                userrecord.RP = str(userrecord.beforemmr%250)
                            else:
                                userrecord.RP = str(userrecord.beforemmr-6000)
                                if userrecord.beforemmr >= eternity:
                                    userrecord.tier = '이터니티'
                                elif userrecord.beforemmr >= demigod:
                                    userrecord.tier = '데미갓'
                                else:
                                    userrecord.tier = '미스릴'                            
                            userrecord.save()

            # 7일이 넘은 기록부터는 가져오지 않음
            if days_check:
                break

            if 'next' in match:
                next_number = match['next']
            else:
                break

    edtime = time.time()
    search_user.updatedate = now_time
    search_user.save()

    return JsonResponse(userNum_json)




def getuserRecord(request):

    

    return

class RecordPage(PageNumberPagination):
    page_size = 10


class RecordView(ModelViewSet):
    pagination_class = RecordPage
    filterset_fields = ['character']
    queryset = Record.objects.all()

    def get_queryset(self, *args,**kwargs):

        try:
            new_user = Gameuser.objects.get(nickname=self.kwargs.get('nickname'))
            
        except:
            getusernum(self.kwargs.get('nickname'))

        qs = Record.objects.filter(user=self.kwargs.get('nickname')).order_by('-gamenumber')

        return qs
    
        

    serializer_class = RecordSerializer


class UserDetailView(ModelViewSet):

    queryset = Gameuser.objects.all()
    serializer_class = GameuserSerializer
    lookup_field = 'nickname'

class UseChView(ModelViewSet):

    pagination_class = RecordPage
    queryset = Gameuser.objects.all()
    serializer_class = UserUseSerializer
    lookup_field = 'nickname'


def recentgainrp(request,nickname):
    
    alldict = dict()
    
    ch_dict = defaultdict(int)
    ch2_dict = defaultdict(int)

    userid = Gameuser.objects.get(nickname = nickname)
    userrecord = Record.objects.filter(user = userid, startDtm__range=[date.today()-timedelta(days=14),date.today()])

    for g in userrecord:
        chname = Character.objects.get(id=g.character).name
        ch_dict[chname]+=g.mmrGain
        ch2_dict[chname]+=1

    ch2_item = list(ch2_dict.items())
    ch2_item.sort(key=lambda x:(-x[1]))

    result_list = []

    for item in ch2_item:
        temtdict = dict()
        temtdict['chname']=item[0]
        temtdict['trygame']=item[1]
        temtdict['mmrGain']=ch_dict[item[0]]
        result_list.append(temtdict)
        
    alldict['result'] = result_list

    return JsonResponse(alldict)


def testrp(request,nickname):

    return refreshrecord(nickname)

def timetest(request):
    now_time = timezone.localtime(timezone.now())
    ABCDE = []
    ABCDE.append(now_time)
    temt = timezone.now()
    ABCDE.append(temt)

    return HttpResponse(ABCDE)

def resetrp():

    allcharacter = Character.objects.all()

    for ch in allcharacter:
        ch.RPfor7days = 0
        ch.RPeff = 0
        ch.trygame7days = 0
        ch.save()

def gainrp(start,end):
    sttime = time.time()
    alldict = dict()
    mmrdict=defaultdict(int)
    trydict = defaultdict(int)

    top1000 = requests.get(
    f'https://open-api.bser.io/v1/rank/top/19/3',
    headers={'x-api-key':apikey}).json()['topRanks'][start:end]

    for user in top1000:
        userNum = user['userNum']
        time.sleep(0.02)
        match = requests.get(
            f'https://open-api.bser.io/v1/user/games/{userNum}',
            headers={'x-api-key':apikey}
        ).json()
        matchdetail = match['userGames']
    
        # 가져온 전적을 등록하는 과정
        for game in matchdetail:
            t = game['startDtm']
            gametime = datetime(int(t[0:4]),int(t[5:7]),int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19]))
            gametime_aware = timezone.make_aware(gametime)

            if game['matchingMode'] !=3:

                continue

            elif (now_time - gametime_aware).days >= 7:
                break

            else:
                charater_name = Character.objects.get(id = game['characterNum']).name
                mmrdict[charater_name] += game['mmrGain']
                trydict[charater_name] += 1


            if 'next' in match:
                next_number = match['next']

                while True:

                    days_check = False
                    time.sleep(0.02)
                    match = requests.get(
                        f'https://open-api.bser.io/v1/user/games/{userNum}?next={next_number}',
                        headers={'x-api-key':apikey})
                    match = match.json()
                    # while 'userGames' not in match:
                    #     match = requests.get(
                    #     f'https://open-api.bser.io/v1/user/games/{userNum}?next={next_number}',
                    #     headers={'x-api-key':apikey}).json()
                    matchdetail = match['userGames']
                    upt = matchdetail[0]['startDtm']


                    # 가져온 전적을 등록하는 과정
                    for game in matchdetail:
                        
                        t = game['startDtm']
                        gametime = datetime(int(t[0:4]),int(t[5:7]),int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19])  )
                        gametime_aware = timezone.make_aware(gametime)

                        if game['matchingMode'] !=3:
                            continue

                        elif (now_time - gametime_aware).days >= 7:
                            days_check = True
                            break

                        else:
                            charater_name = Character.objects.get(id = game['characterNum']).name
                            mmrdict[charater_name] += game['mmrGain']
                            trydict[charater_name] += 1


                    # 7일이 넘은 기록부터는 가져오지 않음
                    if days_check:
                        break

                    if 'next' in match:
                        next_number = match['next']
                    else:
                        break

    print('탐색종료')
    ch2_item = list(trydict.items())
    ch2_item.sort(key=lambda x:(-x[1]))

    result_list = []

    for item in ch2_item:
        temtdict = dict()
        temtdict['chname']=item[0]
        temtdict['trygame']=item[1]
        temtdict['mmrGain']=mmrdict[item[0]]
        result_list.append(temtdict)
        
    alldict['result'] = result_list

    for i in alldict['result']:
        ch = Character.objects.get(name=i['chname'])
        ch.RPfor7days += i['mmrGain']
        ch.RPeff += round(i['mmrGain'] / i['trygame'],2)
        ch.trygame7days += i['trygame']
        ch.save()
        print(ch)
    
    print('등록종료')

def rpeff():

    allcharacter = Character.objects.all()

    for ch in allcharacter:
        ch.RPeff = round(ch['mmrGain'] / ch['trygame'],2)
        ch.save()