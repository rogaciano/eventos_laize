# Generated by Django 5.0 on 2025-03-20 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0002_person_address_complement_person_address_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='pix',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Chave Pix'),
        ),
    ]
