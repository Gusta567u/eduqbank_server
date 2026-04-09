from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import socket


DISPOSABLE_EMAIL_DOMAINS = {
    "mailinator.com",
    "tempmail.com",
    "10minutemail.com",
    "guerrillamail.com",
    "yopmail.com",
}


def _has_valid_mail_domain(email: str) -> bool:
    try:
        domain = email.split("@", 1)[1].strip().lower()
    except Exception:
        return False

    if not domain or domain in DISPOSABLE_EMAIL_DOMAINS:
        return False

    try:
        socket.getaddrinfo(domain, None)
        return True
    except socket.gaierror:
        return False


@api_view(["POST"])
def signup(request):
    email = (request.data.get("email") or "").strip().lower()
    password = request.data.get("password")

    if not email or not password:
        return Response({"detail": "Campos obrigatórios"}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return Response({"detail": "E-mail inválido."}, status=400)

    if not _has_valid_mail_domain(email):
        return Response({"detail": "Use um e-mail real com domínio válido."}, status=400)

    if User.objects.filter(username=email).exists():
        return Response({"detail": "Email já cadastrado"}, status=400)

    user = User.objects.create_user(username=email, email=email, password=password)
    return Response({"message": "Usuário criado com sucesso"}, status=201)


@api_view(["POST"])
def login_view(request):
    email = request.data.get("email")
    password = request.data.get("password")

    user = authenticate(username=email, password=password)
    if user is None:
        return Response({"detail": "Credenciais inválidas"}, status=400)

    refresh = RefreshToken.for_user(user)
    return Response({
        "token": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser
        }
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    """Retorna informações do usuário autenticado"""
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
        "is_staff": request.user.is_staff,
        "is_superuser": request.user.is_superuser
    })


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Atualiza o perfil do usuário autenticado"""
    username = request.data.get('username')
    
    if not username:
        return Response({"detail": "Nome de usuário é obrigatório"}, status=400)
    
    # Verificar se o username já existe (exceto para o próprio usuário)
    if User.objects.filter(username=username).exclude(id=request.user.id).exists():
        return Response({"detail": "Este nome de usuário já está em uso"}, status=400)
    
    request.user.username = username
    request.user.save()
    
    return Response({
        "message": "Perfil atualizado com sucesso",
        "user": {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "is_staff": request.user.is_staff,
            "is_superuser": request.user.is_superuser
        }
    })

