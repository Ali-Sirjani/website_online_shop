from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

import json

from .models import Order, OrderItem, ShippingAddress
from products.models import Product


class TestCartLoginUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user(email='aliqw@gmail.com', username='aliqw',
                                                         password='q1w2e3r4a')
        cls.user2 = get_user_model().objects.create_user(email='ali12qw@gmail.com', username='ali12qw',
                                                         password='q1w2e3r4a')
        cls.user3 = get_user_model().objects.create_user(email='ali3qw@gmail.com', username='ali3qw',
                                                         password='q1w2e3r4a')

        cls.product1 = Product.objects.create(
            title='ست گیمینگ اونیکوما مدل Professional 5 in 1',
            description='وزن ۳۵۰ گرم نوع اتصال با سیم منبع تغذیه پورت USB نوع رابط USB تعداد کلیدهای میانبر ۴ عدد',
            cover='static/test/blog3.jpg',
            price=12_000,
            discount=True,
            discount_price=11_000,
        )
        cls.product2 = Product.objects.create(
            title='ماشین لباسشویی بوش مدل WAX32E90ME ظرفیت 10 کیلوگرم',
            description='ماشین لباسشویی بوش WAX32E90 از سری HomeProfessional است که '
                        'از جمله سری های فوق العاده شرکت بوش می باشد.',
            cover='static/test/blog5.jpg',
            price=20_000,
            discount=True,
            discount_price=15_000,
        )
        cls.product3 = Product.objects.create(
            title='ماوس گرین مدل GM606-RGB',
            description='ماوس های نسل جدید مجهز به بدنه مشبک به لطف وزن به مراتب کمتر و '
                        'تهویه کارآمد که تعریق کمتر دست را به دنبال دارد، به',
            cover='static/test/blog-1.jpg',
            price=5_000,
        )
        cls.product4 = Product.objects.create(
            title='شارژر دیواری لیتو مدل LH13 به همراه کابل تبدیل microUSB',
            description='شارژرهای دیواری به یکی از پرمصرف‌ترین اکسسوری‌های گوشی‌های موبایل و تبلت تبدیل شده‌اند.',
            cover='static/test/blog-1-500x400.jpg',
            price=6_000,
            discount=True,
            discount_price=3_000,
            active=False,
        )
        cls.product5 = Product.objects.create(
            title='کیبورد گرین GK703',
            description='ماوس های نسل جدید مجهز به بدنه مشبک به لطف وزن به مراتب کمتر و '
                        'تهویه کارآمد که تعریق کمتر دست را به دنبال دارد، به',
            cover='static/test/blog-1.jpg',
            price=5_000,
        )

    def send_request_update_view(self, action, product_pk=None, qty=None, status=200):
        request_data = {'action': action, 'productId': product_pk, 'quantity': f'{qty}'}
        response = self.client.post(reverse('cart:update_item'), json.dumps(request_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status)

    def test_update_item(self):
        # correct info
        self.client.login(username=self.user1.username, password='q1w2e3r4a')
        # add without quantity None
        self.send_request_update_view('add', self.product1.pk)
        self.order1 = Order.objects.last()
        self.order_item1 = OrderItem.objects.last()
        # test str order and order_item
        self.assertEqual(str(self.order1), str(self.order1.pk))
        self.assertEqual(str(self.order_item1), f'order number: {self.order1.pk}')
        # test info order and order_item
        self.assertEqual(self.order_item1.order, self.order1)
        self.assertEqual(self.order_item1.product, self.product1)
        self.assertEqual(self.order_item1.quantity, 1)
        self.assertEqual(self.order_item1.track_order, 0)
        # add with quantity
        self.send_request_update_view('add', self.product1.pk, 14)
        self.order_item1.refresh_from_db()
        self.assertEqual(self.order_item1.product, self.product1)
        self.assertEqual(self.order_item1.quantity, 15)
        self.assertEqual(self.order_item1.track_order, 0)
        # remove without quantity
        self.send_request_update_view('remove', self.product1.pk)
        self.order_item1.refresh_from_db()
        self.assertEqual(self.order_item1.product, self.product1)
        self.assertEqual(self.order_item1.quantity, 14)
        self.assertEqual(self.order_item1.track_order, 0)
        # remove with quantity
        # negative quantity
        self.send_request_update_view('remove', self.product1.pk, -7)
        # positive quantity
        self.send_request_update_view('remove', self.product1.pk, 2)
        self.order_item1.refresh_from_db()
        self.assertEqual(self.order_item1.product, self.product1)
        self.assertEqual(self.order_item1.quantity, 5)
        self.assertEqual(self.order_item1.track_order, 0)
        # delete with remove
        self.send_request_update_view('remove', self.product1.pk, -5)
        try:
            self.order_item1.refresh_from_db()
            self.fail('The order_item must not update because it must be deleted')
        except OrderItem.DoesNotExist:
            self.assertEqual(self.order1.items.all().count(), 0)
        # delete with delete_item
        # create a new order_item
        self.send_request_update_view('add', self.product2.pk)
        self.order_item2 = OrderItem.objects.last()
        self.assertEqual(self.order1.items.all().count(), 1)

        self.send_request_update_view('delete_item', self.product2.pk)
        try:
            self.order_item1.refresh_from_db()
            self.fail('The order_item must not update because it must be deleted')
        except OrderItem.DoesNotExist:
            self.assertEqual(self.order1.items.all().count(), 0)
        # clear cart with delete_cart
        # create a new order_items
        self.send_request_update_view('add', self.product2.pk)
        self.order_item2 = OrderItem.objects.last()
        self.send_request_update_view('add', self.product3.pk, 12)
        self.order_item3 = OrderItem.objects.last()
        self.send_request_update_view('add', self.product1.pk, 4)
        self.order_item2 = OrderItem.objects.last()
        self.assertEqual(self.order1.items.all().count(), 3)
        # send delete_cart
        self.send_request_update_view('delete_cart')
        self.assertEqual(self.order1.items.all().count(), 0)

        # incorrect info
        # inactive product
        self.send_request_update_view('add', self.product4.pk, status=404)
        self.assertEqual(self.order1.items.all().count(), 0)

        # send negative quantity for action add
        self.send_request_update_view('add', self.product3.pk, -2)
        self.assertEqual(self.order1.items.all().count(), 0)

        # send quantity for action remove with more than item.quantity
        # create an order item
        self.send_request_update_view('add', self.product3.pk, 6)
        self.send_request_update_view('remove', self.product3.pk, -14)
        self.assertEqual(self.order1.items.all().count(), 0)

    def test_cart_page_url_and_template(self):
        # with reverse
        response = self.client.get(reverse('cart:cart_page'))
        self.assertEqual(response.status_code, 200)
        # without reverse
        response = self.client.get(f'/cart/')
        self.assertEqual(response.status_code, 200)
        # template
        self.assertTemplateUsed(response, 'cart/cart.html')

    def test_order_item_in_cart_page(self):
        self.client.login(username=self.user2.username, password='q1w2e3r4a')
        self.send_request_update_view('add', self.product3.pk)


















