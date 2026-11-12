from orders.models import Order
from orders.models import RefundRequest
from django.utils import timezone

from .tracking_data import DELIVERY_DATA


def get_order_by_id(order_id):
    """
    Retrieve an order by its ID.

    Args:
        order_id (int): The ID of the order to retrieve.

    Returns:
        Order: The order instance if found, otherwise None.
    """
    try:
        order = Order.objects.get(id=order_id)
        return {
            "order_id": order.id,
            "order_name": order.name,
            "ammount": order.amount,
            "status": order.status,
            "carrier": order.carrier,
            "tracking_number": order.tracking_number,
            "delivery_address": order.delivery_address,
            "ordered_on": order.created_at.strftime("%Y-%m-%d)"),
            "days_since_ordered": (timezone.now() - order.created_at).days,
        }
    except Order.DoesNotExist:
        return {"error": f"Order with ID {order_id} does not exist."}


def get_refund_history_by_user_id(user_id):
    """
    Retrieve refund requests for a user, newest first.

    Args:
        user_id (int): The ID of the user whose refund history is requested.

    Returns:
        list[dict]: Refund details, including their associated order.
    """
    refunds = (
        RefundRequest.objects.filter(user_id=user_id)
        .select_related("order")
        .order_by("-created_at", "-id")
    )
    return [
        {
            "refund_id": refund.id,
            "order_id": refund.order_id,
            "product_name": refund.order.product_name,
            "amount": str(refund.order.amount),
            "status": refund.status,
            "reason": refund.reason,
            "created_at": refund.created_at.isoformat(),
        }
        for refund in refunds
    ]


def check_delivery_status(tracking_number):
    """
    Retrieve delivery information for a tracking number.

    Args:
        tracking_number (str): The tracking number to look up.

    Returns:
        dict: Delivery details if found, otherwise a default not-found response.
    """
    tracking_number = tracking_number.strip().upper()
    delivery = DELIVERY_DATA.get(tracking_number)
    if delivery is None:
        return {
            "tracking_number": tracking_number,
            "status": "Not Found",
            "last_location": None,
            "last_update": None,
            "estimated_delivery": None,
            "delay_reason": None,
            "message": "No delivery information was found for this tracking number.",
        }

    return {"tracking_number": tracking_number, **delivery}
