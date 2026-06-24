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
    from django.db import transaction
    
    try:
        pedido_id = int(pedido_id)
    except (ValueError, TypeError):
        messages.error(request, "ID de pedido inválido.")
        return redirect('orders:pedido-list')
        
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    if pedido.status_pedido == 'pago':
        messages.warning(request, "Este pedido já foi pago.")
        return redirect('orders:pedido-detail', pk=pedido.id)
        
    if pedido.status_pedido in ['cancelado', 'concluido', 'impresso', 'em_producao', 'enviado']:
        messages.error(request, f"Não é possível pagar um pedido com status '{pedido.get_status_pedido_display()}'.")
        return redirect('orders:pedido-detail', pk=pedido.id)
        
    if request.method == 'POST':
        method = request.POST.get('method', 'pix')
        
        method_mapping = {
            'pix': 'pix',
            'boleto': 'boleto',
            'credit_card': 'cartao_credito',
            'debit_card': 'cartao_debito',
        }
        
        if method not in method_mapping:
            messages.error(request, "Método de pagamento inválido.")
            return redirect('payments:simular-pagamento', pedido_id=pedido.id)
            
        pedido_forma_pagamento = method_mapping[method]
        
        try:
            with transaction.atomic():
                # Criar ou obter registro de Payment
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
                    payment.method = method
                    payment.save()
                    
                # Atualizar status do pedido no serviço
                PedidoService.confirmar_pagamento(pedido, forma_pagamento=pedido_forma_pagamento, status_pagamento='confirmado')
                
            messages.success(request, "Pagamento confirmado com sucesso!")
        except ValueError as e:
            messages.error(request, f"Erro ao processar pagamento: {str(e)}")
            
        return redirect('orders:pedido-detail', pk=pedido.id)
        
    return render(request, 'payments/simular_pagamento.html', {
        'pedido': pedido,
    })
