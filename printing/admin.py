from django.contrib import admin
from .models import Impressora, FilaImpressao


@admin.register(Impressora)
class ImpressoraAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'status', 'localizacao', 'fabricante', 'data_criacao')
    list_filter = ('tipo', 'status', 'data_criacao')
    search_fields = ('nome', 'fabricante', 'modelo', 'localizacao')
    readonly_fields = ('data_criacao',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'tipo', 'status')
        }),
        ('Especificações', {
            'fields': ('fabricante', 'modelo', 'localizacao')
        }),
        ('Datas', {
            'fields': ('data_aquisicao', 'data_ultima_manutencao', 'data_criacao')
        }),
    )


@admin.register(FilaImpressao)
class FilaImpressaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'impressora', 'status', 'prioridade', 'criado_em')
    list_filter = ('status', 'impressora', 'criado_em')
    search_fields = ('pedido__id', 'observacoes')
    readonly_fields = ('criado_em', 'iniciado_em', 'concluido_em')
    ordering = ('-prioridade', 'criado_em')
    
    fieldsets = (
        ('Informações', {
            'fields': ('pedido', 'impressora', 'status', 'prioridade')
        }),
        ('Notas', {
            'fields': ('observacoes',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'iniciado_em', 'concluido_em'),
            'classes': ('collapse',)
        }),
    )