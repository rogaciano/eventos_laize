# Generated by Django 5.0 on 2025-03-20 17:50

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('address', models.TextField(blank=True, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='people_photos/')),
                ('efficiency', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('punctuality', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('proactivity', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('appearance', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('communication', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Person',
                'verbose_name_plural': 'People',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PersonContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('whatsapp', 'WhatsApp'), ('email', 'Email'), ('instagram', 'Instagram'), ('other', 'Other')], max_length=20)),
                ('value', models.CharField(max_length=255)),
                ('label', models.CharField(blank=True, help_text='E.g. Personal, Work, etc.', max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='people.person')),
            ],
        ),
    ]
