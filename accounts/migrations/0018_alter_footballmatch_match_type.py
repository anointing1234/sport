# Generated by Django 5.0.7 on 2024-11-12 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_rename_withdrawal_time_withdrawaltimeanddate_withdrawal_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='footballmatch',
            name='match_type',
            field=models.CharField(choices=[('soccer', 'Soccer Matches')], max_length=10),
        ),
    ]