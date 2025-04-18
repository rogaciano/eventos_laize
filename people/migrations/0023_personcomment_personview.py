# Generated by Django 5.0 on 2025-04-06 02:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0022_publiccataloglink'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_text', models.TextField(verbose_name='Comentário/Pergunta')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('is_question', models.BooleanField(default=False, verbose_name='É uma pergunta?')),
                ('is_answered', models.BooleanField(default=False, verbose_name='Foi respondida?')),
                ('answer_text', models.TextField(blank=True, null=True, verbose_name='Resposta')),
                ('answered_at', models.DateTimeField(blank=True, null=True, verbose_name='Respondido em')),
                ('catalog', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='people.castingcatalog', verbose_name='Catálogo')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='people.person', verbose_name='Pessoa')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_comments', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Comentário/Pergunta',
                'verbose_name_plural': 'Comentários/Perguntas',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PersonView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(blank=True, max_length=50, null=True, verbose_name='Endereço IP')),
                ('session_key', models.CharField(blank=True, max_length=40, null=True, verbose_name='Chave de Sessão')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')),
                ('catalog', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='views', to='people.castingcatalog', verbose_name='Catálogo')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='people.person', verbose_name='Pessoa')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='person_views', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Visualização de Perfil',
                'verbose_name_plural': 'Visualizações de Perfis',
                'ordering': ['-timestamp'],
            },
        ),
    ]
