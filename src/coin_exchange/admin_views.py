from django import forms
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import urlunquote

from coin_exchange.business.order import OrderManagement
from coin_exchange.constants import ORDER_STATUS, ORDER_TYPE, PAYMENT_STATUS
from coin_exchange.models import Order
from coin_exchange.widgets import ImageWidget, CryptoTransactionWidget, CryptoAmountWidget, FiatAmountWidget, \
    TextWidget, JSONWidget, CryptoAddressWidget, PaymentTransactionWidget
from common.constants import DIRECTION


class OrderBankForm(forms.Form):
    id = forms.CharField(label='Order #', disabled=True, widget=TextWidget)
    user = forms.CharField(disabled=True, widget=TextWidget)
    amount = forms.DecimalField(max_digits=18, decimal_places=6, disabled=True, widget=CryptoAmountWidget)
    fiat_local_amount = forms.DecimalField(label='Fiat Amount', max_digits=18, decimal_places=2,
                                           disabled=True, widget=FiatAmountWidget)
    ref_code = forms.CharField(label='Ref Code', disabled=True, widget=TextWidget)
    receipt_url = forms.CharField(label='Receipt', disabled=True, widget=ImageWidget)
    address = forms.CharField(label='Transfer To', disabled=True, widget=CryptoAddressWidget)
    tx_hash = forms.CharField(label='Tx Hash', disabled=True, widget=CryptoTransactionWidget)

    def __init__(self, *args, **kwargs):
        super(OrderBankForm, self).__init__(*args, **kwargs)

        self.fields['tx_hash'].widget.currency = self.initial['currency']
        self.fields['address'].widget.currency = self.initial['currency']

        self.fields['amount'].widget.currency = self.initial['currency']
        self.fields['fiat_local_amount'].widget.currency = self.initial['fiat_local_currency']


@transaction.atomic
def custom_order_view(admin_view, request, pk, title, read_only):
    changelist_filters = request.GET.get('_changelist_filters')
    url_filters = urlunquote(changelist_filters) if changelist_filters else ''

    order = Order.objects.get(id=pk)
    if request.method != 'POST':
        form = OrderBankForm(initial={
            'id': order.id,
            'user': order.user,
            'amount': order.amount,
            'currency': order.currency,
            'fiat_local_amount': order.fiat_local_amount,
            'fiat_local_currency': order.fiat_local_currency,
            'address': order.address,
            'ref_code': order.ref_code,
            'receipt_url': order.receipt_url,
            'tx_hash': order.tx_hash,
            'instance': order,
        })
        if not read_only:
            if order.status not in [ORDER_STATUS.fiat_transferring, ORDER_STATUS.processing] and \
                    order.direction == DIRECTION.buy and \
                    order.order_type == ORDER_TYPE.bank:
                messages.warning(request, 'Order is in invalid status to process')
                return HttpResponseRedirect(reverse("admin:coin_exchange_order_changelist") + '?{}'.format(url_filters))

            # Change to processing status
            if order.status == ORDER_STATUS.fiat_transferring:
                order.status = ORDER_STATUS.processing
                order.save(update_fields=['status', 'updated_at'])
    else:
        action = request.POST['action'].lower()
        if action == 'approve':
            OrderManagement.complete_order(order)
            messages.success(request, 'Order is approved successful. Sending crypto to destination...')
        elif action == 'reject':
            OrderManagement.reject_order(order)
            messages.success(request, 'Order is rejected successful.')

        return HttpResponseRedirect(reverse("admin:coin_exchange_order_changelist") + '?{}'.format(url_filters))

    context = admin_view.admin_site.each_context(request)
    context['opts'] = admin_view.model._meta
    context['form'] = form
    context['obj'] = order
    context['title'] = title
    context['read_only'] = read_only
    return TemplateResponse(
        request,
        'admin/order/order_bank.html',
        context,
    )


class OrderCODForm(forms.Form):
    id = forms.CharField(label='Order #', disabled=True, widget=TextWidget)
    user = forms.CharField(disabled=True, widget=TextWidget)
    amount = forms.DecimalField(max_digits=18, decimal_places=6, disabled=True, widget=CryptoAmountWidget)
    fiat_local_amount = forms.DecimalField(label='Fiat Amount', max_digits=18, decimal_places=2,
                                           disabled=True, widget=FiatAmountWidget)
    ref_code = forms.CharField(label='Ref Code', disabled=True, widget=TextWidget)
    user_info = forms.CharField(label='User Info', disabled=True, widget=JSONWidget)
    address = forms.CharField(label='Transfer To', disabled=True, widget=CryptoAddressWidget)
    tx_hash = forms.CharField(label='Tx Hash', disabled=True, widget=CryptoTransactionWidget)

    def __init__(self, *args, **kwargs):
        super(OrderCODForm, self).__init__(*args, **kwargs)

        self.fields['tx_hash'].widget.currency = self.initial['currency']
        self.fields['address'].widget.currency = self.initial['currency']

        self.fields['amount'].widget.currency = self.initial['currency']
        self.fields['fiat_local_amount'].widget.currency = self.initial['fiat_local_currency']


@transaction.atomic
def custom_order_cod_view(admin_view, request, pk, title, read_only):
    changelist_filters = request.GET.get('_changelist_filters')
    url_filters = urlunquote(changelist_filters) if changelist_filters else ''

    order = Order.objects.get(id=pk)
    if request.method != 'POST':
        form = OrderCODForm(initial={
            'id': order.id,
            'user': order.user,
            'amount': order.amount,
            'currency': order.currency,
            'fiat_local_amount': order.fiat_local_amount,
            'fiat_local_currency': order.fiat_local_currency,
            'address': order.address,
            'user_info': order.user_info,
            'ref_code': order.ref_code,
            'tx_hash': order.tx_hash,
            'instance': order,
        })
        if not read_only:
            if order.status not in [ORDER_STATUS.pending, ORDER_STATUS.processing] and \
                    order.direction == DIRECTION.buy and \
                    order.order_type == ORDER_TYPE.cod:
                messages.warning(request, 'Order is in invalid status to process')
                return HttpResponseRedirect(
                    reverse("admin:coin_exchange_codorder_changelist") + '?{}'.format(url_filters))

            # Change to processing status
            if order.status == ORDER_STATUS.pending:
                order.status = ORDER_STATUS.processing
                order.save(update_fields=['status', 'updated_at'])
    else:
        action = request.POST['action'].lower()
        if action == 'approve':
            OrderManagement.complete_order(order)
            messages.success(request, 'Order is approved successful. Sending crypto to destination...')
        elif action == 'reject':
            OrderManagement.reject_order(order)
            messages.success(request, 'Order is rejected successful.')

        return HttpResponseRedirect(reverse("admin:coin_exchange_codorder_changelist") + '?{}'.format(url_filters))

    context = admin_view.admin_site.each_context(request)
    context['opts'] = admin_view.model._meta
    context['form'] = form
    context['obj'] = order
    context['title'] = title
    context['read_only'] = read_only
    return TemplateResponse(
        request,
        'admin/order/order_cod.html',
        context,
    )


class SellingOrderForm(forms.Form):
    id = forms.CharField(label='Order #', disabled=True, widget=TextWidget)
    user = forms.CharField(disabled=True, widget=TextWidget)
    amount = forms.DecimalField(max_digits=18, decimal_places=6, disabled=True, widget=CryptoAmountWidget)
    fiat_local_amount = forms.DecimalField(label='Fiat Amount', max_digits=18, decimal_places=2,
                                           disabled=True, widget=FiatAmountWidget)
    ref_code = forms.CharField(label='Ref Code', disabled=True, widget=TextWidget)
    user_info = forms.CharField(label='User Info', disabled=True, widget=JSONWidget)
    address = forms.CharField(label='Receiving address', disabled=True, widget=CryptoAddressWidget)
    payment = forms.CharField(label='Total received', disabled=True, widget=TextWidget)
    tx_hash = forms.CharField(label='Tx Hashes', disabled=True, widget=PaymentTransactionWidget)

    def __init__(self, *args, **kwargs):
        super(SellingOrderForm, self).__init__(*args, **kwargs)

        self.fields['tx_hash'].widget.currency = self.initial['currency']
        self.fields['tx_hash'].widget.payment_details = self.initial['payment_details']

        self.fields['address'].widget.currency = self.initial['currency']

        self.fields['amount'].widget.currency = self.initial['currency']
        self.fields['fiat_local_amount'].widget.currency = self.initial['fiat_local_currency']
        self.fields['tx_hash'].widget.currency = self.initial['currency']


@transaction.atomic
def custom_selling_order_view(admin_view, request, pk, title, read_only):
    changelist_filters = request.GET.get('_changelist_filters')
    url_filters = urlunquote(changelist_filters) if changelist_filters else ''

    order = Order.objects.get(id=pk)
    if request.method != 'POST':
        payment = None
        payment_details = []
        if order.selling_order_payments:
            payment = order.selling_order_payments.first()
            payment_details = payment.selling_payment_details

        form = SellingOrderForm(initial={
            'id': order.id,
            'user': order.user,
            'amount': order.amount,
            'currency': order.currency,
            'payment': '{:.6f} ({})'.format(payment.amount, PAYMENT_STATUS[payment.status]),
            'payment_details': payment_details,
            'fiat_local_amount': order.fiat_local_amount,
            'fiat_local_currency': order.fiat_local_currency,
            'address': order.address,
            'user_info': order.user_info,
            'ref_code': order.ref_code,
            'tx_hash': order.tx_hash,
            'instance': order,
        })
        if not read_only:
            if order.status not in [ORDER_STATUS.transferred, ORDER_STATUS.processing] and \
                    order.direction == DIRECTION.buy and \
                    order.order_type == ORDER_TYPE.cod:
                messages.warning(request, 'Order is in invalid status to process')
                return HttpResponseRedirect(
                    reverse("admin:coin_exchange_sellingorder_changelist") + '?{}'.format(url_filters))

            # Change to processing status
            if order.status == ORDER_STATUS.transferred:
                order.status = ORDER_STATUS.processing
                order.save(update_fields=['status', 'updated_at'])
    else:
        action = request.POST['action'].lower()
        if action == 'approve':
            OrderManagement.complete_order(order)
            messages.success(request, 'Order is approved successful.')
        elif action == 'reject':
            OrderManagement.reject_order(order)
            messages.success(request, 'Order is rejected successful.')

        return HttpResponseRedirect(reverse("admin:coin_exchange_sellingorder_changelist") + '?{}'.format(url_filters))

    context = admin_view.admin_site.each_context(request)
    context['opts'] = admin_view.model._meta
    context['form'] = form
    context['obj'] = order
    context['title'] = title
    context['read_only'] = read_only
    return TemplateResponse(
        request,
        'admin/order/selling_order.html',
        context,
    )
