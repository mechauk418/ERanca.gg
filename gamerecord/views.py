from django.shortcuts import render, get_list_or_404, get_object_or_404
from .models import *
from .serializers import *
from rest_framework.viewsets import ModelViewSet
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from datetime import datetime, timedelta, date
from rest_framework.pagination import PageNumberPagination
from collections import defaultdict
from character.models import Character, Item
from django.utils import timezone
import json, os, time, requests, logging
from django_filters.rest_framework import DjangoFilterBackend

logger = logging.getLogger('gamerecord')

apikey = os.getenv("X_API_KEY")

seasonid = 20 # 정규 프리 시즌2
versionMajor = 7 # 메이저버전 

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

tacticalskill = {
    30:'블링크',
    40:'퀘이크',
    50:'프로토콜 위반',
    60:'붉은 폭풍',
    70:'초월',
    80:'아티팩트',
    90:'무효화',
    110:'강한 결속',
    120:'스트라이더 - A13',
    130:'진실의 칼날',
    140:'거짓 서약',
    150:'치유의 바람',
}

weapon_data = {
"0": "없음",
"1": "글러브",
"2": "톤파",
"3": "방망이",
"4": "채찍",
"5": "투척",
"6": "암기",
"7": "활",
"8": "석궁",
"9": "권총",
"10": "돌격 소총",
"11": "저격총",
"13": "망치",
"14": "도끼",
"15": "단검",
"16": "양손검",
"17": "폴암",
"18": "쌍검",
"19": "창",
"20": "쌍절곤",
"21": "레이피어",
"22": "기타",
"23": "카메라",
"24": "아르카나",
"25": "VF의수"
}

traitinfo = {
   7000201 : "취약",
   7000301 : "광분",
   7000401 : "흡혈마",
   7000501 : "벽력",
   7000601 : "아드레날린",
   7100101 : "금강",
   7100201 : "불괴",
   7100301 : "망각",
   7100401 : "빛의 수호",
   7100501 : "응징",
   7200101 : "초재생",
   7200301 : "치유 드론",
   7200201 : "증폭 드론",
   7200401 : "추진력",
   7200501 : "헌신",
}


def refreshuser(nickname, seasonid):
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
        f'https://open-api.bser.io/v1/user/stats/{userNum}/{seasonid}',
        headers={'x-api-key':apikey}
    ).json()['userStats'][0]

    user = Gameuser.objects.get(userNum = userstats['userNum'], season=seasonid)
    user.mmr = userstats['mmr']
    user.rank = userstats['rank']
    user.totalGames = userstats['totalGames']
    if userstats['totalGames'] ==0:
        user.winrate = 0
    else:
        user.winrate = round((userstats['totalWins']*100 / userstats['totalGames']),1)
    user.averageKills = userstats['averageKills']
    user.save()

    return


def getusernum(nickname, seasonid, limitdays):
    sttime = time.time()
    
    now_time = timezone.localtime(timezone.now())
    # 유저 닉네임으로 유저 정보 받아옴
    time.sleep(0.02)
    userNum = requests.get(
        f'https://open-api.bser.io/v1/user/nickname?query={nickname}',
        headers={'x-api-key':apikey}
    )
    userNum_json = userNum.json()
    if userNum_json['code']==404 and userNum_json['message'] == "Not Found":
        # raise ValueError('에러')
        message = {'message':"플레이어를 찾을 수 없습니다."}
        return (message)
    else:
        userNum = userNum_json['user']['userNum']
    
    
    
    # 이터니티, 데미갓 티어 커트라인 점수를 구함
    top1000 = requests.get(
    f'https://open-api.bser.io/v1/rank/top/{seasonid}/3',
    headers={'x-api-key':apikey}).json()


    if top1000['code']==404:
        eternity = 9999
        demigod = 9999
    else:

        eternity = top1000['topRanks'][199]['mmr']
        demigod = top1000['topRanks'][799]['mmr']
    

    # 유저의 이번 시즌 정보를 받아옴, 19는 정규시즌1 번호
    time.sleep(0.02)
    userstats = requests.get(
        f'https://open-api.bser.io/v1/user/stats/{userNum}/{seasonid}',
        headers={'x-api-key':apikey}
    ).json()

    if userstats['code']== 404 and userstats['message']=='Not Found':
        message = {'message':"이번 시즌 정보가 없습니다."}
        return (message)
    userstats = userstats['userStats'][0]


    # 처음 검색해서 DB에 유저가 없음
    if not Gameuser.objects.filter(nickname = userstats['nickname'], season = seasonid):
        Gameuser.objects.create(
            userNum = userstats['userNum'],
            mmr = userstats['mmr'],
            nickname = userstats['nickname'],
            rank = userstats['rank'],
            totalGames = userstats['totalGames'],
            winrate = round((userstats['totalWins']*100 / userstats['totalGames']),1),
            averageKills = userstats['averageKills'],
            season = userstats['seasonId']
        )
    
    refreshuser(nickname, seasonid)

    search_user = Gameuser.objects.get(nickname = nickname, season = seasonid)
    search_user.updatedate = now_time
    search_user.save()
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

        if len(Record.objects.filter(gamenumber = game['gameId'])):
            continue
        elif (now_time - gametime_aware).days >= limitdays:
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
                
                if g['versionMajor'] < -2:

                    return JsonResponse(userNum_json)
                
                elif g['seasonId'] != seasonid:
                    continue
                
                elif g['matchingMode']!=2 and g['matchingMode']!=3:
                    continue
                
                elif g['matchingMode']==3:
                
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
                        escapeState = g['escapeState'],
                        tacticalSkillGroup = tacticalskill[g['tacticalSkillGroup']],
                        tacticalSkillLevel = g['tacticalSkillLevel'],
                        bestWeapon = weapon_data[str(g['bestWeapon'])],
                        traitFirstCore = traitinfo[g['traitFirstCore']],
                        traitFirstSub1 =g['traitFirstSub'][0],
                        traitFirstSub2 =g['traitFirstSub'][1],
                        traitSecondSub1 =g['traitSecondSub'][0],
                        traitSecondSub2 =g['traitSecondSub'][1],
                        matchingMode = g['matchingMode'],
                        season = g['seasonId'],
                        versionMajor = g['versionMajor']
                    )

                else:
                    #노말이면 일부 요소 제거
                    userrecord = Record.objects.create(
                        gamenumber = game['gameId'],
                        user = g['nickname'],
                        character = g['characterNum'],
                        beforemmr = 0,
                        aftermmr = 0,
                        gamerank = g['gameRank'],
                        playerkill = g['playerKill'],
                        playerAss = g['playerAssistant'],
                        mosterkill = g['monsterKill'],
                        startDtm = g['startDtm'],
                        mmrGain = 0,
                        damageToPlayer = g['damageToPlayer'],
                        damageToMonster  = g['damageToMonster'],
                        premaid  = g['preMade'],
                        useWard  = g['addSurveillanceCamera']+g['addTelephotoCamera'],
                        escapeState = g['escapeState'],
                        tacticalSkillGroup = tacticalskill[g['tacticalSkillGroup']],
                        tacticalSkillLevel = g['tacticalSkillLevel'],
                        bestWeapon = weapon_data[str(g['bestWeapon'])],
                        traitFirstCore = traitinfo[g['traitFirstCore']],
                        traitFirstSub1 =g['traitFirstSub'][0],
                        traitFirstSub2 =g['traitFirstSub'][1],
                        traitSecondSub1 =g['traitSecondSub'][0],
                        traitSecondSub2 =g['traitSecondSub'][1],
                        matchingMode = g['matchingMode'],
                        season = g['seasonId'],
                        versionMajor = g['versionMajor']
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
                    userrecord.rp = str(userrecord.beforemmr%250)
                else:
                    userrecord.rp = str(userrecord.beforemmr-6000)
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

                elif (now_time - gametime_aware).days >= limitdays:
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
                        if g['versionMajor']<-2:

                            return JsonResponse(userNum_json)

                        elif g['seasonId'] != seasonid:
                            continue
                        
                        elif g['matchingMode']!=2 and g['matchingMode']!=3:
                            continue

                        elif g['matchingMode']==3:
                        
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
                                escapeState = g['escapeState'],
                                tacticalSkillGroup = tacticalskill[g['tacticalSkillGroup']],
                                tacticalSkillLevel = g['tacticalSkillLevel'],
                                bestWeapon = weapon_data[str(g['bestWeapon'])],
                                traitFirstCore = traitinfo[g['traitFirstCore']],
                                traitFirstSub1 =g['traitFirstSub'][0],
                                traitFirstSub2 =g['traitFirstSub'][1],
                                traitSecondSub1 =g['traitSecondSub'][0],
                                traitSecondSub2 =g['traitSecondSub'][1],
                                matchingMode = g['matchingMode'],
                                season = g['seasonId'],
                                versionMajor = g['versionMajor']
                            )

                        else:
                            userrecord = Record.objects.create(
                                gamenumber = game['gameId'],
                                user = g['nickname'],
                                character = g['characterNum'],
                                beforemmr = 0,
                                aftermmr = 0,
                                gamerank = g['gameRank'],
                                playerkill = g['playerKill'],
                                playerAss = g['playerAssistant'],
                                mosterkill = g['monsterKill'],
                                startDtm = g['startDtm'],
                                mmrGain = 0,
                                damageToPlayer = g['damageToPlayer'],
                                damageToMonster  = g['damageToMonster'],
                                premaid  = g['preMade'],
                                useWard  = g['addSurveillanceCamera']+g['addTelephotoCamera'],
                                escapeState = g['escapeState'],
                                tacticalSkillGroup = tacticalskill[g['tacticalSkillGroup']],
                                tacticalSkillLevel = g['tacticalSkillLevel'],
                                bestWeapon = weapon_data[str(g['bestWeapon'])],
                                traitFirstCore = traitinfo[g['traitFirstCore']],
                                traitFirstSub1 =g['traitFirstSub'][0],
                                traitFirstSub2 =g['traitFirstSub'][1],
                                traitSecondSub1 =g['traitSecondSub'][0],
                                traitSecondSub2 =g['traitSecondSub'][1],
                                matchingMode = g['matchingMode'],
                                season = g['seasonId'],
                                versionMajor = g['versionMajor']
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
                            userrecord.rp = str(userrecord.beforemmr%250)
                        else:
                            userrecord.rp = str(userrecord.beforemmr-6000)
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
    f'https://open-api.bser.io/v1/rank/top/{seasonid}/3',
    headers={'x-api-key':apikey}).json()

    if top1000['code']==404:
        eternity = 9999
        demigod = 9999
    else:

        eternity = top1000['topRanks'][199]['mmr']
        demigod = top1000['topRanks'][799]['mmr']


    # 유저의 이번 시즌 정보를 받아옴, 19는 정규시즌1 번호
    time.sleep(0.02)
    userstats = requests.get(
        f'https://open-api.bser.io/v1/user/stats/{userNum}/{seasonid}',
        headers={'x-api-key':apikey}
    ).json()

    if userstats['code'] == 404 and userstats['message'] == "Not Found":
        return JsonResponse(userstats)
    else:
        userstats = userstats['userStats'][0]

    # 처음 검색해서 DB에 유저가 없음
    if not Gameuser.objects.filter(nickname = userstats['nickname'], season = seasonid):
        Gameuser.objects.create(
            userNum = userstats['userNum'],
            mmr = userstats['mmr'],
            nickname = userstats['nickname'],
            rank = userstats['rank'],
            totalGames = userstats['totalGames'],
            winrate = round((userstats['totalWins']*100 / userstats['totalGames']),1),
            averageKills = userstats['averageKills'],
            season = userstats['seasonId']
        )
    
    refreshuser(nickname, seasonid)

    search_user = Gameuser.objects.get(nickname = nickname, season = seasonid)
    search_user.updatedate = now_time
    search_user.save()

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

        if (now_time - gametime_aware).days >= 30:
            break

        else:
            
            gamepost = requests.get(
                f'https://open-api.bser.io/v1/games/{game["gameId"]}',
                headers={'x-api-key':apikey}
            )
            gamepost = gamepost.json()
            if 'userGames' not in gamepost:
                print('request limit')

            for g in gamepost['userGames']:
                
                try:
                    ingameuser = Record.objects.get(user=g['nickname'], gamenumber=game['gameId'], season = seasonid)
                    continue

                except:
                    
                    if g['versionMajor']<versionMajor:

                        return JsonResponse(userNum_json)
                    
                    elif g['matchingMode']!=2 and g['matchingMode']!=3:
                        continue
                    elif g['seasonId'] != seasonid:
                        continue
                    if g['matchingMode']==3:
                    
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
                            escapeState = g['escapeState'],
                            tacticalSkillGroup = tacticalskill[g['tacticalSkillGroup']],
                            tacticalSkillLevel = g['tacticalSkillLevel'],
                            bestWeapon = weapon_data[str(g['bestWeapon'])],
                            traitFirstCore = traitinfo[g['traitFirstCore']],
                            traitFirstSub1 =g['traitFirstSub'][0],
                            traitFirstSub2 =g['traitFirstSub'][1],
                            traitSecondSub1 =g['traitSecondSub'][0],
                            traitSecondSub2 =g['traitSecondSub'][1],
                            matchingMode = g['matchingMode'],
                            season = g['seasonId'],
                            versionMajor = g['versionMajor']
                        )

                    else:
                        userrecord = Record.objects.create(
                            gamenumber = game['gameId'],
                            user = g['nickname'],
                            character = g['characterNum'],
                            beforemmr = 0,
                            aftermmr = 0,
                            gamerank = g['gameRank'],
                            playerkill = g['playerKill'],
                            playerAss = g['playerAssistant'],
                            mosterkill = g['monsterKill'],
                            startDtm = g['startDtm'],
                            mmrGain = 0,
                            damageToPlayer = g['damageToPlayer'],
                            damageToMonster  = g['damageToMonster'],
                            premaid  = g['preMade'],
                            useWard  = g['addSurveillanceCamera']+g['addTelephotoCamera'],
                            escapeState = g['escapeState'],
                            tacticalSkillGroup = tacticalskill[g['tacticalSkillGroup']],
                            tacticalSkillLevel = g['tacticalSkillLevel'],
                            bestWeapon = weapon_data[str(g['bestWeapon'])],
                            traitFirstCore = traitinfo[g['traitFirstCore']],
                            traitFirstSub1 =g['traitFirstSub'][0],
                            traitFirstSub2 =g['traitFirstSub'][1],
                            traitSecondSub1 =g['traitSecondSub'][0],
                            traitSecondSub2 =g['traitSecondSub'][1],
                            matchingMode = g['matchingMode'],
                            season = g['seasonId'],
                            versionMajor = g['versionMajor']
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
                        userrecord.rp = str(userrecord.beforemmr%250)
                    else:
                        userrecord.rp = str(userrecord.beforemmr-6000)
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

                if (now_time - gametime_aware).days >= 30:
                    days_check = True
                    break

                else:
                    gamepost = requests.get(
                        f'https://open-api.bser.io/v1/games/{game["gameId"]}',
                        headers={'x-api-key':apikey}
                    )
                    gamepost = gamepost.json()
                    if 'userGames' not in gamepost:
                        print('request limit')
                    # while 'userGames' not in gamepost:
                    #                            gamepost = requests.get(
                    #     f'https://open-api.bser.io/v1/games/{game["gameId"]}',
                    #     headers={'x-api-key':apikey}
                    #     ).json()

                    for g in gamepost['userGames']:
                        
                        try:
                            ingameuser = Record.objects.get(user=g['nickname'], gamenumber=game['gameId'], season=seasonid)
                            continue

                        except:
                            
                            if g['versionMajor']<versionMajor:

                                return JsonResponse(userNum_json)
                            elif g['matchingMode']!=2 and g['matchingMode']!=3:
                                continue
                            elif g['seasonId'] != seasonid:
                                continue
                            if g['matchingMode']==3:

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
                                    escapeState = g['escapeState'],
                                    tacticalSkillGroup = tacticalskill[g['tacticalSkillGroup']],
                                    tacticalSkillLevel = g['tacticalSkillLevel'],
                                    bestWeapon = weapon_data[str(g['bestWeapon'])],
                                    traitFirstCore = traitinfo[g['traitFirstCore']],
                                    traitFirstSub1 =g['traitFirstSub'][0],
                                    traitFirstSub2 =g['traitFirstSub'][1],
                                    traitSecondSub1 =g['traitSecondSub'][0],
                                    traitSecondSub2 =g['traitSecondSub'][1],
                                    matchingMode = g['matchingMode'],
                                    season = g['seasonId'],
                                    versionMajor = g['versionMajor']
                                    )
                                
                            else:
                                userrecord = Record.objects.create(
                                    gamenumber = game['gameId'],
                                    user = g['nickname'],
                                    character = g['characterNum'],
                                    beforemmr = 0,
                                    aftermmr = 0,
                                    gamerank = g['gameRank'],
                                    playerkill = g['playerKill'],
                                    playerAss = g['playerAssistant'],
                                    mosterkill = g['monsterKill'],
                                    startDtm = g['startDtm'],
                                    mmrGain = 0,
                                    damageToPlayer = g['damageToPlayer'],
                                    damageToMonster  = g['damageToMonster'],
                                    premaid  = g['preMade'],
                                    useWard  = g['addSurveillanceCamera']+g['addTelephotoCamera'],
                                    escapeState = g['escapeState'],
                                    tacticalSkillGroup = tacticalskill[g['tacticalSkillGroup']],
                                    tacticalSkillLevel = g['tacticalSkillLevel'],
                                    bestWeapon = weapon_data[str(g['bestWeapon'])],
                                    traitFirstCore = traitinfo[g['traitFirstCore']],
                                    traitFirstSub1 =g['traitFirstSub'][0],
                                    traitFirstSub2 =g['traitFirstSub'][1],
                                    traitSecondSub1 =g['traitSecondSub'][0],
                                    traitSecondSub2 =g['traitSecondSub'][1],
                                    matchingMode = g['matchingMode'],
                                    season = g['seasonId'],
                                    versionMajor = g['versionMajor']
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
                                userrecord.rp = str(userrecord.beforemmr%250)
                            else:
                                userrecord.rp = str(userrecord.beforemmr-6000)
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
    

    return JsonResponse(userNum_json)




class RecordPage(PageNumberPagination):
    page_size = 10


class RecordView(ModelViewSet):
    pagination_class = RecordPage
    filterset_fields = ['character']
    serializer_class = RecordSerializer
    queryset = Record.objects.all()
    # def get_queryset(self, *args,**kwargs):
    #     logger.info('전적검색')
    #     logger.info(self.kwargs.get('nickname'))
    #     Logs.objects.create(
    #         whatuse = '전적검색',
    #         nick1 = self.kwargs.get('nickname')
    #     )

    #     try:
    #         new_user = Gameuser.objects.get(nickname=self.kwargs.get('nickname'),season = self.kwargs.get('season') )
            
    #     except:
    #         getusernum(self.kwargs.get('nickname'), self.kwargs.get('season'), 7)
    #         getusernum(self.kwargs.get('nickname'), self.kwargs.get('season')-1, 14)

    #     qs = Record.objects.filter(user=self.kwargs.get('nickname'), season = self.kwargs.get('season')).order_by('-gamenumber')

    #     return qs
    
    def list(self, request, *args, **kwargs):
        try:
            new_user = Gameuser.objects.get(nickname=self.kwargs.get('nickname'),season = self.kwargs.get('season') )
            
        except:
            usercheck = getusernum(self.kwargs.get('nickname'), self.kwargs.get('season'), 7)
            if 'message' in usercheck:
                if usercheck['message'] == '플레이어를 찾을 수 없습니다.':
                    return JsonResponse(usercheck)
                else:
                    getusernum(self.kwargs.get('nickname'), self.kwargs.get('season')-1, 14)
        
        qs = Record.objects.filter(user=self.kwargs.get('nickname'), season = self.kwargs.get('season')).order_by('-gamenumber')
        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer =  RecordSerializer(page,many=True)
            return self.get_paginated_response(serializer.data)
        serializer =  RecordSerializer(qs,many=True)
        return Response(serializer.data)


class RecordDetailView(ModelViewSet):
    pagination_class = None
    queryset = Record.objects.all()
    def get_queryset(self):
        qs = Record.objects.filter(gamenumber = self.kwargs.get('gamenumber')).order_by('gamerank')
        return qs

    serializer_class = GameDetailSerializer
    lookup_field = 'gamenumber'


class UserDetailView(ModelViewSet):

    queryset = Gameuser.objects.all()
    serializer_class = GameuserSerializer
    lookup_field = 'nickname'

    def retrieve(self, request, *args, **wargs):
        try:
            user = Gameuser.objects.get(nickname=self.kwargs.get('nickname'), season = self.kwargs.get('season'))
            serializer = GameuserSerializer(user)
            return Response(serializer.data)
        except:
            userdetail={
                'mmr':'-',
                'nickname':self.kwargs.get('nickname'),
                'rank':'-',
                'totalGames':'-',
                'winrate':'-',
                'averageKills':'-',
                'averageDamage':'-',
                'winrate':0,
                "message":"시즌 정보가 없습니다."
            }
            return JsonResponse(userdetail)
        

class UseChView(ModelViewSet):

    pagination_class = RecordPage
    queryset = Gameuser.objects.all()
    serializer_class = UserUseSerializer
    lookup_field = 'nickname'

    def retrieve(self, request, *args, **wargs):
        try:
            user = Gameuser.objects.get(nickname=self.kwargs.get('nickname'), season = self.kwargs.get('season'))
            serializer = UserUseSerializer(user)
            return Response(serializer.data)
        except:
            return JsonResponse({"usechrank":[]})

        



# 최근 획득 RP View
def recentgainrp(request,nickname,season):

    alldict = dict()
    
    ch_dict = defaultdict(int)
    ch2_dict = defaultdict(int)
    try:
        userid = Gameuser.objects.get(nickname = nickname, season=season)
    except:
        return JsonResponse({"result":[]})
    userrecord = Record.objects.filter(user = userid, startDtm__range=[date.today()-timedelta(days=14),date.today()], season=season)

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


def refresh(request,nickname):

    return refreshrecord(nickname)

# RP 통계 초기화
def resetrp():
    logger.info('resetrp')

    allcharacter = Character.objects.all()

    for ch in allcharacter:
        ch.rpfor7days = 0
        ch.rpeff = 0
        ch.trygame7days = 0
        ch.save()

    return

# RP 통계 데이터 수집
def gainrp(start,end):
    logger.info('gainrp   '+str(start)  + str(end))
    sttime = time.time()
    alldict = dict()
    mmrdict=defaultdict(int)
    trydict = defaultdict(int)

    top1000 = requests.get(
    f'https://open-api.bser.io/v1/rank/top/{seasonid}/3',
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

    logger.info('탐색종료')
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
        ch.rpfor7days += i['mmrGain']
        ch.trygame7days += i['trygame']
        ch.save()
    
    logger.info('등록종료')

    return

# RP통계 데이터 작성
def rpeff():
    logger.info('rpeff')

    allcharacter = Character.objects.all()

    for ch in allcharacter:
        if ch.trygame7days !=0:
            ch.rpeff = round(ch.rpfor7days / ch.trygame7days,2)
            ch.save()

    return

import io, json, base64
from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from google.cloud import vision

@csrf_exempt
def detect_text(request):
    print('gcp test0')
    testdata = json.loads(request.body)
    path = testdata['imgurl'][22:]

    top1000 = requests.get(
    f'https://open-api.bser.io/v1/rank/top/{seasonid}/3',
    headers={'x-api-key':apikey}).json()

    if top1000['code']==404:
        eternity = 9999
        demigod = 9999
    else:

        eternity = top1000['topRanks'][199]['mmr']
        demigod = top1000['topRanks'][799]['mmr']
    
    try:
        client = vision.ImageAnnotatorClient()
        print(client)
    except:
        print('fail')
    base64img = base64.b64decode(path)
    img = Image.open(io.BytesIO(base64img))
    img_h,img_w = img.size
    if (img_w/img_h) > 0.57 or  (img_w/img_h) < 0.56:
        return HttpResponse('error')
    crop1=(2200/3840)*img_h
    crop2=(3600/3840)*img_h
    crop3=(1850/2160)*img_w
    crop4=(1950/2160)*img_w

    img_crop = img.crop((crop1,crop3,crop2,crop4))

    buffer = io.BytesIO()
    img_crop.save(buffer,format='PNG')
    img_data = buffer.getvalue()

    print('gcp test1')
    image = vision.Image(content=img_data)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    nicklist=[]
    
    print('gcp test2')

    for text in texts:
        temt = text.description
        nicklist = temt.split('\n')
        break
    print(nicklist)
    logger.info('이미지 전적 검색')
    logger.info(nicklist)
    
    Logs.objects.create(
            whatuse = '이미지검색',
            nick1 = temt,
        )
    
    multilist = {}
    for nickname in nicklist:
        userNum = requests.get(
            f'https://open-api.bser.io/v1/user/nickname?query={nickname}',
            headers={'x-api-key':apikey}
        )
        userNum_json = userNum.json()
        if 'user' not in userNum_json:
            continue
        userNum = userNum_json['user']['userNum']
        userstats = requests.get(
            f'https://open-api.bser.io/v1/user/stats/{userNum}/{seasonid}',
            headers={'x-api-key':apikey}
        ).json()
        temtdict={}
        if userstats['code']==404 and userstats['message']=='Not Found':
            temtdict = {
                'mmr':'-',
                'tier':'-',
                'grade':'-',
                'rp':'-',
                'nickname':nickname,
                'totalGames':'-',
                'totalWins':'-',
                'winrate':'-',
                'averageKills':'-',
            }

        else:
            userstats=userstats['userStats'][0]
            
            logger.info('검색된 유저 mmr')
            logger.info(userstats['mmr'])
            if userstats['mmr'] < 6000:
                temtdict['tier'] = tiervalue[userstats['mmr']//1000]
                temtdict['grade'] = gradevalue[(userstats['mmr']%1000)//250]
                temtdict['rp'] = userstats['mmr']%250
            else:
                temtdict['rp'] = userstats['mmr']-6000
                if userstats['mmr'] >= eternity:
                    temtdict['tier'] = '이터니티'
                    temtdict['grade']=''
                elif userstats['mmr'] >= demigod:
                    temtdict['tier'] = '데미갓'
                    temtdict['grade']=''
                else:
                    temtdict['tier'] = '미스릴'
                    temtdict['grade']=''


            temtdict['nickname']=userstats['nickname']
            temtdict['totalGames']=userstats['totalGames']
            temtdict['totalWins']=userstats['totalWins']
            temtdict['winrate']=round((userstats['totalWins']*100)/userstats['totalGames'],1)
            temtdict['averageKills']=userstats['averageKills']

            mostcharacternumber = len(userstats['characterStats'])
            
            for i in range(mostcharacternumber):
                temtdict[f'most{i+1}'] = Character.objects.get(id=userstats['characterStats'][i]['characterCode']).name
                temtdict[f'most{i+1}_play'] = round((userstats['characterStats'][i]['totalGames']*100)/userstats['totalGames'],1)


        multilist[nickname]=temtdict

    return JsonResponse(multilist)