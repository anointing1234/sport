# Generated by Django 5.0.7 on 2024-11-06 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_bethistory_placed_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='soccer_slider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='soccer_slider/')),
            ],
            options={
                'verbose_name': 'soccer_slider',
                'verbose_name_plural': 'soccer_slider',
            },
        ),
    ]
