# Generated by Django 5.0 on 2025-03-20 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='address_complement',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Complemento'),
        ),
        migrations.AddField(
            model_name='person',
            name='address_number',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Número'),
        ),
        migrations.AddField(
            model_name='person',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Cidade'),
        ),
        migrations.AddField(
            model_name='person',
            name='document_id',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Documento (CPF/RG)'),
        ),
        migrations.AddField(
            model_name='person',
            name='neighborhood',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Bairro'),
        ),
        migrations.AddField(
            model_name='person',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Observações'),
        ),
        migrations.AddField(
            model_name='person',
            name='state',
            field=models.CharField(blank=True, max_length=2, null=True, verbose_name='Estado'),
        ),
        migrations.AddField(
            model_name='person',
            name='zipcode',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='CEP'),
        ),
        migrations.AlterField(
            model_name='person',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Logradouro'),
        ),
    ]
