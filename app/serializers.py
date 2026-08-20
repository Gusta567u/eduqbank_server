# app/serializers.py

from rest_framework import serializers

from .models import Questao, Conteudo
from .utils import html_render_math_to_img

from django.contrib.auth.models import User


class ConteudoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conteudo
        fields = ['id', 'nome', 'tipo', 'pai_id']


class QuestaoListSerializer(serializers.ModelSerializer):
    """
    Serializer leve usado na listagem de questões.

    IMPORTANTE:
    - Não envia enunciado
    - Não envia resposta
    - Não envia resposta_gabarito
    - Não renderiza LaTeX
    """

    area = ConteudoSerializer(read_only=True)
    unidade = ConteudoSerializer(read_only=True)
    topico = ConteudoSerializer(read_only=True)
    subtopico = ConteudoSerializer(read_only=True)
    categoria = ConteudoSerializer(read_only=True)

    class Meta:
        model = Questao
        fields = [
            'id',
            'area',
            'unidade',
            'topico',
            'subtopico',
            'categoria',
            'ano',
            'banca',
            'tipo_questao',
            'dificuldade',
            'grau_escolaridade',
        ]


class QuestaoSerializer(serializers.ModelSerializer):
    """
    Serializer completo usado para buscar uma questão específica.

    Aqui a renderização de LaTeX continua existindo,
    mas agora acontece somente quando necessário.
    """

    area = ConteudoSerializer(read_only=True)
    unidade = ConteudoSerializer(required=False, allow_null=True)
    topico = ConteudoSerializer(required=False, allow_null=True)
    subtopico = ConteudoSerializer(required=False, allow_null=True)
    categoria = ConteudoSerializer(required=False, allow_null=True)

    enunciado_rendered = serializers.SerializerMethodField()
    resposta_rendered = serializers.SerializerMethodField()

    class Meta:
        model = Questao

        fields = [
            'id',
            'area',
            'unidade',
            'topico',
            'subtopico',
            'categoria',
            'ano',
            'banca',
            'tipo_questao',
            'dificuldade',
            'grau_escolaridade',
            'enunciado',
            'resposta',
            'resposta_gabarito',
            'enunciado_rendered',
            'resposta_rendered',
        ]

    def get_enunciado_rendered(self, obj: Questao):
        return html_render_math_to_img(obj.enunciado or "")

    def get_resposta_rendered(self, obj: Questao):
        return html_render_math_to_img(obj.resposta or "")


class QuestaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questao
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
        ]