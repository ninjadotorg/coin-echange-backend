from decimal import Decimal

from django.forms.widgets import Input, Widget

from common.constants import CURRENCY


class TextWidget(Input):
    template_name = 'widgets/text.html'


class CryptoAmountWidget(TextWidget):
    def get_context(self, name, value, attrs):
        context = super(CryptoAmountWidget, self).get_context(name, value, attrs)
        widget = context['widget']
        widget['raw_value'] = widget['value']
        widget['value'] = '{:.6f} {}'.format(Decimal(widget['raw_value']), self.currency)

        return context


class FiatAmountWidget(TextWidget):
    def get_context(self, name, value, attrs):
        context = super(FiatAmountWidget, self).get_context(name, value, attrs)
        widget = context['widget']
        widget['raw_value'] = widget['value']
        widget['value'] = '{:.2f} {}'.format(Decimal(widget['raw_value']), self.currency)

        return context


class ImageWidget(Input):
    template_name = 'widgets/image.html'


class CryptoTransactionWidget(Widget):
    template_name = 'widgets/link.html'

    def get_context(self, name, value, attrs):
        context = super(CryptoTransactionWidget, self).get_context(name, value, attrs)
        widget = context['widget']
        widget['raw_value'] = widget['value']
        if widget['raw_value'] and widget['raw_value'] != 'None':
            if self.currency == CURRENCY.ETH:
                widget['value'] = 'https://etherscan.io/tx/{}'.format(widget['value'])
            elif self.currency == CURRENCY.BTC:
                widget['value'] = 'https://www.blockchain.com/btc/tx/{}'.format(widget['value'])
            else:
                widget['value'] = '#'
        else:
            widget['raw_value'] = '(not yet)'
            widget['value'] = '#'

        return context
