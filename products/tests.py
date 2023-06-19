from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse

from .models import Product, Category
from trans_persian.templatetags.trans_fa import num_fa


class TestProduct(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = get_user_model().objects.create_user(username='joker', email='joker@gmail.com',
                                                         password='q1w2e3r4a')
        cls.user2 = get_user_model().objects.create_user(username='batman', email='batman@gmail.com',
                                                         password='q1w2e3r4a')
        cls.user3 = get_user_model().objects.create_user(username='angry4', email='angry4@gmail.com',
                                                         password='q1w2e3r4a')
        cls.user4 = get_user_model().objects.create_user(username='dota2', email='dota2@gmail.com',
                                                         password='q1w2e3r4a')

        cls.category1 = Category.objects.create(name='Electronic')
        cls.category2 = Category.objects.create(name='Computer')
        cls.category3 = Category.objects.create(name='mouse and keyboard')
        cls.category4 = Category.objects.create(name='Home')

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

        # add categories
        cls.product1.category.add(cls.category1, cls.category2, cls.category3)
        cls.product2.category.add(cls.category4)

    def add_favorite(self):
        # user 1
        self.client.login(username=self.user1.username, password='q1w2e3r4a')
        self.client.post(reverse('products:favorite', args=[self.product1.pk]))
        self.client.post(reverse('products:favorite', args=[self.product3.pk]))
        # user 2
        self.client.login(username=self.user2.username, password='q1w2e3r4a')
        self.client.post(reverse('products:favorite', args=[self.product1.pk]))
        # user 3
        self.client.login(username=self.user3.username, password='q1w2e3r4a')
        self.client.post(reverse('products:favorite', args=[self.product1.pk]))

    def test_categories_info(self):
        self.assertEqual(self.category1.name, 'Electronic')
        self.assertEqual(self.category1.slug, slugify('Electronic', allow_unicode=True))

    def test_products_info(self):
        self.assertEqual(self.product2.title, 'ماشین لباسشویی بوش مدل WAX32E90ME ظرفیت 10 کیلوگرم')
        self.assertEqual(self.product2.description, 'ماشین لباسشویی بوش WAX32E90 از سری HomeProfessional است که '
                                                    'از جمله سری های فوق العاده شرکت بوش می باشد.')
        self.assertEqual(self.product2.cover, 'static/test/blog5.jpg')
        self.assertEqual(self.product2.price, 20_000)
        self.assertEqual(self.product2.discount, True)
        self.assertEqual(self.product2.discount_price, 15_000)
        self.assertEqual(self.product2.slug, slugify(self.product2.title, allow_unicode=True))
        self.assertEqual(self.product2.title, str(self.product2))
        # active test product4
        self.assertEqual(self.product4.active, False)

    def test_products_list_url_and_template(self):
        # with reverse
        response = self.client.get(reverse('products:products_list'))
        self.assertEqual(response.status_code, 200)
        # without reverse
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)
        # template
        self.assertTemplateUsed(response, 'products/products_list.html')

    def test_products_in_products_list(self):
        response = self.client.get(reverse('products:products_list'))
        # active products
        self.assertContains(response, self.product3.title)
        self.assertContains(response, self.product3.cover)
        self.assertContains(response, num_fa(self.product3.price))
        # not active discount price product3
        self.assertNotContains(response, self.product3.discount_price)
        # discount price product2
        self.assertContains(response, num_fa(self.product2.discount_price))
        # test link
        self.assertContains(response,
                            f"<a href=\"{reverse('products:product_detail', args=[self.product1.slug])}\">"
                            f"{self.product1.title}</a>",
                            html=True)
        # test add cart
        self.assertContains(response,
                            f'<a href="" data-product="{self.product3.pk}" data-action="add" class="btn btn-small'
                            f' btn-bg-sand btn-color-dark px-3 update-cart">Add to cart</a>',
                            html=True)

        # inactive product
        self.assertNotContains(response, self.product4.title)
        self.assertNotContains(response, self.product4.cover)
        self.assertNotContains(response, num_fa(self.product4.price))
        self.assertNotContains(response, num_fa(self.product4.discount_price))

    def test_products_add_in_categories_and_favorites(self):
        self.add_favorite()

        def method_test_categories_and_favorites(operation, field, num, dict_obj):
            dict_obj_value = list(dict_obj.values())
            self.assertEqual(field.count(), num)
            objects = field.all()
            if operation == 'c':
                for i in range(len(dict_obj_value)):
                    if dict_obj_value[i] not in objects:
                        self.fail(msg=f'there is no category with name {dict_obj_value[i].name}!')
            elif operation == 'f':
                for i in range(len(dict_obj_value)):
                    if dict_obj_value[i] not in objects:
                        self.fail(msg=f'there is no user with name {dict_obj_value[i].username} in favorite')
            else:
                self.fail(msg='Enter the wrong operation You should enter c or f')

        # categories
        method_test_categories_and_favorites('c', self.product1.category, 3,
                                             {'category1': self.category1, 'category2': self.category2,
                                              'category3': self.category3})
        # favorites
        method_test_categories_and_favorites('f', self.product1.favorite, 3,
                                             {'user1': self.user1, 'user2': self.user2, 'user3': self.user3})

    def test_category_page_url_and_template(self):
        # with reverse
        response = self.client.get(reverse('products:category_page', args=[self.category4.slug]))
        self.assertEqual(response.status_code, 200)
        # without reverse
        response = self.client.get(f'/products/category/{self.category1.slug}/')
        self.assertEqual(response.status_code, 200)
        # template
        self.assertTemplateUsed(response, 'products/category.html')

    def test_products_in_category_page(self):
        response = self.client.get(reverse('products:category_page', args=[self.category4.slug]))
        #  product with category4
        self.assertContains(response, self.product2.title)
        self.assertContains(response, self.product2.cover)
        self.assertContains(response, num_fa(self.product2.price))
        self.assertContains(response, num_fa(self.product2.discount_price))
        # test link
        self.assertContains(response,
                            f"<a href=\"{reverse('products:product_detail', args=[self.product2.slug])}\">"
                            f"{self.product2.title}</a>",
                            html=True)
        self.assertContains(response,
                            f'<a href="" data-product="{self.product2.pk}" data-action="add" class="btn btn-small'
                            f' btn-bg-sand btn-color-dark px-3 update-cart">Add to cart</a>',
                            html=True)

        #  product without category4
        self.assertNotContains(response, self.product1.title)
        self.assertNotContains(response, self.product1.cover)
        self.assertNotContains(response, num_fa(self.product1.price))
        self.assertNotContains(response, num_fa(self.product1.discount_price))

    def test_icon_like(self):
        self.add_favorite()

        # products_list
        response = self.client.get(reverse('products:products_list'))
        self.assertContains(response, 'static/img/hearts.png')
        # category
        response = self.client.get(reverse('products:category_page', args=[self.category3.slug]))
        self.assertContains(response, 'static/img/hearts.png')

        # products_list
        self.client.login(username=self.user4.username, password='q1w2e3r4a')
        response = self.client.get(reverse('products:products_list'))
        self.assertNotContains(response, 'static/img/hearts.png')
        # category
        response = self.client.get(reverse('products:category_page', args=[self.category3.slug]))
        self.assertNotContains(response, 'static/img/hearts.png')

    def test_search_page_url_and_template(self):
        # q is none
        # with reverse
        response = self.client.get(reverse('products:search_page'))
        self.assertEqual(response.status_code, 200)
        # without reverse
        response = self.client.get(f'/products/search/')
        self.assertEqual(response.status_code, 200)
        # template
        self.assertTemplateUsed(response, 'products/search_q_none.html')

        # q isn't none
        response = self.client.get(reverse('products:search_page'), {'q': 'test'})
        self.assertEqual(response.status_code, 200)
        # without reverse
        response = self.client.get(f'/products/search/', {'q': 'test'})
        self.assertEqual(response.status_code, 200)
        # template
        self.assertTemplateUsed(response, 'products/search.html')

    def test_products_in_search_page(self):
        q = 'test'
        response = self.client.get(f'/products/search/', {'q': q})
        products_list = [self.product1, self.product2, self.product3, self.product4]
        for product in products_list:
            self.assertNotContains(response, product)

        # text when search nothing find
        self.assertContains(response, f'There is no product with title {q}')

        response = self.client.get(f'/products/search/', {'q': 'GM606-RGB'})
        for product in products_list:
            if product == self.product3:
                self.assertContains(response, product)
                self.assertContains(response,
                                    f"<a href=\"{reverse('products:product_detail', args=[product.slug])}\">"
                                    f"{product.title}</a>",
                                    html=True)
                self.assertContains(response,
                                    f'<a href="" data-product="{product.pk}" data-action="add" class="btn btn-small'
                                    f' btn-bg-sand btn-color-dark px-3 update-cart">Add to cart</a>',
                                    html=True)

            else:
                self.assertNotContains(response, product)

        response = self.client.get(f'/products/search/', {'q': 'USB'})
        for product in products_list:
            self.assertNotContains(response, product)

        response = self.client.get(f'/products/search/', {'q': 'gk'})
        for product in products_list:
            if product == self.product5:
                self.assertContains(response, product)

        response = self.client.get(f'/products/search/', {'q': 'گرین'})
        for product in products_list:
            if product == self.product3 or product == self.product5:
                self.assertContains(response, product)

            else:
                self.assertNotContains(response, product)

    def test_product_detail_url_and_template(self):
        # with reverse
        response = self.client.get(reverse('products:product_detail', args=[self.product1.slug]))
        self.assertEqual(response.status_code, 200)
        # without reverse
        response = self.client.get(f'/products/{self.product3.slug}/')
        self.assertEqual(response.status_code, 200)
        # template
        self.assertTemplateUsed(response, 'products/product_detail.html')
        # not active product
        response = self.client.get(f'/products/{self.product4.slug}/')
        self.assertEqual(response.status_code, 404)

    def test_product_detail_page_and_comments(self):
        response = self.client.get(reverse('products:product_detail', args=[self.product2.slug]))
        self.assertContains(response, self.product2.title)
        self.assertContains(response, self.product2.cover)
        self.assertContains(response, num_fa(self.product2.price))
        self.assertContains(response, num_fa(self.product2.discount_price))

        self.assertContains(response,
                            f'<button href="{ reverse("cart:update_item")}" type="button" class="btn btn-small '
                            f'btn-bg-red btn-color-white btn-hover-2  update-cart" data-product="{ self.product2.pk }" '
                            f'onclick="addToCart()">Add to cart</button>',
                            html=True)

        response = self.client.post(reverse('products:product_detail', args=[self.product2.slug]),
                                    {'text': 'I am trying to test this page', 'star': 2})
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.user2.username, password='q1w2e3r4a')
        # incorrect info
        response = self.client.post(reverse('products:product_detail', args=[self.product2.slug]),
                                    {'text': 'Now I am log in so I can comment in this page', 'star': 1.2})
        self.assertContains(response, 'Your comment have problem please try again!')

        # correct info
        # with user2
        response = self.client.post(reverse('products:product_detail', args=[self.product2.slug]),
                                    {'text': 'Now I am log in so I can comment in this page', 'star': 5})

        # with user4
        self.client.login(username=self.user4.username, password='q1w2e3r4a')
        response = self.client.post(reverse('products:product_detail', args=[self.product2.slug]),
                                    {'text': 'this was very expensive and with low quality', 'star': 2})
        self.assertRedirects(response, reverse('products:product_detail', args=[self.product2.slug]))

        self.assertEqual(self.product2.comments.all().count(), 2)

        comment1 = self.product2.comments.all()[0]
        comment2 = self.product2.comments.all()[1]

        # test info comment
        self.assertEqual(comment1.product, self.product2)
        self.assertEqual(comment1.author, self.user2)
        self.assertEqual(comment1.text, 'Now I am log in so I can comment in this page')
        self.assertEqual(comment1.star, '5')
        self.assertEqual(comment1.confirmation, False)

        comment1.confirmation = True
        comment1.save()

        # log out because we want to test author.username if we be login with user4 test will fail
        self.client.logout()
        response = self.client.get(reverse('products:product_detail', args=[self.product2.slug]))
        # true confirmation
        self.assertContains(response, comment1.text)
        self.assertContains(response, comment1.author.username)
        # false confirmation
        self.assertNotContains(response, comment2.text)
        self.assertNotContains(response, comment2.author.username)
