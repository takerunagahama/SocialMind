# Generated by Django 5.1.1 on 2024-12-11 12:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SocialInsight', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qanda',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qanda_set', to='SocialInsight.session'),
        ),
    ]
