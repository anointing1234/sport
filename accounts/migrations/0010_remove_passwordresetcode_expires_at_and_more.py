# Generated by Django 5.0.7 on 2024-11-04 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_passwordresetcode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='passwordresetcode',
            name='expires_at',
        ),
        migrations.AlterField(
            model_name='passwordresetcode',
            name='code',
            field=models.CharField(max_length=6),
        ),
    ]
