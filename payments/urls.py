from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, payment_list_view, payment_detail_view, simular_pagamento_view

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="api-payments")

app_name = "payments"

urlpatterns = [
    # Rotas HTML (templates)
    path('', payment_list_view, name='payment-list'),
    path('<int:pk>/', payment_detail_view, name='payment-detail'),
    path('pagar/<int:pedido_id>/', simular_pagamento_view, name='simular-pagamento'),
    
    # Rotas API REST
    path('api/', include(router.urls)),
]
