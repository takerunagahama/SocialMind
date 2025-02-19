# Generated by Django 5.1.1 on 2024-12-11 11:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute', models.CharField(choices=[('empathy', '共感力'), ('organization', '組織理解'), ('visioning', 'ビジョニング'), ('influence', '影響力'), ('inspiration', '啓発力'), ('team', 'チームワーク力'), ('perseverance', '忍耐力'), ('total', '合計点')], max_length=20)),
                ('category', models.CharField(choices=[('strength', '強み'), ('improvement', '改善点')], default='', max_length=20)),
                ('message', models.TextField(default='')),
                ('training_name', models.TextField()),
                ('training_content', models.TextField()),
            ],
            options={
                'verbose_name': 'Messages',
                'verbose_name_plural': 'Messages',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Session',
                'verbose_name_plural': 'Sessions',
                'unique_together': {('user', 'session_id')},
            },
        ),
        migrations.CreateModel(
            name='Scores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('empathy', models.IntegerField(default=0)),
                ('organization', models.IntegerField(default=0)),
                ('visioning', models.IntegerField(default=0)),
                ('influence', models.IntegerField(default=0)),
                ('inspiration', models.IntegerField(default=0)),
                ('team', models.IntegerField(default=0)),
                ('perseverance', models.IntegerField(default=0)),
                ('total', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to=settings.AUTH_USER_MODEL)),
                ('qanda_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='SocialInsight.session')),
            ],
            options={
                'verbose_name': 'Scores',
                'verbose_name_plural': 'Scores',
            },
        ),
        migrations.CreateModel(
            name='QandA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('model_answer', models.TextField()),
                ('user_answer', models.TextField()),
                ('attribute', models.CharField(choices=[('empathy', '共感力'), ('organization', '組織理解'), ('visioning', 'ビジョニング'), ('influence', '影響力'), ('inspiration', '啓発力'), ('team', 'チームワーク力'), ('perseverance', '忍耐力'), ('total', '合計点')], max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='SocialInsight.session')),
            ],
            options={
                'verbose_name': 'Q and A',
                'verbose_name_plural': 'Q and A',
            },
        ),
    ]
