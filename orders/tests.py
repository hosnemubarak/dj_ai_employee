from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Order, RefundRequest


class OrderListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.customer = user_model.objects.create_user(
            username='customer',
            password='customer-password',
        )
        cls.other_customer = user_model.objects.create_user(
            username='other',
            password='other-password',
        )
        cls.staff = user_model.objects.create_user(
            username='staff',
            password='staff-password',
            is_staff=True,
        )
        Order.objects.create(
            user=cls.customer,
            product_name='Customer item',
            amount='12.50',
            created_at=timezone.now(),
        )
        Order.objects.create(
            user=cls.other_customer,
            product_name='Other customer item',
            amount='20.00',
            created_at=timezone.now(),
        )
        cls.customer_order = Order.objects.get(user=cls.customer)
        cls.other_order = Order.objects.get(user=cls.other_customer)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('order_list'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('order_list')}",
        )

    def test_homepage_redirects_to_orders(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('order_list'))

    def test_customer_sees_only_their_own_orders(self):
        self.client.force_login(self.customer)

        response = self.client.get(reverse('order_list'))

        self.assertContains(response, 'Customer item')
        self.assertNotContains(response, 'Other customer item')
        self.assertContains(
            response,
            reverse('order_detail', args=(self.customer_order.pk,)),
        )

    def test_customer_can_view_their_order_details(self):
        self.client.force_login(self.customer)

        response = self.client.get(
            reverse('order_detail', args=(self.customer_order.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_detail.html')
        self.assertContains(response, 'Customer item')
        self.assertContains(response, 'Refund history')
        self.assertContains(response, 'There are no refund requests')

    def test_order_details_show_refund_history(self):
        refund = RefundRequest.objects.create(
            order=self.customer_order,
            user=self.customer,
            reason='Package arrived damaged',
            status='approved',
            created_at=timezone.now(),
        )
        self.client.force_login(self.customer)

        response = self.client.get(
            reverse('order_detail', args=(self.customer_order.pk,))
        )

        self.assertContains(response, 'Refund history')
        self.assertContains(response, f'Refund #{refund.pk}')
        self.assertContains(response, 'Approved')
        self.assertContains(response, 'Package arrived damaged')

    def test_customer_cannot_view_another_customers_order(self):
        self.client.force_login(self.customer)

        response = self.client.get(
            reverse('order_detail', args=(self.other_order.pk,))
        )

        self.assertEqual(response.status_code, 404)

    def test_staff_can_view_any_order_details(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse('order_detail', args=(self.other_order.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Other customer item')

    def test_staff_user_sees_all_orders(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse('order_list'))

        self.assertContains(response, 'Customer item')
        self.assertContains(response, 'Other customer item')

    def test_successful_login_redirects_to_orders(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'customer', 'password': 'customer-password'},
        )

        self.assertRedirects(response, reverse('order_list'))

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.customer)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))


class ErrorPageTests(TestCase):
    @override_settings(DEBUG=False)
    def test_not_found_page_uses_custom_template(self):
        response = self.client.get('/this-page-does-not-exist/')

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        self.assertContains(response, 'We could not find that page', status_code=404)

    def test_standard_error_templates_are_available(self):
        for template_name in ('400.html', '403.html', '403_csrf.html', '404.html', '500.html'):
            with self.subTest(template=template_name):
                self.assertIsNotNone(get_template(template_name))
