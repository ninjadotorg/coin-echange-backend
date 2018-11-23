from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import urlunquote

from coin_exchange.widgets import ImageWidget, CryptoTransactionWidget, CryptoAmountWidget, FiatAmountWidget, TextWidget


class OrderBankForm(forms.Form):
    id = forms.CharField(label='Order #', disabled=True, widget=TextWidget)
    user = forms.CharField(disabled=True, widget=TextWidget)
    amount = forms.DecimalField(max_digits=18, decimal_places=6, disabled=True, widget=CryptoAmountWidget)
    fiat_local_amount = forms.DecimalField(label='Fiat Amount', max_digits=18, decimal_places=2,
                                           disabled=True, widget=FiatAmountWidget)
    ref_code = forms.CharField(label='Ref Code', disabled=True, widget=TextWidget)
    receipt_url = forms.CharField(label='Receipt', disabled=True, widget=ImageWidget)
    address = forms.CharField(label='Transfer To', disabled=True, widget=TextWidget)
    tx_hash = forms.CharField(label='Tx Hash', disabled=True, widget=CryptoTransactionWidget)

    def __init__(self, *args, **kwargs):
        super(OrderBankForm, self).__init__(*args, **kwargs)
        self.fields['tx_hash'].widget.currency = self.initial['currency']
        self.fields['amount'].widget.currency = self.initial['currency']
        self.fields['fiat_local_amount'].widget.currency = self.initial['fiat_local_currency']


def custom_order_view(admin_view, request, pk, title, read_only):
    changelist_filters = request.GET.get('_changelist_filters')
    url_filters = urlunquote(changelist_filters) if changelist_filters else ''

    order = admin_view.get_object(request, pk)
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
    else:
        action = request.POST['action'].lower()
        if action == 'approve':
            messages.success(request, 'Order is approved successful')
        elif action == 'reject':
            messages.success(request, 'Order is rejected successful')

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
