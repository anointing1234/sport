# Generated by Django 5.0.7 on 2024-11-13 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_footballmatch_status_match_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bethistory',
            name='status',
            field=models.CharField(choices=[('playing', 'Playing'), ('won', 'Won'), ('loss', 'Loss')], default='playing', max_length=10),
        ),
    ]