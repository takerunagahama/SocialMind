# Generated by Django 5.1.1 on 2025-01-24 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialInsight', '0002_alter_qanda_session'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='session',
            options={},
        ),
        migrations.AddField(
            model_name='session',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
