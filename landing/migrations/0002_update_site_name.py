from django.db import migrations

def update_site_name(apps, schema_editor):
    SiteSettings = apps.get_model('landing', 'SiteSettings')
    # Atualiza todos os registros existentes
    SiteSettings.objects.all().update(site_name="Agência Atitude")
    # Se não existir nenhum registro, cria um
    if not SiteSettings.objects.exists():
        SiteSettings.objects.create(site_name="Agência Atitude")

class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_site_name),
    ]
