from django.test import TestCase
from django.shortcuts import reverse
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

import datetime

from products.models import Product, Category, TimeLike
from cart.models import Order, OrderItem
from trans_persian.templatetags.trans_fa import num_fa


class TestSetUserName(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user(email='aliqw@gmail.com', username='aliqw',
                                                         password='q1w2e3r4a')
        cls.user2 = get_user_model().objects.create_user(email='ali12qw@gmail.com', username='ali12qw',
                                                         password='q1w2e3r4a')
        cls.user3 = get_user_model().objects.create_user(email='ali3qw@gmail.com', username='ali3qw',
                                                         password='q1w2e3r4a')

    def test_set_username_url_and_template(self):
        # without login
        response = self.client.get(reverse('accounts:set_username'))
        # test url
        self.assertRedirects(response, reverse('account_login') + '?next=' + reverse('accounts:set_username'),
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        # with login
        self.client.login(email=self.user1.email, password='q1w2e3r4a')
        response = self.client.get(reverse('accounts:set_username'))
        self.assertEqual(response.status_code, 200)
        # test template use
        self.assertTemplateUsed(response, 'accounts/set_username.html')

    def test_set_username_exist(self):
        self.client.login(email=self.user1.email, password='q1w2e3r4a')
        self.assertEqual(self.user1.set_username.first_time, True)

        response = self.client.post(reverse('accounts:set_username'), {
            # username of user2
            'username': 'ali12qw',
        })
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, 'aliqw')
        # self.assertEqual(flag_exist, True)

    def test_set_username_change(self):
        # user1
        self.client.login(email=self.user1.email, password='q1w2e3r4a')
        self.assertEqual(self.user1.set_username.first_time, True)
        response = self.client.post(reverse('accounts:set_username'), {
            'username': 'joker',
        })
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, 'joker')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user1.set_username.first_time, False)
        self.client.logout()

        # check first_time's user2 that don't change
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.set_username.first_time, True)

    def test_set_username_do_not_change(self):
        self.client.login(email='aliqw@gmail.com', password='q1w2e3r4a')
        self.assertEqual(self.user1.set_username.first_time, True)
        self.user1.refresh_from_db()
        response = self.client.post(reverse('accounts:set_username'), {
            'username': 'bat',
        })
        self.assertNotEqual(self.user1.username, 'bat')
        self.assertEqual(self.user1.set_username.first_time, False)


class TestProfile(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user(email='angryjoker@gmail.com', username='angry',
                                                         password='q1w2e3r4a')
        cls.user2 = get_user_model().objects.create_user(email='batman@gmail.com', username='bat',
                                                         password='q1w2e3r4a')
        cls.user3 = get_user_model().objects.create_user(email='rez1234@gmail.com', username='rez',
                                                         password='q1w2e3r4a')

        cls.category1 = Category.objects.create(
            name='mountain',
        )

        cls.product1 = Product.objects.create(
            title='کیسه خواب فوروارد مدل CAMPING PRO - 3012',
            description='ابعاد۱۲x۸۰x۲۱۰ سانتی‌متر وزن۱۵۰۰ گرم',
            price=400,
            cover='static/test/blog3.jpg'
        )

        cls.product2 = Product.objects.create(
            title='کپسول گاز بلک دیر مدل BGB-450 وزن 450 گرم',
            description='در مواقعی که برای گردش و تفریح به طبیعت گردی یا کوهنوردی و موارد مشابه می روید، برای '
                        'درست کردن یا گرم',
            price=1400,
            discount=True,
            discount_price=700,
            cover='static/test/blog5.jpg'
        )

    def test_profile_url_and_template(self):
        # without login
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, reverse('account_login') + '?next=' + reverse('accounts:profile'),
                             status_code=302, target_status_code=200, fetch_redirect_response=True
                             )
        # with login
        self.client.login(email=self.user1.email, password='q1w2e3r4a')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        # test template use
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_favorites_list_in_profile(self):
        self.client.login(username=self.user1.username, password='q1w2e3r4a')
        # add favorite
        self.client.post(reverse('products:favorite', args=[self.product1.pk]))
        self.client.post(reverse('products:favorite', args=[self.product2.pk]))

        response = self.client.get(reverse('accounts:profile'))
        # product1 in favorites list
        self.assertContains(response, self.product1.title)
        self.assertContains(response, self.product1.cover)
        # product2 in favorites list
        self.assertContains(response, self.product2.title)
        self.assertContains(response, self.product2.cover)

        self.client.post(reverse('products:favorite', args=[self.product1.pk]))
        response = self.client.get(reverse('accounts:profile'))

        self.assertNotContains(response, self.product1.title)
        self.assertNotContains(response, self.product1.cover)

        self.client.login(username=self.user2.username, password='q1w2e3r4a')
        self.client.post(reverse('products:favorite', args=[self.product2.pk]))

        response = self.client.get(reverse('accounts:profile'))
        # product2 in favorites list
        self.assertContains(response, self.product2.title)
        self.assertContains(response, self.product2.cover)
        self.assertContains(response,
                            TimeLike.objects.get(user=self.user2, product=self.product2).datetime_like.strftime(
                                '%Y-%m-%d %H:%M:%S'))
        # product1 not in favorites list
        self.assertNotContains(response, self.product1.title)
        self.assertNotContains(response, self.product1.cover)

    def test_orders_in_profile(self):
        self.product3 = Product.objects.create(
            title='کیس کامپیوتر گرین مدل Surena z5',
            description='هر آنچه از یک کیس گیمینگ جذاب، مدرن و باکیفیت انتظار دارید ',
            price=1_381_000,
            discount=True,
            discount_price=1_300_000,
            cover='static/test/blog6.jpg'
        )
        order1 = Order.objects.create(
            customer=self.user1,
            completed=True,
            get_cart_total_past=20_000_000,
            get_cart_items_past=12,
        )
        order2 = Order.objects.create(
            customer=self.user1,
            completed=True,
            get_cart_total_past=100_000,
            get_cart_items_past=8,
        )
        order3 = Order.objects.create(
            customer=self.user1,
            completed=False,
            get_cart_total_past=185_000,
            get_cart_items_past=76,
        )

        # order item for order1
        OrderItem.objects.create(
            product=self.product2,
            order=order1,
            quantity=2,
            track_order=20,
        )
        OrderItem.objects.create(
            product=self.product1,
            order=order1,
            quantity=10,
            track_order=100,
        )
        # order item for order2
        OrderItem.objects.create(
            product=self.product3,
            order=order2,
            quantity=8,
            track_order=40,
        )
        # order item for order3
        OrderItem.objects.create(
            product=self.product3,
            order=order3,
            quantity=76,
            track_order=0,
        )

        self.client.login(username=self.user1.username, password='q1w2e3r4a')
        response = self.client.get(reverse('accounts:profile'))

        # test track_order
        self.assertEqual(order1.avg_track_items, 'Out for delivery')
        self.assertEqual(order2.avg_track_items, 'Processing')

        # completed order
        # order1
        self.assertContains(response, f'${num_fa(order1.get_cart_total_past)} for {num_fa(order1.get_cart_items_past)} item')
        self.assertContains(response, 'Out for delivery')
        self.assertContains(response, order1.format_time_ordered())
        # order2
        self.assertContains(response, f'${num_fa(order2.get_cart_total_past)} for {num_fa(order2.get_cart_items)} item')
        self.assertContains(response, 'Processing')
        self.assertContains(response, order2.format_time_ordered())
        # test link order detail
        self.assertContains(response, f'<a href="{reverse("cart:order_detail", args=[order2.pk])}" class="btn btn-small'
                                      f' btn-bg-red btn-color-white btn-hover-2">Visit</a>',
                            html=True)

        # not completed order
        self.assertNotContains(response,
                               f'${num_fa(order3.get_cart_total_past)} for {num_fa(order3.get_cart_items)} item')
        # don't be same with time order1 and order2
        order3.datetime_ordered += datetime.timedelta(days=1)
        self.assertNotContains(response, order3.format_time_ordered())
        self.assertNotContains(response, f'<a href="{reverse("cart:order_detail", args=[order3.pk])}" '
                                         f'class="btn btn-small btn-bg-red btn-color-white btn-hover-2">Visit</a>',
                               html=True)

    def test_profile_detail(self):
        self.client.login(username=self.user2.username, password='q1w2e3r4a')
        response = self.client.get(reverse('accounts:profile'))

        self.assertContains(response, f'You didn\'t set username. Click on<a class="forgot-pass" '
                                      f'href="{reverse("accounts:set_username")}"><strong>set username</strong></a>to'
                                      f' redirect. But pay attention You can set your username for one time!',
                            html=True,
                            )

        # change username
        response = self.client.post(reverse('accounts:set_username'), {
            'username': 'joker',
        })

        response = self.client.get(reverse('accounts:profile'))
        self.assertNotContains(response, f'You didn\'t set username. Click on<a class="forgot-pass" '
                                         f'href="{reverse("accounts:set_username")}"><strong>set username</strong></a>to'
                                         f' redirect. But pay attention You can set your username for one time!',
                               html=True,
                               )

        response = self.client.post(reverse('accounts:profile'), {
            'phone': '+98930012322333333',
        })

        self.assertNotEqual(self.user2.profile.phone, 930012322333333)

        response = self.client.post(reverse('accounts:profile'), {
            'first_name': 'ali',
            'last_name': 'sirjani',
            'location': 'I\'m some where in this world',
            # because we use widget for phone field the name change to phone_1
            'phone_1': '+989312844761',
        })

        self.user2.profile.refresh_from_db()

        self.assertEqual(self.user2.profile.first_name, 'ali')
        self.assertEqual(self.user2.profile.last_name, 'sirjani')
        self.assertEqual(self.user2.profile.location, 'I\'m some where in this world')
        self.assertEqual(self.user2.profile.phone, '+989312844761')


