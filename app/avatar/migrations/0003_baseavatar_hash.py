# Generated by Django 2.1.4 on 2019-01-11 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0002_auto_20190109_0018'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseavatar',
            name='hash',
            field=models.CharField(default='', max_length=16),
            preserve_default=False,
        ),
    ]
