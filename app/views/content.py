from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.models import Conteudo, Questao
from app.serializers import ConteudoSerializer


def buscar_conteudos_filho(request):
    pai_id = request.GET.get('pai_id')
    if not pai_id:
        return JsonResponse({'error': 'pai_id ausente'}, status=400)

    filhos = Conteudo.objects.filter(pai_id=pai_id).values('id', 'nome')
    return JsonResponse(list(filhos), safe=False)


@api_view(["GET"])
def list_conteudos(request):
    """List all Conteudos, optionally filtered by tipo and pai_id"""
    conteudos = Conteudo.objects.all()
    
    tipo = request.query_params.get('tipo', None)
    if tipo:
        conteudos = conteudos.filter(tipo=tipo)
    
    pai_id = request.query_params.get('pai_id', None)
    if pai_id:
        conteudos = conteudos.filter(pai_id=pai_id)
    else:
        if tipo:
            conteudos = conteudos.filter(pai__isnull=True)
    
    serializer = ConteudoSerializer(conteudos, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_unique_values(request):
    """Get unique values for fields like banca, tipo_questao, dificuldade, ano"""
    field = request.query_params.get('field', None)
    
    if not field:
        return Response({"error": "Field parameter is required"}, status=400)
    
    if field == 'banca':
        # Normalizar para reduzir inconsistência de filtro (ENEM vs Enem, etc.)
        values = (
            Questao.objects
            .exclude(banca__isnull=True)
            .exclude(banca__exact="")
            .values_list('banca', flat=True)
            .distinct()
        )
        normalized = sorted({(v or "").strip().upper() for v in values if (v or "").strip()})
        # Bancas "fixas" que precisam sempre aparecer na lista
        for fixed in ("IFRN", "IFPB"):
            if fixed not in normalized:
                normalized.append(fixed)
        normalized.sort()
        return Response(normalized)
    elif field == 'tipo_questao':
        values = Questao.objects.values_list('tipo_questao', flat=True).distinct().order_by('tipo_questao')
    elif field == 'dificuldade':
        values = Questao.objects.values_list('dificuldade', flat=True).distinct().order_by('dificuldade')
    elif field == 'ano':
        values = Questao.objects.values_list('ano', flat=True).distinct().order_by('-ano')
    elif field == 'grau_escolaridade':
        values = Questao.objects.values_list('grau_escolaridade', flat=True).distinct().order_by('grau_escolaridade')
    else:
        return Response({"error": "Invalid field"}, status=400)
    
    return Response(list(values))

