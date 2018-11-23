from urllib.parse import urlencode

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html

from coin_exchange.admin_views import custom_order_view
from coin_exchange.constants import ORDER_TYPE, ORDER_STATUS
from coin_exchange.models import Order, Review, Pool, TrackingAddress, TrackingTransaction
from common.constants import DIRECTION


class InlineLinkMixin:
    def create_button(self, obj, title, url_name):
        return format_html(
            '<a class="button" href="{}?{}">{}</a>',
            reverse(url_name, args=[obj.pk]),
            self.get_preserved_filters(self.request),
            title
        )


class DefaultFilterMixin:
    def get_default_filters(self, request):
        """Set default filters to the page.
            request (Request)
            Returns (dict):
                Default filter to encode.
        """
        raise NotImplementedError()

    def changelist_view(self, request, extra_context=None, *args, **kwargs):
        self.request = request

        ref = request.META.get('HTTP_REFERER', '')
        path = request.META.get('PATH_INFO', '')

        # If already have query parameters or if the page
        # was referred from it self (by drilldown or redirect)
        # don't apply default filter.
        if request.GET or ref.endswith(path):
            return super().changelist_view(
                request,
                extra_context=extra_context
            )
        query = urlencode(self.get_default_filters(request))
        return redirect('{}?{}'.format(path, query))


class BaseOrderAdmin(InlineLinkMixin, DefaultFilterMixin, admin.ModelAdmin):
    list_display = ['id', 'user', 'format_amount', 'currency', 'fiat_local_amount', 'fiat_local_currency',
                    'status', 'user_actions']
    list_filter = ['status', 'currency']


@admin.register(Order)
class OrderAdmin(BaseOrderAdmin):
    def get_default_filters(self, request):
        return {
            'status__exact': ORDER_STATUS.fiat_transferring,
        }

    def get_queryset(self, request):
        return self.model.objects.filter(direction=DIRECTION.buy, order_type=ORDER_TYPE.bank).order_by('-id')

    def has_delete_permission(self, request, obj=None):
        return False

    def user_actions(self, obj):
        return self.create_button(obj, 'View', 'admin:custom-order-view') + \
               format_html('&nbsp;') + \
               self.create_button(obj, 'Process', 'admin:custom-order-process')

    user_actions.short_description = 'Actions'
    user_actions.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('order-view/<int:pk>',
                 self.admin_site.admin_view(self.order_view),
                 name='custom-order-view'),
            path('order-process/<int:pk>',
                 self.admin_site.admin_view(self.order_process),
                 name='custom-order-process'),
        ]
        return custom_urls + urls

    def order_view(self, request, pk, *args, **kwargs):
        return custom_order_view(self, request, pk, 'View Bank Order', True)

    def order_process(self, request, pk, *args, **kwargs):
        return custom_order_view(self, request, pk, 'Process Bank Order', False)


class CODOrder(Order):
    class Meta:
        proxy = True


@admin.register(CODOrder)
class CODOrderAdmin(BaseOrderAdmin):
    def get_default_filters(self, request):
        return {
            'status__exact': ORDER_STATUS.pending,
        }

    def get_queryset(self, request):
        return self.model.objects.filter(direction=DIRECTION.buy, order_type=ORDER_TYPE.cod).order_by('-id')

    def has_delete_permission(self, request, obj=None):
        return False

    def user_actions(self, obj):
        return self.create_button(obj, 'View', 'admin:custom-order-view') + \
               format_html('&nbsp;') + \
               self.create_button(obj, 'Process', 'admin:custom-order-process')

    user_actions.short_description = 'Actions'
    user_actions.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('order-view/<int:pk>',
                 self.admin_site.admin_view(self.order_view),
                 name='custom-order-view'),
            path('order-process/<int:pk>',
                 self.admin_site.admin_view(self.order_process),
                 name='custom-order-process'),
        ]
        return custom_urls + urls

    def order_view(self, request, pk, *args, **kwargs):
        return custom_order_view(self, request, pk, 'View Bank Order', True)

    def order_process(self, request, pk, *args, **kwargs):
        return custom_order_view(self, request, pk, 'Process Bank Order', False)


class SellingOrder(Order):
    class Meta:
        proxy = True


@admin.register(SellingOrder)
class SellingOrderAdmin(BaseOrderAdmin):
    def get_default_filters(self, request):
        return {
            'status__exact': ORDER_STATUS.transferred,
        }

    def get_queryset(self, request):
        return self.model.objects.filter(direction=DIRECTION.sell).order_by('-id')

    def has_delete_permission(self, request, obj=None):
        return False

    def user_actions(self, obj):
        return self.create_button(obj, 'View', 'admin:custom-order-view') + \
               format_html('&nbsp;') + \
               self.create_button(obj, 'Process', 'admin:custom-order-process')

    user_actions.short_description = 'Actions'
    user_actions.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('order-view/<int:pk>',
                 self.admin_site.admin_view(self.order_view),
                 name='custom-order-view'),
            path('order-process/<int:pk>',
                 self.admin_site.admin_view(self.order_process),
                 name='custom-order-process'),
        ]
        return custom_urls + urls

    def order_view(self, request, pk, *args, **kwargs):
        return custom_order_view(self, request, pk, 'View Bank Order', True)

    def order_process(self, request, pk, *args, **kwargs):
        return custom_order_view(self, request, pk, 'Process Bank Order', False)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'country', 'direction', 'review']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ['direction', 'currency', 'limit', 'usage']

    def get_queryset(self, request):
        return self.model.objects.all().order_by('-id')

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TrackingAddress)
class TrackingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'currency', 'status', 'order']


@admin.register(TrackingTransaction)
class TrackingTransactionAdmin(admin.ModelAdmin):
    list_display = ['tx_hash', 'currency', 'status', 'order', 'direction']
