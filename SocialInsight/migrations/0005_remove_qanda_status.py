# Generated by Django 5.1.1 on 2024-09-09 12:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SocialInsight', '0004_qanda_status_alter_messages_attribute_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='qanda',
            name='status',
        ),
    ]
