# Generated by Django 4.2.2 on 2023-10-30 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamerecord', '0004_logs'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='matchingMode',
            field=models.IntegerField(blank=True, default=3, null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='season',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
