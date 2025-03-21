# Generated by Django 5.0 on 2025-03-20 22:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_alter_eventparticipant_options_eventparticipant_role_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Funcao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Função',
                'verbose_name_plural': 'Funções',
                'ordering': ['nome'],
            },
        ),
        migrations.AlterField(
            model_name='eventparticipant',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='events.funcao', verbose_name='Função'),
        ),
    ]
