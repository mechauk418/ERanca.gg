from django.db import models

# Create your models here.


class Character(models.Model):

    name = models.CharField(max_length=80)
    attack = models.DecimalField(max_digits=6, decimal_places=3)
    hp = models.DecimalField(max_digits=6, decimal_places=3)
    hpregen = models.DecimalField(max_digits=6, decimal_places=3)
    stamina = models.DecimalField(max_digits=6, decimal_places=3)
    stregen = models.DecimalField(max_digits=6, decimal_places=3)
    defense = models.DecimalField(max_digits=6, decimal_places=3)
    atkspeed = models.DecimalField(max_digits=6, decimal_places=3)
    speed = models.DecimalField(max_digits=6, decimal_places=3)
    koreanname = models.CharField(max_length=80, blank=True)
    rpfor7days = models.IntegerField(blank=True, default=0)
    rpeff = models.DecimalField(max_digits=6, decimal_places=2, blank=True, default=0)
    trygame7days = models.IntegerField(blank=True, default=0)


class Item(models.Model):

    itemnumber = models.IntegerField(blank=True, default=0)
    grade = models.CharField(max_length=80)
    name = models.CharField(max_length=80)