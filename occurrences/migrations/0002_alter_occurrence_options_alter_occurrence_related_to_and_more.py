# Generated by Django 5.0 on 2025-03-20 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('occurrences', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='occurrence',
            options={'ordering': ['-date'], 'verbose_name': 'Ocorrência', 'verbose_name_plural': 'Ocorrências'},
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='related_to',
            field=models.CharField(choices=[('client', 'Cliente'), ('person', 'Pessoa')], max_length=10),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='status',
            field=models.CharField(choices=[('pending', 'Pendente'), ('in_progress', 'Em Andamento'), ('resolved', 'Resolvido'), ('closed', 'Fechado')], default='pending', max_length=20),
        ),
    ]
