from django.contrib import admin

from .models import Disciplina, Duvida, HorarioAtendimento


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nome", "ativa"]
    list_filter = ["ativa"]
    search_fields = ["codigo", "nome"]
    filter_horizontal = ["monitores"]


@admin.register(Duvida)
class DuvidaAdmin(admin.ModelAdmin):
    list_display = ["titulo", "disciplina", "autor", "monitor", "situacao", "criada_em"]
    list_filter = ["situacao", "disciplina"]
    search_fields = ["titulo", "descricao", "autor__username"]
    readonly_fields = ["criada_em", "atualizada_em"]


@admin.register(HorarioAtendimento)
class HorarioAtendimentoAdmin(admin.ModelAdmin):
    list_display = ["monitor", "disciplina", "dia_semana", "inicio", "fim"]
    list_filter = ["disciplina", "dia_semana"]
    search_fields = ["monitor__username", "disciplina__nome"]
