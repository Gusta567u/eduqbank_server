from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'questoes', views.QuestaoViewSet)

urlpatterns = [
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/user-info/', views.user_info, name='user_info'),
    path('auth/update-profile/', views.update_user_profile, name='update_user_profile'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('buscar-conteudos/', views.buscar_conteudos_filho, name='buscar_conteudos'),
    path('conteudos/', views.list_conteudos, name='list_conteudos'),
    path('unique-values/', views.get_unique_values, name='get_unique_values'),
    path('print-test/docx/', views.print_test_docx, name='print_test_docx'),
    path('about/images/', views.list_about_images, name='list_about_images'),
    path('about/images/upload/', views.upload_about_image, name='upload_about_image'),
    path('', include(router.urls)),
]