from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

class Conteudo(models.Model):
    nome = models.CharField(max_length=500)
    pai = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='subconteudos')
    
    TIPO_CHOICES = [
        ('area', 'Área'),
        ('unidade', 'Unidade'),
        ('topico', 'Tópico'),
        ('subtopico', 'Subtópico'),
        ('categoria', 'Categoria'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        if self.pai:
            return f"{self.nome} ({self.get_tipo_display()})"
        return f"{self.nome} ({self.get_tipo_display()})"

class Questao(models.Model):
    area = models.ForeignKey('Conteudo', on_delete=models.PROTECT, related_name='q_area')
    unidade = models.ForeignKey('Conteudo', on_delete=models.PROTECT, related_name='q_unidade', null=True, blank=True)
    topico = models.ForeignKey('Conteudo', on_delete=models.PROTECT, related_name='q_topico', null=True, blank=True)
    subtopico = models.ForeignKey('Conteudo', on_delete=models.PROTECT, related_name='q_subtopico', null=True, blank=True)
    categoria = models.ForeignKey('Conteudo', on_delete=models.PROTECT, related_name='q_categoria', null=True, blank=True)

    ano = models.IntegerField()
    banca = models.CharField(max_length=100)
    tipo_questao = models.CharField(max_length=50)
    dificuldade = models.CharField(max_length=20)
    
    GRAU_ESCOLARIDADE_CHOICES = [
        ('fundamental', 'Ensino Fundamental'),
        ('medio', 'Ensino Médio'),
        ('superior', 'Ensino Superior'),
    ]
    grau_escolaridade = models.CharField(max_length=20, choices=GRAU_ESCOLARIDADE_CHOICES)
    
    enunciado = RichTextUploadingField('Enunciado')
    resposta = RichTextUploadingField('Resposta')
    resposta_gabarito = RichTextUploadingField('Resposta Gabarito', blank=True, null=True)


class AboutImage(models.Model):
    image = models.ImageField(upload_to='about/')
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='about_images',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Imagem Sobre #{self.id}"
