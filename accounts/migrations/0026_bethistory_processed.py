# Generated by Django 5.0.7 on 2024-11-20 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0025_prediction'),
    ]

    operations = [
        migrations.AddField(
            model_name='bethistory',
            name='processed',
            field=models.BooleanField(default=False),
        ),
    ]
