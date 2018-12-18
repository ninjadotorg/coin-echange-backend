import simplejson

from django import forms
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import urlunquote

from coin_exchange.business.fund import FundManagement
from coin_exchange.business.order import OrderManagement
from coin_exchange.constants import (
    ORDER_STATUS,
    ORDER_TYPE,
    PAYMENT_STATUS,
    ORDER_USER_PAYMENT_TYPE,
    REFERRAL_STATUS,
    CRYPTO_FUND_TYPE)
from coin_exchange.models import Order, PromotionOrder, CryptoFund
from coin_exchange.widgets import (
    ImageWidget,
    CryptoTransactionWidget,
    CryptoAmountWidget,
    FiatAmountWidget,
    TextWidget,
    JSONWidget,
    CryptoAddressWidget,
    PaymentTransactionWidget)
from common.constants import DIRECTION, CURRENCY


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
    context['url_filters'] = url_filters

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
        user_info = order.user_info
        try:
            user_info = simplejson.loads(user_info)
            user_info = simplejson.dumps(user_info, ensure_ascii=False, indent=2, sort_keys=True)
        except Exception:
            pass

        form = OrderCODForm(initial={
            'id': order.id,
            'user': order.user,
            'amount': order.amount,
            'currency': order.currency,
            'fiat_local_amount': order.fiat_local_amount,
            'fiat_local_currency': order.fiat_local_currency,
            'address': order.address,
            'user_info': user_info,
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
                    reverse("admin:coin_exchange_order_changelist") + '?{}'.format(url_filters))

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

        return HttpResponseRedirect(reverse("admin:coin_exchange_order_changelist") + '?{}'.format(url_filters))

    context = admin_view.admin_site.each_context(request)
    context['opts'] = admin_view.model._meta
    context['form'] = form
    context['obj'] = order
    context['title'] = title
    context['read_only'] = read_only
    context['url_filters'] = url_filters

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
    order_user_payment_type = forms.CharField(label='Payment Type', disabled=True, widget=TextWidget)
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

        user_info = order.user_info
        try:
            user_info = simplejson.loads(user_info)
            user_info = simplejson.dumps(user_info, ensure_ascii=False, indent=2, sort_keys=True)
        except Exception:
            pass

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
            'order_user_payment_type': ORDER_USER_PAYMENT_TYPE[order.order_user_payment_type]
            if order.order_user_payment_type else '-',
            'user_info': user_info,
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
    context['url_filters'] = url_filters

    return TemplateResponse(
        request,
        'admin/order/selling_order.html',
        context,
    )


@transaction.atomic
def custom_selling_cod_order_view(admin_view, request, pk, title, read_only):
    changelist_filters = request.GET.get('_changelist_filters')
    url_filters = urlunquote(changelist_filters) if changelist_filters else ''

    order = Order.objects.get(id=pk)
    if request.method != 'POST':
        payment = None
        payment_details = []
        if order.selling_order_payments:
            payment = order.selling_order_payments.first()
            if payment:
                payment_details = payment.selling_payment_details

        user_info = order.user_info
        try:
            user_info = simplejson.loads(user_info)
            user_info = simplejson.dumps(user_info, ensure_ascii=False, indent=2, sort_keys=True)
        except Exception:
            pass

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
            'order_user_payment_type': ORDER_USER_PAYMENT_TYPE[order.order_user_payment_type]
            if order.order_user_payment_type else '-',
            'user_info': user_info,
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

        return HttpResponseRedirect(
            reverse("admin:coin_exchange_sellingorder_changelist") + '?{}'.format(url_filters))

    context = admin_view.admin_site.each_context(request)
    context['opts'] = admin_view.model._meta
    context['form'] = form
    context['obj'] = order
    context['title'] = title
    context['read_only'] = read_only
    context['url_filters'] = url_filters

    return TemplateResponse(
        request,
        'admin/order/selling_cod_order.html',
        context,
    )


class PromotionOrderForm(forms.Form):
    id = forms.CharField(label='Order #', disabled=True, widget=TextWidget)
    user = forms.CharField(disabled=True, widget=TextWidget)
    amount = forms.DecimalField(label='Fiat Amount', max_digits=18, decimal_places=2,
                                disabled=True, widget=FiatAmountWidget)
    user_info = forms.CharField(label='User Info', disabled=True, widget=JSONWidget)

    def __init__(self, *args, **kwargs):
        super(PromotionOrderForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.currency = self.initial['currency']


@transaction.atomic
def custom_promotion_order_view(admin_view, request, pk, title, read_only):
    changelist_filters = request.GET.get('_changelist_filters')
    url_filters = urlunquote(changelist_filters) if changelist_filters else ''

    order = PromotionOrder.objects.get(id=pk)
    if request.method != 'POST':
        user_info = order.user.payment_info
        try:
            user_info = simplejson.loads(user_info)
            user_info = simplejson.dumps(user_info, ensure_ascii=False, indent=2, sort_keys=True)
        except Exception:
            pass

        form = PromotionOrderForm(initial={
            'id': order.id,
            'user': order.user,
            'amount': order.amount,
            'currency': order.currency,
            'user_info': user_info,
            'instance': order,
        })
        if not read_only:
            if order.status not in [REFERRAL_STATUS.pending, REFERRAL_STATUS.processing]:
                messages.warning(request, 'Order is in invalid status to process')
                return HttpResponseRedirect(
                    reverse("admin:coin_exchange_promotionorder_changelist") + '?{}'.format(url_filters))

            # Change to processing status
            if order.status == REFERRAL_STATUS.pending:
                order.status = REFERRAL_STATUS.processing
                order.save(update_fields=['status', 'updated_at'])
    else:
        action = request.POST['action'].lower()
        if action == 'approve':
            order.status = REFERRAL_STATUS.paid
            order.save(update_fields=['status', 'updated_at'])
            messages.success(request, 'Order is approved successful.')
        elif action == 'reject':
            order.status = REFERRAL_STATUS.rejected
            order.save(update_fields=['status', 'updated_at'])
            messages.success(request, 'Order is rejected successful.')

        return HttpResponseRedirect(
            reverse("admin:coin_exchange_promotionorder_changelist") + '?{}'.format(url_filters))

    context = admin_view.admin_site.each_context(request)
    context['opts'] = admin_view.model._meta
    context['form'] = form
    context['obj'] = order
    context['title'] = title
    context['read_only'] = read_only
    context['url_filters'] = url_filters

    return TemplateResponse(
        request,
        'admin/order/promotion_order.html',
        context,
    )


def custom_out_fund_view(admin_view, request, pk, title):
    return custom_fund_view(admin_view, request, pk, title, 'transfer_out_fund')


def custom_storage_fund_view(admin_view, request, pk, title):
    return custom_fund_view(admin_view, request, pk, title, 'transfer_storage_fund')


def custom_convert_from_fund_view(admin_view, request, pk, title):
    return custom_fund_view(admin_view, request, pk, title, 'convert_from_storage_fund')


def custom_convert_to_fund_view(admin_view, request, pk, title):
    return custom_fund_view(admin_view, request, pk, title, 'convert_to_storage_fund')


class FundForm(forms.Form):
    available_amount = forms.DecimalField(max_digits=18, decimal_places=6, disabled=True, widget=CryptoAmountWidget)
    to_currency = forms.ChoiceField(choices=CURRENCY, widget=forms.Select, required=False, disabled=True)
    to_amount = forms.DecimalField(max_digits=18, decimal_places=6)

    def __init__(self, *args, **kwargs):
        super(FundForm, self).__init__(*args, **kwargs)
        self.fields['available_amount'].widget.currency = self.initial['currency']
        if self.initial['fund_type'] == CRYPTO_FUND_TYPE.storage_fund and self.initial['convert'] and \
                self.initial['currency'] == CURRENCY.USDT:
            self.fields['to_currency'].disabled = False


@transaction.atomic
def custom_fund_view(admin_view, request, pk, title, action):
    changelist_filters = request.GET.get('_changelist_filters')
    url_filters = urlunquote(changelist_filters) if changelist_filters else ''

    fund = CryptoFund.objects.get(id=pk)
    if request.method != 'POST':
        form = FundForm(initial={
            'available_amount': '{:.6f}'.format(fund.amount),
            'currency': fund.currency,
            'to_amount': '',
            'to_currency': fund.currency,
            'fund_type': fund.fund_type,
            'convert': 'convert' in action
        })
    else:
        form = FundForm(request.POST, initial={
            'available_amount': '{:.6f}'.format(fund.amount),
            'currency': fund.currency,
            'fund_type': fund.fund_type,
            'convert': 'convert' in action
        })

        is_success = True
        if form.is_valid():
            amount = form.cleaned_data['to_amount']
            currency = form.cleaned_data['to_currency']
            if not currency:
                currency = fund.currency

            if action == 'transfer_out_fund':
                if fund.fund_type == CRYPTO_FUND_TYPE.in_fund:
                    FundManagement.transfer_in_fund_to_out_fund(currency, amount)
                else:
                    FundManagement.transfer_storage_to_out_fund(currency, amount)
                messages.success(request, 'Request sent successfully.')
            elif action == 'transfer_storage_fund':
                FundManagement.transfer_in_fund_to_storage(currency, amount)
                messages.success(request, 'Request sent successfully.')
            elif action == 'convert_from_storage_fund':
                FundManagement.convert_storage_to_vault(currency, amount)
                messages.success(request, 'Request sent successfully.')
            elif action == 'convert_to_storage_fund':
                if currency != CURRENCY.USDT:
                    FundManagement.convert_vault_to_storage(currency, amount)
                    messages.success(request, 'Request sent successfully.')
                else:
                    messages.error(request, 'Please choose other currency.')
                    is_success = False

            if is_success:
                return HttpResponseRedirect(
                    reverse("admin:coin_exchange_cryptofund_changelist") + '?{}'.format(url_filters))

    context = admin_view.admin_site.each_context(request)
    context['opts'] = admin_view.model._meta
    context['form'] = form
    context['obj'] = fund
    context['title'] = title
    context['url_filters'] = url_filters

    return TemplateResponse(
        request,
        'admin/fund/fund.html',
        context,
    )
