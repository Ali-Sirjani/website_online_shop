from django.contrib import admin

from .models import Order, OrderItem, ShippingAddress


class OrderItemTabular(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', )
    fields = ('product', 'quantity', 'track_order')
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ('customer', 'first_name', 'last_name', 'email', 'phone', 'completed', 'transaction',
              'get_cart_total_no_discount_pass', 'get_cart_total_discount_pass', 'get_cart_total_profit_pass',
              'get_cart_total_pass')
    readonly_fields = ('get_cart_total_no_discount_pass', 'get_cart_total_discount_pass', 'get_cart_total_profit_pass',
                       'get_cart_total_pass', 'transaction')
    inlines = (OrderItemTabular, )
    search_fields = ('transaction', )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass

    # readonly_fields = ('get_cart_total_no_discount_pass', 'get_cart_total_discount_pass',
    # 'get_cart_total_profit_pass',
    #                    'get_cart_total_pass', 'transaction')
    #
    # def get_fields(self, request, obj=None):
    #     fields = super().get_fields(request, obj)
    #
    #     if obj and obj.order_id and obj.order.completed:
    #         # try:
    #         #     order = Order.objects.get(pk=obj.order_id)
    #         #     if order.completed:
    #         #         # Modify the fields list to include the fields you want to display for completed orders
    #         #         fields = ['field1', 'field2', 'field3']
    #         # except Order.DoesNotExist:
    #         #     pass
    #         fields = ('item_title', )
    #     else:
    #         fields = ('product', 'order', 'quantity')
    #
    #     return fields


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    pass
