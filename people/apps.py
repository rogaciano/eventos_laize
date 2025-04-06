from django.apps import AppConfig


class PeopleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'people'
    
    def ready(self):
        """
        Inicialização do aplicativo.
        Garante que os templatetags sejam carregados corretamente.
        """
        import people.templatetags
