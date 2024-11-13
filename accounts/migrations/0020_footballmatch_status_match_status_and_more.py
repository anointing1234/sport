# Generated by Django 5.0.7 on 2024-11-13 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_hotgame_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='footballmatch',
            name='status',
            field=models.CharField(choices=[('playing', 'Playing'), ('won', 'Won'), ('lost', 'Lost')], default='playing', max_length=10),
        ),
        migrations.AddField(
            model_name='match',
            name='status',
            field=models.CharField(choices=[('playing', 'Playing'), ('won', 'Won'), ('lost', 'Lost')], default='playing', max_length=10),
        ),
        migrations.AddField(
            model_name='premierleaguegame',
            name='status',
            field=models.CharField(choices=[('playing', 'Playing'), ('won', 'Won'), ('lost', 'Lost')], default='playing', max_length=10),
        ),
    ]