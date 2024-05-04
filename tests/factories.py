import factory
from django.contrib.auth import get_user_model
from faker import Faker

from apps.users.models import BuyerSettings

faker = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        # skip_postgeneration_save=True

    first_name = faker.first_name()
    last_name = faker.last_name()
    email = faker.email()
    mobile = faker.phone_number()
    # password = factory.PostGenerationMethodCall('set_password', '"$rootpa$$"')
    password = "$rootpa$$"
    username = "john_doe"
    address = faker.address()
    state = "NY"
    country = "USA"
    city = "New York"
    zip_code = "10001"


class BuyerSettingsFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = BuyerSettings

    business_name = "Sister Magret's PUB"
    user = factory.SubFactory(UserFactory)
