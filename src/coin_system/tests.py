from decimal import Decimal

from django.test import TestCase

from coin_system.business import get_config, get_fee
from coin_system.factories import ConfigFactory, FeeFactory
from coin_system.models import Config
from common.constants import VALUE_TYPE


class ConfigValueTypeTest(TestCase):
    def setUp(self):
        self.key = 'KEY'

    def test_get_int(self):
        ConfigFactory(key=self.key, value='10', value_type=VALUE_TYPE.int)
        config = Config.objects.get(pk=self.key)

        value = config.get_value()
        self.assertEqual(type(value), int)
        self.assertEqual(value, 10)

    def test_get_decimal(self):
        ConfigFactory(key=self.key, value='10.005', value_type=VALUE_TYPE.decimal)
        config = Config.objects.get(pk=self.key)

        value = config.get_value()
        self.assertEqual(type(value), Decimal)
        self.assertEqual(value, Decimal('10.005'))

    def test_get_string(self):
        text = 'Some string'
        ConfigFactory(key=self.key, value=text, value_type=VALUE_TYPE.string)
        config = Config.objects.get(pk=self.key)

        value = config.get_value()
        self.assertEqual(type(value), str)
        self.assertEqual(value, text)


class GetterTests(TestCase):
    def test_get_config(self):
        key = 'KEY'
        value = 'value'

        ConfigFactory(key=key, value=value, value_type=VALUE_TYPE.string)

        config1 = get_config(key)
        config1_value = config1.get_value()
        self.assertEqual(value, config1_value)

        config2 = get_config(key)
        config2_value = config2.get_value()
        self.assertEqual(value, config2_value)

    def test_get_fee(self):
        key = 'KEY'
        value = Decimal('10.5')

        FeeFactory(key=key, value=value)

        fee1 = get_fee(key)
        self.assertEqual(value, fee1.value)

        fee2 = get_fee(key)
        self.assertEqual(value, fee2.value)
