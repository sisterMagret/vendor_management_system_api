from decouple import config
from django.db.models import PositiveSmallIntegerField


class CustomEnum(object):
    class Enum(object):
        name = None
        value = None
        type = None

        def __init__(self, name, value, type):
            self.key = name
            self.name = name
            self.value = value
            self.type = type

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.name

        def __eq__(self, other):
            if other is None:
                return False
            if isinstance(other, CustomEnum.Enum):
                return self.value == other.value
            raise TypeError

    @classmethod
    def choices(c):
        attrs = [a for a in c.__dict__.keys() if a.isupper()]
        values = [
            (c.__dict__[v], CustomEnum.Enum(v, c.__dict__[v], c).__str__())
            for v in attrs
        ]
        return sorted(values, key=lambda x: x[0])

    @classmethod
    def default(cls):
        """
        Returns default value, which is the first one by default.
        Override this method if you need another default value.
        """
        return cls.choices()[0][0]

    @classmethod
    def field(cls, **kwargs):
        """
        A shortcut for
        Usage:
            class MyModelStatuses(CustomEnum):
                UNKNOWN = 0
            class MyModel(Model):
                status = MyModelStatuses.field(label='my status')
        """
        field = PositiveSmallIntegerField(
            choices=cls.choices(), default=cls.default(), **kwargs
        )
        field.enum = cls
        return field

    @classmethod
    def get(c, value):
        if type(value) is int:
            try:
                return [
                    CustomEnum.Enum(k, v, c)
                    for k, v in c.__dict__.items()
                    if k.isupper() and v == value
                ][0]
            except Exception:
                return None
        else:
            try:
                key = value.upper()
                return CustomEnum.Enum(key, c.__dict__[key], c)
            except Exception:
                return None

    @classmethod
    def key(c, key):
        try:
            return [
                value
                for name, value in c.__dict__.items()
                if name == key.upper()
            ][0]
        except Exception:
            return None

    @classmethod
    def name(c, key):
        try:
            return [
                name for name, value in c.__dict__.items() if value == key
            ][0]
        except Exception:
            return None

    @classmethod
    def get_counter(c):
        counter = {}
        for key, value in c.__dict__.items():
            if key.isupper():
                counter[value] = 0
        return counter

    @classmethod
    def items(c):
        attrs = [a for a in c.__dict__.keys() if a.isupper()]
        values = [(v, c.__dict__[v]) for v in attrs]
        return sorted(values, key=lambda x: x[1])

    @classmethod
    def to_list(c):
        attrs = [a for a, _ in c.choices()]
        return attrs

    @classmethod
    def is_valid_transition(c, from_status, to_status):
        return (
            from_status == to_status
            or from_status in c.transition_origins(to_status)
        )

    @classmethod
    def transition_origins(c, to_status):
        return to_status

    @classmethod
    def get_name(c, key):
        choices_name = dict(c.choices())
        return choices_name.get(key)


class UserGroup(CustomEnum):
    BUYER = "buyer"
    VENDOR = "vendor"

    @classmethod
    def choices(cls):
        return ((cls.BUYER, "BUYER"), (cls.VENDOR, "VENDOR"))


class POStatusEnum(CustomEnum):
    COMPLETED = "completed"
    PENDING = "pending"
    CANCELLED = "cancelled"

    @classmethod
    def choices(cls):
        return (
            (cls.COMPLETED, "Completed"), 
            (cls.PENDING, "Pending"),
            (cls.CANCELLED, "Cancelled"),
            )
