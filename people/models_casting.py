from django.db import models
from django.utils import timezone
import uuid

class CastingCatalog(models.Model):
    """
    Modelo para armazenar catálogos de casting com filtros específicos
    """
    name = models.CharField(max_length=255, verbose_name="Nome do Catálogo")
    description = models.TextField(verbose_name="Descrição")
    company = models.CharField(max_length=255, blank=True, null=True, verbose_name="Empresa/Cliente")
    date_created = models.DateTimeField(default=timezone.now, verbose_name="Data de Criação")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Filtros salvos
    min_height = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, verbose_name="Altura Mínima (m)")
    max_height = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, verbose_name="Altura Máxima (m)")
    min_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Peso Mínimo (kg)")
    max_weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="Peso Máximo (kg)")
    min_age = models.IntegerField(blank=True, null=True, verbose_name="Idade Mínima")
    max_age = models.IntegerField(blank=True, null=True, verbose_name="Idade Máxima")
    manequim = models.CharField(max_length=50, blank=True, null=True, verbose_name="Manequim")
    
    # Relacionamentos para filtros
    eye_colors = models.ManyToManyField('people.CorOlhos', blank=True, verbose_name="Cores de Olhos")
    hair_colors = models.ManyToManyField('people.CorCabelo', blank=True, verbose_name="Cores de Cabelo")
    skin_colors = models.ManyToManyField('people.CorPele', blank=True, verbose_name="Cores de Pele")
    genders = models.ManyToManyField('people.Genero', blank=True, verbose_name="Gêneros")
    professional_categories = models.ManyToManyField('people.ProfessionalCategory', blank=True, verbose_name="Categorias Profissionais")
    
    # Filtro de avaliações
    min_efficiency = models.IntegerField(blank=True, null=True, verbose_name="Eficiência Mínima")
    min_punctuality = models.IntegerField(blank=True, null=True, verbose_name="Pontualidade Mínima")
    min_proactivity = models.IntegerField(blank=True, null=True, verbose_name="Proatividade Mínima")
    min_appearance = models.IntegerField(blank=True, null=True, verbose_name="Aparência Mínima")
    min_communication = models.IntegerField(blank=True, null=True, verbose_name="Comunicação Mínima")
    
    # Filtro de cidade/estado
    cities = models.TextField(blank=True, null=True, verbose_name="Cidades")
    states = models.TextField(blank=True, null=True, verbose_name="Estados")
    
    # Filtro de status
    status_choices = models.TextField(blank=True, null=True, verbose_name="Status")
    
    # Filtro de origem do cadastro
    origem_cadastro = models.TextField(blank=True, null=True, verbose_name="Origem do Cadastro")
    
    # Pessoas incluídas manualmente (além dos filtros)
    included_people = models.ManyToManyField(
        'people.Person',  
        related_name='manual_castings',
        blank=True,
        verbose_name="Pessoas Incluídas Manualmente"
    )
    
    # Pessoas excluídas manualmente (mesmo que atendam aos filtros)
    excluded_people = models.ManyToManyField(
        'people.Person',  
        related_name='excluded_castings',
        blank=True,
        verbose_name="Pessoas Excluídas Manualmente"
    )
    
    # Filtro de texto livre (para busca por nome)
    search_query = models.CharField(max_length=255, blank=True, null=True, verbose_name="Busca por Nome")
    
    # Campo para armazenar a query completa em JSON (para casos mais complexos)
    filter_json = models.JSONField(blank=True, null=True, verbose_name="Filtros em JSON")
    
    class Meta:
        verbose_name = 'Catálogo de Casting'
        verbose_name_plural = 'Catálogos de Casting'
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.name} ({self.date_created.strftime('%d/%m/%Y')})"
    
    def get_filtered_people(self):
        """
        Retorna a lista de pessoas que atendem aos critérios de filtro
        """
        from .models import Person
        
        queryset = Person.objects.all()
        
        # Aplicar filtros de busca por nome
        if self.search_query:
            queryset = queryset.filter(name__icontains=self.search_query)
        
        # Aplicar filtros de características físicas
        if self.min_height:
            queryset = queryset.filter(altura__gte=self.min_height)
        if self.max_height:
            queryset = queryset.filter(altura__lte=self.max_height)
        if self.min_weight:
            queryset = queryset.filter(peso__gte=self.min_weight)
        if self.max_weight:
            queryset = queryset.filter(peso__lte=self.max_weight)
        if self.min_age:
            queryset = queryset.filter(idade__gte=self.min_age)
        if self.max_age:
            queryset = queryset.filter(idade__lte=self.max_age)
        if self.manequim:
            queryset = queryset.filter(manequim=self.manequim)
        
        # Aplicar filtros de relacionamentos
        if self.eye_colors.exists():
            queryset = queryset.filter(cor_olhos__in=self.eye_colors.all())
        if self.hair_colors.exists():
            queryset = queryset.filter(cor_cabelo__in=self.hair_colors.all())
        if self.skin_colors.exists():
            queryset = queryset.filter(cor_pele__in=self.skin_colors.all())
        if self.genders.exists():
            queryset = queryset.filter(genero__in=self.genders.all())
        if self.professional_categories.exists():
            queryset = queryset.filter(professional_categories__in=self.professional_categories.all()).distinct()
        
        # Aplicar filtros de avaliações
        if self.min_efficiency:
            queryset = queryset.filter(efficiency__gte=self.min_efficiency)
        if self.min_punctuality:
            queryset = queryset.filter(punctuality__gte=self.min_punctuality)
        if self.min_proactivity:
            queryset = queryset.filter(proactivity__gte=self.min_proactivity)
        if self.min_appearance:
            queryset = queryset.filter(appearance__gte=self.min_appearance)
        if self.min_communication:
            queryset = queryset.filter(communication__gte=self.min_communication)
        
        # Aplicar filtros de cidade/estado
        if self.cities:
            city_list = [city.strip() for city in self.cities.split(',')]
            queryset = queryset.filter(city__in=city_list)
        if self.states:
            state_list = [state.strip() for state in self.states.split(',')]
            queryset = queryset.filter(state__in=state_list)
        
        # Aplicar filtro de status
        if self.status_choices:
            status_list = [status.strip() for status in self.status_choices.split(',')]
            queryset = queryset.filter(status__in=status_list)
        
        # Aplicar filtro de origem do cadastro
        if self.origem_cadastro:
            origem_list = [origem.strip() for origem in self.origem_cadastro.split(',')]
            queryset = queryset.filter(origem_cadastro__in=origem_list)
        
        # Incluir pessoas manualmente adicionadas
        manual_people = self.included_people.all().distinct()
        if manual_people.exists():
            queryset = queryset.distinct()
            queryset = (queryset | manual_people)
        
        # Excluir pessoas manualmente removidas
        excluded_people = self.excluded_people.all()
        if excluded_people.exists():
            queryset = queryset.exclude(id__in=excluded_people.values_list('id', flat=True))
        
        return queryset

class PublicCatalogLink(models.Model):
    """
    Modelo para links públicos de catálogos de casting, permitindo acesso sem login
    """
    catalog = models.ForeignKey(CastingCatalog, on_delete=models.CASCADE, related_name='public_links', verbose_name="Catálogo")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Token de Acesso")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name="Data de Expiração")
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Criado por")
    
    class Meta:
        verbose_name = "Link Público de Catálogo"
        verbose_name_plural = "Links Públicos de Catálogos"
        
    def __str__(self):
        return f"Link para {self.catalog.name}"
    
    @property
    def is_expired(self):
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at
    
    @property
    def public_url(self):
        from django.urls import reverse
        return reverse('people:public_catalog_view', kwargs={'token': self.token})
