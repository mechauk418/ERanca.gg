from django.db import models

# Create your models here.



class Gameuser(models.Model):

    userNum = models.IntegerField()
    mmr = models.IntegerField()
    nickname = models.CharField(max_length=90)
    rank = models.IntegerField()
    totalGames = models.IntegerField()
    winrate = models.DecimalField(max_digits=6, decimal_places=1)
    averageKills = models.DecimalField(max_digits=6, decimal_places=2)
    updatedate = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.nickname




class Record(models.Model):

    gamenumber = models.IntegerField()
    user = models.CharField(max_length=90)
    character = models.IntegerField()
    beforemmr = models.IntegerField()
    aftermmr = models.IntegerField()
    gamerank = models.IntegerField() # 게임 등수
    playerkill = models.IntegerField() # 킬
    playerAss = models.IntegerField() # 어시
    mosterkill = models.IntegerField() # 동물킬
    startDtm = models.DateTimeField() # 게임 시작 시간
    mmrGain = models.IntegerField() # mmr 획득량
    damageToPlayer = models.IntegerField(blank=True, default=0) # 플레이어 피해량
    damageToMonster = models.IntegerField(blank=True, default=0) # 동물 피해량
    premaid = models.IntegerField(blank=True, default=0) # 사전 구성팀
    useWard = models.IntegerField(blank=True, default=0) # 카메라 사용 갯수
    useConsole = models.IntegerField(blank=True, default=0) # 콘솔 작동 횟수
    item0=models.IntegerField(blank=True, default=0) # 무기
    item0_grade = models.CharField(max_length=80, blank=True)

    item1=models.IntegerField(blank=True, default=0) # 옷
    item1_grade = models.CharField(max_length=80, blank=True)

    item2=models.IntegerField(blank=True, default=0) # 모자
    item2_grade = models.CharField(max_length=80, blank=True)

    item3=models.IntegerField(blank=True, default=0) # 팔
    item3_grade = models.CharField(max_length=80, blank=True)

    item4=models.IntegerField(blank=True, default=0) # 신발
    item4_grade = models.CharField(max_length=80, blank=True)

    tier = models.CharField(max_length=80, blank=True)
    grade = models.CharField(max_length=80, blank=True)
    rp = models.CharField(max_length=80, blank=True)
    
    #탈출여부, 1은 실패(전투 이외 요소), 2는 실패(전투패배), 3은 성공
    escapeState = models.IntegerField(default=0, blank=True, null=True)

    tacticalSkillGroup = models.CharField(max_length=80,blank=True)
    tacticalSkillLevel = models.IntegerField(default=0, blank=True, null=True)
    bestWeapon = models.CharField(max_length=80,blank=True)

    traitFirstCore = models.CharField(max_length=80,blank=True)
    traitFirstSub1= models.IntegerField(default=0, blank=True, null=True)
    traitFirstSub2= models.IntegerField(default=0, blank=True, null=True)
    traitSecondSub1= models.IntegerField(default=0, blank=True, null=True)
    traitSecondSub2= models.IntegerField(default=0, blank=True, null=True)


# skillOrderInfo = 스킬 레벨업 순서

# escapeSt-ate = 1이면 탈출 실패, 2이면 전투 패배, 3이면 탈출

# tacticalSkillGroup = 최종 전술 스킬 종류

# tacticalSkillLevel = 최종 전술 스킬 레벨