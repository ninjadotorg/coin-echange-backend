from urllib.parse import urlencode

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html

from coin_exchange.admin_views import custom_order_view, custom_order_cod_view, custom_selling_order_view, \
    custom_selling_cod_order_view, custom_promotion_order_view
from coin_exchange.constants import ORDER_TYPE, ORDER_STATUS, REFERRAL_STATUS
from coin_exchange.models import Order, Review, Pool, TrackingAddress, TrackingTransaction, ReferralOrder, \
    PromotionOrder, PromotionRule
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


class BaseOrderAdmin(InlineLinkMixin, admin.ModelAdmin):
    list_display = ['id', 'user', 'ref_code', 'format_amount', 'currency', 'fiat_local_amount', 'fiat_local_currency',
                    'status', 'user_actions']
    list_filter = ['status', 'currency', 'order_type']
    search_fields = ['user__user__email', 'user__name', 'ref_code']
    date_hierarchy = 'created_at'

    def changelist_view(self, request, extra_context=None, *args, **kwargs):
        self.request = request
        return super(BaseOrderAdmin, self).changelist_view(request, extra_context, *args, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Order)
class OrderAdmin(BaseOrderAdmin):
    def get_default_filters(self, request):
        return {
            'status__exact': ORDER_STATUS.fiat_transferring,
        }

    def get_queryset(self, request):
        return self.model.objects.filter(direction=DIRECTION.buy).order_by('-id')

    def user_actions(self, obj):
        if obj.order_type == ORDER_TYPE.bank:
            process_button_html = format_html('')
            if obj.status in [ORDER_STATUS.fiat_transferring, ORDER_STATUS.processing]:
                process_button_html = self.create_button(obj, 'Process', 'admin:custom-order-process')
            return self.create_button(obj, 'View', 'admin:custom-order-view') + \
                format_html('&nbsp;') + process_button_html
        else:
            process_button_html = format_html('')
            if obj.status in [ORDER_STATUS.pending, ORDER_STATUS.processing]:
                process_button_html = self.create_button(obj, 'Process', 'admin:custom-order-cod-process')

            return self.create_button(obj, 'View', 'admin:custom-order-cod-view') + \
                format_html('&nbsp;') + process_button_html

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
            path('order-cod-view/<int:pk>',
                 self.admin_site.admin_view(self.order_cod_view),
                 name='custom-order-cod-view'),
            path('order-cod-process/<int:pk>',
                 self.admin_site.admin_view(self.order_cod_process),
                 name='custom-order-cod-process'),
        ]
        return custom_urls + urls

    def order_view(self, request, pk, *args, **kwargs):
        return custom_order_view(self, request, pk, 'View Bank Order', True)

    def order_process(self, request, pk, *args, **kwargs):
        return custom_order_view(self, request, pk, 'Process Bank Order', False)

    def order_cod_view(self, request, pk, *args, **kwargs):
        return custom_order_cod_view(self, request, pk, 'View COD Order', True)

    def order_cod_process(self, request, pk, *args, **kwargs):
        return custom_order_cod_view(self, request, pk, 'Process COD Order', False)


class SellingOrder(Order):
    class Meta:
        proxy = True
        verbose_name = 'Exch Selling Order'
        verbose_name_plural = 'Exch Selling Orders'


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
        if obj.order_type == ORDER_TYPE.bank:
            process_button_html = format_html('')
            if obj.status in [ORDER_STATUS.transferred, ORDER_STATUS.processing]:
                process_button_html = self.create_button(obj, 'Process', 'admin:custom-selling-order-process')

            return self.create_button(obj, 'View', 'admin:custom-selling-order-view') + \
                format_html('&nbsp;') + process_button_html
        else:
            process_button_html = format_html('')
            if obj.status in [ORDER_STATUS.transferred, ORDER_STATUS.processing]:
                process_button_html = self.create_button(obj, 'Process', 'admin:custom-selling-cod-order-process')

            return self.create_button(obj, 'View', 'admin:custom-selling-cod-order-view') + \
                format_html('&nbsp;') + process_button_html

    user_actions.short_description = 'Actions'
    user_actions.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('selling-order-view/<int:pk>',
                 self.admin_site.admin_view(self.order_view),
                 name='custom-selling-order-view'),
            path('selling-order-process/<int:pk>',
                 self.admin_site.admin_view(self.order_process),
                 name='custom-selling-order-process'),
            path('selling-cod-order-view/<int:pk>',
                 self.admin_site.admin_view(self.order_cod_view),
                 name='custom-selling-cod-order-view'),
            path('selling-cod-order-process/<int:pk>',
                 self.admin_site.admin_view(self.order_cod_process),
                 name='custom-selling-cod-order-process'),
        ]
        return custom_urls + urls

    def order_view(self, request, pk, *args, **kwargs):
        return custom_selling_order_view(self, request, pk, 'View Selling Order', True)

    def order_process(self, request, pk, *args, **kwargs):
        return custom_selling_order_view(self, request, pk, 'Process Selling Order', False)

    def order_cod_view(self, request, pk, *args, **kwargs):
        return custom_selling_cod_order_view(self, request, pk, 'View Selling COD Order', True)

    def order_cod_process(self, request, pk, *args, **kwargs):
        return custom_selling_cod_order_view(self, request, pk, 'Process Selling COD Order', False)


@admin.register(PromotionRule)
class PromotionRuleAdmin(admin.ModelAdmin):
    list_display = ['country', 'currency', 'first_referral_amount',
                    'first_referral_referrer_bonus', 'first_referral_referee_bonus',
                    'referrer_percentage',
                    'active']


@admin.register(ReferralOrder)
class ReferralOrderAdmin(admin.ModelAdmin):
    list_display = ['order', 'format_amount', 'currency', 'status', 'referrer']
    list_filter = ['status', 'referrer']


@admin.register(PromotionOrder)
class PromotionOrderAdmin(InlineLinkMixin, admin.ModelAdmin):
    list_display = ['order', 'amount', 'currency', 'status', 'referrer', 'user_actions']
    list_filter = ['status', 'referrer']

    def changelist_view(self, request, extra_context=None, *args, **kwargs):
        self.request = request
        return super(PromotionOrderAdmin, self).changelist_view(request, extra_context, *args, **kwargs)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def user_actions(self, obj):
        process_button_html = format_html('')
        if obj.status in [REFERRAL_STATUS.pending, REFERRAL_STATUS.processing]:
            process_button_html = self.create_button(obj, 'Process', 'admin:custom-promotion-order-process')

        return self.create_button(obj, 'View', 'admin:custom-promotion-order-view') + \
            format_html('&nbsp;') + process_button_html

    user_actions.short_description = 'Actions'
    user_actions.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('promotion-order-view/<int:pk>',
                 self.admin_site.admin_view(self.order_view),
                 name='custom-promotion-order-view'),
            path('promotion-order-process/<int:pk>',
                 self.admin_site.admin_view(self.order_process),
                 name='custom-promotion-order-process'),
        ]
        return custom_urls + urls

    def order_view(self, request, pk, *args, **kwargs):
        return custom_promotion_order_view(self, request, pk, 'View Promotion Order', True)

    def order_process(self, request, pk, *args, **kwargs):
        return custom_promotion_order_view(self, request, pk, 'Process Promotion Order', False)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'country', 'direction', 'review']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ['direction', 'currency', 'limit', 'usage']

    def get_queryset(self, request):
        return self.model.objects.all().order_by('-id')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(TrackingAddress)
class TrackingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'currency', 'status', 'order']


@admin.register(TrackingTransaction)
class TrackingTransactionAdmin(admin.ModelAdmin):
    list_display = ['tx_hash', 'currency', 'status', 'order', 'direction']
