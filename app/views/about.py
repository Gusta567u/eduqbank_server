from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.models import AboutImage


@api_view(["GET"])
def list_about_images(request):
    images = AboutImage.objects.all()
    return Response(
        [
            {
                "id": img.id,
                "url": request.build_absolute_uri(img.image.url),
                "created_at": img.created_at,
            }
            for img in images
            if img.image
        ]
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_about_image(request):
    if not request.user.is_superuser:
        return Response({"detail": "Apenas superusuário pode adicionar imagens."}, status=403)

    image = request.FILES.get("image")
    if not image:
        return Response({"detail": "Envie um arquivo no campo 'image'."}, status=400)

    about_image = AboutImage.objects.create(image=image, uploaded_by=request.user)
    return Response(
        {
            "id": about_image.id,
            "url": request.build_absolute_uri(about_image.image.url),
            "created_at": about_image.created_at,
        },
        status=201,
    )
