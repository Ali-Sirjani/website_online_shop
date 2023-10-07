import datetime

from django.contrib import admin


from .models import Order, OrderItem, ShippingAddress
from .forms import OrderAdminForm, OrderItemAdminForm


class OrderItemTabular(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'track_order')
    extra = 0
    min_num = 1

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        if obj and obj.completed:
            readonly_fields.extend(['product', 'quantity', 'track_order'])

        return readonly_fields


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    fieldsets = (
        ('Contact Info', {'fields': ('customer', 'first_name', 'last_name', 'email', 'phone',)}),
        ('Order Info', {'fields': ('completed', 'transaction', 'get_cart_total_no_discount_past',
                                   'get_cart_total_discount_past', 'get_cart_total_profit_past',
                                   'get_cart_total_past',),
                        'classes': ('collapse',),
                        }),
    )
    list_display = ('id', 'customer', 'phone', 'completed', 'total')
    ordering = ('-id', )
    inlines = (OrderItemTabular,)
    list_filter = ('completed', )
    search_fields = ('transaction', 'id')
    autocomplete_fields = ('customer', )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['get_cart_total_no_discount_past', 'get_cart_total_discount_past',
                           'get_cart_total_profit_past', 'get_cart_total_past', 'transaction', ]

        if obj:
            readonly_fields.append('customer')

        return readonly_fields

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance  # Get the saved object

        if obj and form.cleaned_data.get('completed'):

            if not obj.transaction:
                transaction_id = datetime.datetime.now().timestamp()
                obj.transaction = transaction_id

            for item in obj.items.all():
                item.save_price()
                item.backup_product()
                if not item.track_order:
                    item.track_order = 20
                    item.save()

            obj.backup_total()
            obj.datetime_payed = datetime.datetime.now()
            obj.save()

    @admin.display(ordering='get_cart_total_past')
    def total(self, obj):
        if obj.completed:
            return f'{obj.get_cart_total_past:,}'

        return 0


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    form = OrderItemAdminForm
    fields = ('product', 'order', 'quantity', 'track_order', 'datetime_added', 'get_total_no_discount_past',
              'get_total_discount_past', 'get_total_profit_past', 'get_total_past',)
    list_display = ('order', 'product', 'quantity', 'datetime_added', 'is_order_completed')
    autocomplete_fields = ('product', 'order',)
    search_fields = ('order__id', 'order__transaction')
    ordering = ('-datetime_added',)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['datetime_added', 'get_total_no_discount_past', 'get_total_discount_past',
                           'get_total_profit_past', 'get_total_past', ]

        if obj:
            if obj.order.completed:
                readonly_fields.extend(['product', 'quantity'])

            readonly_fields.append('order')

        return readonly_fields

    @admin.display(ordering='order__completed', description='completed')
    def is_order_completed(self, obj):
        try:
            return obj.order.completed
        except AttributeError:
            return None


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    fields = ('customer', 'order', 'state', 'city', 'address', 'plate', 'datetime_added',)
    list_display = ('id', 'customer', 'order', 'datetime_added',)
    search_fields = ('customer__username', 'order__id', 'order__transaction')
    autocomplete_fields = ('customer', 'order')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['datetime_added']

        if obj:
            readonly_fields.extend(['customer', 'order', ])

        return readonly_fields
