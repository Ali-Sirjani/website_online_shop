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


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    pass
