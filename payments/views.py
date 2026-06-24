from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=True, methods=["patch"])
    def pay(self, request, pk=None):
        payment = self.get_object()

        if payment.status == "paid":
            return Response(
                {"error": "Payment already paid"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.status = "paid"
        payment.paid_at = now()
        payment.save()

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Views HTML para templates
def payment_list_view(request):
    payments = Payment.objects.all().order_by('-created_at')
    return render(request, 'payments/payment_list.html', {'payments': payments})


def payment_detail_view(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'payments/payment_detail.html', {'payment': payment})


@login_required
def simular_pagamento_view(request, pedido_id):
    from orders.models import Pedido
    from orders.services import PedidoService
    from django.contrib import messages
    
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    if pedido.status_pedido == 'pago':
        messages.warning(request, "Este pedido já foi pago.")
        return redirect('orders:pedido-detail', pk=pedido.id)
        
    if request.method == 'POST':
        method = request.POST.get('method', 'pix')
        
        # Criar registro de Payment
        payment, created = Payment.objects.get_or_create(
            pedido=pedido,
            defaults={
                'usuario': request.user,
                'amount': pedido.valor_total,
                'method': method,
                'status': 'paid',
                'paid_at': now()
            }
        )
        if not created:
            payment.status = 'paid'
            payment.paid_at = now()
            payment.save()
            
        # Atualizar status do pedido no serviço
        PedidoService.confirmar_pagamento(pedido, forma_pagamento=method, status_pagamento='confirmado')
        
        messages.success(request, "Pagamento confirmado com sucesso!")
        return redirect('orders:pedido-detail', pk=pedido.id)
        
    return render(request, 'payments/simular_pagamento.html', {
        'pedido': pedido,
    })
