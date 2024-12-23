# Generated by Django 5.0.7 on 2024-11-12 18:52

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_withdrawaltimeanddate'),
    ]

    operations = [
        migrations.RenameField(
            model_name='withdrawaltimeanddate',
            old_name='withdrawal_time',
            new_name='withdrawal_end_time',
        ),
        migrations.AddField(
            model_name='withdrawaltimeanddate',
            name='withdrawal_start_time',
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
