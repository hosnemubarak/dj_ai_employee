from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from orders.models import Order, RefundRequest
from support.tools import check_delivery_status, get_refund_history_by_user_id


class RefundHistoryToolTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.user = user_model.objects.create_user(username="refund-customer")
        cls.other_user = user_model.objects.create_user(username="other-customer")
        cls.order = Order.objects.create(
            user=cls.user,
            product_name="Refundable item",
            amount="19.95",
            created_at=timezone.now(),
        )
        cls.other_order = Order.objects.create(
            user=cls.other_user,
            product_name="Other item",
            amount="29.95",
            created_at=timezone.now(),
        )
        cls.first_refund = RefundRequest.objects.create(
            order=cls.order,
            user=cls.user,
            reason="Item was damaged",
            status="pending",
            created_at=timezone.now() - timezone.timedelta(days=1),
        )
        cls.latest_refund = RefundRequest.objects.create(
            order=cls.order,
            user=cls.user,
            reason="Missing parts",
            status="approved",
            created_at=timezone.now(),
        )
        RefundRequest.objects.create(
            order=cls.other_order,
            user=cls.other_user,
            reason="Different customer refund",
            status="pending",
            created_at=timezone.now(),
        )

    def test_returns_all_refunds_for_user_newest_first(self):
        history = get_refund_history_by_user_id(self.user.id)

        self.assertEqual(
            [refund["refund_id"] for refund in history],
            [self.latest_refund.id, self.first_refund.id],
        )
        self.assertEqual(history[0]["order_id"], self.order.id)
        self.assertEqual(history[0]["product_name"], "Refundable item")
        self.assertEqual(history[0]["amount"], "19.95")
        self.assertEqual(history[0]["status"], "approved")
        self.assertEqual(history[0]["reason"], "Missing parts")
        self.assertIn("created_at", history[0])

    def test_returns_empty_list_when_user_has_no_refunds(self):
        user_without_refunds = get_user_model().objects.create_user(
            username="no-refunds"
        )

        self.assertEqual(get_refund_history_by_user_id(user_without_refunds.id), [])


class DeliveryStatusToolTests(TestCase):
    def test_returns_delivery_data_for_tracking_number(self):
        result = check_delivery_status("bd99281733")

        self.assertEqual(result["tracking_number"], "BD99281733")
        self.assertEqual(result["status"], "In Transit")
        self.assertEqual(result["last_location"], "Bangalore Sorting Hub")
        self.assertEqual(result["delay_reason"], "High volume at sorting facility")

    def test_returns_default_data_for_unknown_tracking_number(self):
        result = check_delivery_status("unknown-tracking-number")

        self.assertEqual(result["tracking_number"], "UNKNOWN-TRACKING-NUMBER")
        self.assertEqual(result["status"], "Not Found")
        self.assertIsNone(result["last_location"])
        self.assertIsNone(result["estimated_delivery"])
        self.assertIn("message", result)
