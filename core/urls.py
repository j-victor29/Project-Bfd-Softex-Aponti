"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import home, sobre, como_testar

urlpatterns = [
    path('', home, name='home'),
    path('sobre/', sobre, name='sobre'),
    path('como-testar/', como_testar, name='como-testar'),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('products/', include('products.urls')),
    path("orders/", include("orders.urls")),
    path('artists/', include('artists.urls')),
    path('creations/', include('creations.urls')),
    path("payments/", include("payments.urls")),
    path('gamification/', include('gamification.urls')),
    path('users/', include('users.urls')),
    path('printing/', include('printing.urls')),
    path('carrinho/', include('cart.urls')),
]

# Servir media files em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# NÃO MEXA ISSO AQUI QUE ESTÁ COMENTADO!!!!
# urlpatterns = [
#     path("api/", include("orders.urls")),
# ]

# urlpatterns = [
#     path('api/artists/', include('artists.urls')),
# ]

# urlpatterns = [
#     path('api/creations/', include('creations.urls')),
# ]