from django.contrib import admin
from .models import Conteudo, Questao, AboutImage

@admin.register(Conteudo)
class ConteudoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pai', 'tipo')
    search_fields = ('nome',)

@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ('area', 'unidade', 'topico', 'subtopico', 'categoria', 'ano', 'banca', 'tipo_questao', 'dificuldade', 'enunciado')
    search_fields = ('area', 'unidade', 'topico', 'subtopico', 'categoria', 'enunciado')


@admin.register(AboutImage)
class AboutImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_by', 'created_at')
    search_fields = ('uploaded_by__username', 'uploaded_by__email')