# Generated by Django 4.2 on 2024-05-10 22:47

import django.core.validators
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Item",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "price",
                    models.FloatField(
                        default=0.0,
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.DecimalValidator(
                                decimal_places=1, max_digits=16
                            ),
                        ],
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PurchaseOrder",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "po_number",
                    models.CharField(editable=False, max_length=16, unique=True),
                ),
                ("order_date", models.DateTimeField(auto_now=True)),
                ("delivery_date", models.DateTimeField()),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("completed", "Completed"),
                            ("pending", "Pending"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "quality_rating",
                    models.FloatField(
                        default=0.0,
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(5.0),
                            django.core.validators.DecimalValidator(
                                decimal_places=1, max_digits=2
                            ),
                        ],
                    ),
                ),
                ("issue_date", models.DateTimeField(blank=True, null=True)),
                (
                    "acknowledgment_date",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Purchase order",
                "verbose_name_plural": "Purchase orders",
                "db_table": "purchase_order",
                "ordering": ("-order_date",),
            },
        ),
    ]
