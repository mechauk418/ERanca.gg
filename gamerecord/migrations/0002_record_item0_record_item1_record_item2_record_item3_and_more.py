# Generated by Django 4.2.2 on 2023-09-18 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamerecord', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='item0',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='record',
            name='item1',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='record',
            name='item2',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='record',
            name='item3',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='record',
            name='item4',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
