from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from app.models import Questao, Conteudo
from app.forms import QuestaoForm
from app.serializers import QuestaoSerializer


class QuestaoList(generics.ListAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer


class QuestaoDetail(generics.RetrieveAPIView):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer


class QuestaoViewSet(viewsets.ModelViewSet):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        All actions require authentication.
        """
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        from django.db.models import Q

        queryset = Questao.objects.all()

        # ============================================================
        # BUSCA
        # ============================================================

        search = self.request.query_params.get('search')

        if search:
            queryset = queryset.filter(
                enunciado__icontains=search
            )

        # ============================================================
        # IDS DOS FILTROS
        # ============================================================

        area_ids = (
            self.request.query_params.getlist('area_id')
            or self.request.query_params.getlist('area_ids')
        )

        unidade_ids = (
            self.request.query_params.getlist('unidade_id')
            or self.request.query_params.getlist('unidade_ids')
        )

        topico_ids = (
            self.request.query_params.getlist('topico_id')
            or self.request.query_params.getlist('topico_ids')
        )

        subtopico_ids = (
            self.request.query_params.getlist('subtopico_id')
            or self.request.query_params.getlist('subtopico_ids')
        )

        categoria_ids = (
            self.request.query_params.getlist('categoria_id')
            or self.request.query_params.getlist('categoria_ids')
        )

        # ============================================================
        # CONVERTER IDS PARA INT
        # ============================================================

        def parse_ids(values):
            result = []

            for value in values:
                try:
                    result.append(int(value))
                except (ValueError, TypeError):
                    pass

            return result

        area_ids_int = parse_ids(area_ids)
        unidade_ids_int = parse_ids(unidade_ids)
        topico_ids_int = parse_ids(topico_ids)
        subtopico_ids_int = parse_ids(subtopico_ids)
        categoria_ids_int = parse_ids(categoria_ids)

        # ============================================================
        # FILTRO HIERÁRQUICO
        #
        # Cada seleção de nível superior pode coexistir com seleções
        # de outras áreas.
        #
        # Exemplo:
        #
        # área 1 + unidade 1
        # OU
        # área 2
        #
        # ============================================================

        hierarchy_q = Q()

        # ------------------------------------------------------------
        # CASO 1:
        # Existe alguma seleção de área
        # ------------------------------------------------------------

        if area_ids_int:

            for area_id in area_ids_int:

                area_q = Q(area_id=area_id)

                # ====================================================
                # UNIDADES PERTENCENTES À ÁREA
                # ====================================================

                unidades_da_area = Conteudo.objects.filter(
                    tipo='unidade',
                    pai_id=area_id
                )

                unidades_da_area_ids = list(
                    unidades_da_area.values_list('id', flat=True)
                )

                unidades_selecionadas_da_area = [
                    uid
                    for uid in unidade_ids_int
                    if uid in unidades_da_area_ids
                ]

                # ====================================================
                # TÓPICOS PERTENCENTES ÀS UNIDADES DA ÁREA
                # ====================================================

                topicos_da_area = Conteudo.objects.filter(
                    tipo='topico',
                    pai_id__in=unidades_da_area_ids
                )

                topicos_da_area_ids = list(
                    topicos_da_area.values_list('id', flat=True)
                )

                topicos_selecionados_da_area = [
                    tid
                    for tid in topico_ids_int
                    if tid in topicos_da_area_ids
                ]

                # ====================================================
                # SUBTÓPICOS PERTENCENTES À ÁREA
                # ====================================================

                subtopicos_da_area = Conteudo.objects.filter(
                    tipo='subtopico',
                    pai_id__in=topicos_da_area_ids
                )

                subtopicos_da_area_ids = list(
                    subtopicos_da_area.values_list('id', flat=True)
                )

                subtopicos_selecionados_da_area = [
                    sid
                    for sid in subtopico_ids_int
                    if sid in subtopicos_da_area_ids
                ]

                # ====================================================
                # CATEGORIAS PERTENCENTES À ÁREA
                # ====================================================

                categorias_da_area = Conteudo.objects.filter(
                    tipo='categoria',
                    pai_id__in=subtopicos_da_area_ids
                )

                categorias_da_area_ids = list(
                    categorias_da_area.values_list('id', flat=True)
                )

                categorias_selecionadas_da_area = [
                    cid
                    for cid in categoria_ids_int
                    if cid in categorias_da_area_ids
                ]

                # ====================================================
                # AGORA DEFINIMOS O FILTRO DESTA ÁREA
                # ====================================================

                # ----------------------------------------------------
                # Se há unidade selecionada DENTRO desta área
                # ----------------------------------------------------

                if unidades_selecionadas_da_area:

                    area_q &= Q(
                        unidade_id__in=unidades_selecionadas_da_area
                    )

                # ----------------------------------------------------
                # Se há tópico selecionado DENTRO desta área
                # ----------------------------------------------------

                if topicos_selecionados_da_area:

                    area_q &= Q(
                        topico_id__in=topicos_selecionados_da_area
                    )

                # ----------------------------------------------------
                # Se há subtópico selecionado DENTRO desta área
                # ----------------------------------------------------

                if subtopicos_selecionados_da_area:

                    area_q &= Q(
                        subtopico_id__in=subtopicos_selecionados_da_area
                    )

                # ----------------------------------------------------
                # Se há categoria selecionada DENTRO desta área
                # ----------------------------------------------------

                if categorias_selecionadas_da_area:

                    area_q &= Q(
                        categoria_id__in=categorias_selecionadas_da_area
                    )

                # ----------------------------------------------------
                # IMPORTANTE:
                #
                # Se a área não possui nenhum filtro filho selecionado,
                # ela continua inteira.
                #
                # Ex:
                #
                # área 1 + unidade 1
                # área 2
                #
                # vira:
                #
                # (área 1 AND unidade 1)
                # OR
                # (área 2)
                # ----------------------------------------------------

                hierarchy_q |= area_q

            queryset = queryset.filter(hierarchy_q)

        # ============================================================
        # CASO 2:
        # Não existe área selecionada
        #
        # Nesse caso os filtros filhos funcionam normalmente.
        # ============================================================

        else:

            if unidade_ids_int:
                queryset = queryset.filter(
                    unidade_id__in=unidade_ids_int
                )

            if topico_ids_int:
                queryset = queryset.filter(
                    topico_id__in=topico_ids_int
                )

            if subtopico_ids_int:
                queryset = queryset.filter(
                    subtopico_id__in=subtopico_ids_int
                )

            if categoria_ids_int:
                queryset = queryset.filter(
                    categoria_id__in=categoria_ids_int
                )

        # ============================================================
        # ANO
        # ============================================================

        anos = self.request.query_params.getlist('ano')

        if anos:

            anos_int = parse_ids(anos)

            if anos_int:
                queryset = queryset.filter(
                    ano__in=anos_int
                )

        # ============================================================
        # BANCA
        # ============================================================

        bancas = self.request.query_params.getlist('banca')

        if bancas:

            banca_q = Q()

            for banca in bancas:

                banca = str(banca).strip()

                if banca:
                    banca_q |= Q(
                        banca__iexact=banca
                    )

            if banca_q:
                queryset = queryset.filter(banca_q)

        # ============================================================
        # TIPO DE QUESTÃO
        # ============================================================

        tipos_questao = self.request.query_params.getlist(
            'tipo_questao'
        )

        if tipos_questao:

            queryset = queryset.filter(
                tipo_questao__in=tipos_questao
            )

        # ============================================================
        # DIFICULDADE
        # ============================================================

        dificuldades = self.request.query_params.getlist(
            'dificuldade'
        )

        if dificuldades:

            queryset = queryset.filter(
                dificuldade__in=dificuldades
            )

        # ============================================================
        # GRAU DE ESCOLARIDADE
        # ============================================================

        graus_escolaridade = self.request.query_params.getlist(
            'grau_escolaridade'
        )

        if graus_escolaridade:

            queryset = queryset.filter(
                grau_escolaridade__in=graus_escolaridade
            )

        # ============================================================
        # TEM IMAGEM
        # ============================================================

        tem_imagem = self.request.query_params.get(
            'tem_imagem'
        )

        if tem_imagem is not None:

            if tem_imagem.lower() == 'true':

                queryset = queryset.filter(
                    Q(enunciado__icontains='<img')
                    |
                    Q(resposta__icontains='<img')
                )

            elif tem_imagem.lower() == 'false':

                queryset = queryset.exclude(
                    Q(enunciado__icontains='<img')
                    |
                    Q(resposta__icontains='<img')
                )

        return queryset


@api_view(["GET"])
def list_questoes(request):
    questions = Questao.objects.all()
    serializer = QuestaoSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def questao_detail(request, pk):
    try:
        question = Questao.objects.get(pk=pk)
    except Questao.DoesNotExist:
        return Response({"detail": "Questão não encontrada"}, status=404)
    serializer = QuestaoSerializer(question)
    return Response(serializer.data)


def is_staff(user):
    return user.is_authenticated and user.is_staff

def authenticate_jwt_request(request):
    """
    Autentica a requisição usando JWT token do header Authorization ou cookie.
    Retorna o usuário se autenticado, None caso contrário.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    jwt_auth = JWTAuthentication()
    token = None
    
    # Tentar obter token do header Authorization primeiro
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        logger.debug("Token obtido do header Authorization")
    else:
        # Tentar obter token do cookie
        token = request.COOKIES.get('jwt_token')
        if token:
            logger.debug("Token obtido do cookie")
        else:
            logger.debug(f"Cookie jwt_token não encontrado. Cookies disponíveis: {list(request.COOKIES.keys())}")
    
    if token:
        try:
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            logger.debug(f"Usuário autenticado: {user.username}, is_staff: {user.is_staff}")
            return user
        except (InvalidToken, TokenError, KeyError, IndexError) as e:
            logger.debug(f"Erro ao validar token: {e}")
            pass
    return None

def cadastro_questao(request):
    import logging
    logger = logging.getLogger(__name__)
    
    # Verificar autenticação via JWT primeiro (para requisições do frontend)
    user = authenticate_jwt_request(request)
    logger.debug(f"Usuário após authenticate_jwt_request: {user}")
    
    # Se não autenticado via JWT, verificar sessão Django (para uso direto no navegador)
    if not user:
        user = request.user if request.user.is_authenticated else None
        logger.debug(f"Usuário após verificar sessão: {user}")
    
    # Verificar se está autenticado e é staff
    # Quando autenticado via JWT, o user existe mas pode não ter is_authenticated=True
    # Então verificamos se user existe e é staff
    if not user:
        logger.debug("Nenhum usuário encontrado")
        messages.error(request, "Você precisa estar autenticado para acessar esta página.")
        return redirect('/')
    
    if not user.is_staff:
        logger.debug(f"Usuário {user.username} não é staff")
        messages.error(request, "Você precisa ser staff para acessar esta página.")
        return redirect('/')
    
    logger.debug(f"Acesso permitido para {user.username} (staff: {user.is_staff})")
    
    # Autenticar o usuário na sessão Django para que o formulário funcione
    from django.contrib.auth import login
    if not request.user.is_authenticated or request.user != user:
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    if request.method == 'POST':
        form = QuestaoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão cadastrada com sucesso!")
            return redirect('cadastro_questao')
        else:
            messages.error(request, "Erro ao cadastrar questão.")
    else:
        form = QuestaoForm()

    areas = Conteudo.objects.filter(tipo='area')
    return render(request, 'app/cadastro_questao.html', {'form': form, 'areas': areas})


def inicio(request):
    return render(request, 'app/inicio.html')

