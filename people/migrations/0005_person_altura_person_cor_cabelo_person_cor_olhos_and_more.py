# Generated by Django 5.0 on 2025-03-20 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0004_alter_personcontact_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='altura',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, verbose_name='Altura (m)'),
        ),
        migrations.AddField(
            model_name='person',
            name='cor_cabelo',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Cor do cabelo'),
        ),
        migrations.AddField(
            model_name='person',
            name='cor_olhos',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Cor dos olhos'),
        ),
        migrations.AddField(
            model_name='person',
            name='peso',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Peso (kg)'),
        ),
    ]
