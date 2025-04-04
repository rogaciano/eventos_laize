# Generated by Django 5.0 on 2025-04-04 16:56

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0021_auto_20250404_1207'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicCatalogLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Token de Acesso')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Data de Expiração')),
                ('catalog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='public_links', to='people.castingcatalog', verbose_name='Catálogo')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Criado por')),
            ],
            options={
                'verbose_name': 'Link Público de Catálogo',
                'verbose_name_plural': 'Links Públicos de Catálogos',
            },
        ),
    ]
