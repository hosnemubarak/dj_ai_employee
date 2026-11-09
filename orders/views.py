from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Order, RefundRequest


@login_required
def order_list(request):
    orders = Order.objects.select_related('user', 'product').order_by('-created_at')
    if not request.user.is_staff:
        orders = orders.filter(user=request.user)

    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    refund_history = RefundRequest.objects.select_related('user').order_by(
        '-created_at'
    )
    orders = Order.objects.select_related('user', 'product').prefetch_related(
        Prefetch('refund_requests', queryset=refund_history)
    )
    if not request.user.is_staff:
        orders = orders.filter(user=request.user)

    order = get_object_or_404(orders, pk=pk)
    return render(request, 'orders/order_detail.html', {'order': order})
