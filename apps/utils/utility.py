from django.apps import apps

from apps.utils.enums import ConfigurationTypeEnum


def compute_order_item_total(product, qty):
    configuration = apps.get_model("core", "Configuration")
    rate = 0
    price = product.get_price()
    config_obj = configuration.objects.filter(
        name=ConfigurationTypeEnum.PRODUCT_CHARGE_RATE
    ).first()
    if config_obj:
        rate = config_obj.value
    product_charge_price = float(price) + float(rate)
    sum_total = float(product_charge_price * qty)
    return sum_total
