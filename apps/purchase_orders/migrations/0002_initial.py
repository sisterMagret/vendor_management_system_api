# Generated by Django 4.2 on 2024-05-04 22:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("purchase_orders", "0001_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaseorder",
            name="buyer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s",
                to="users.buyersettings",
            ),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="vendor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s",
                to="users.vendorprofile",
            ),
        ),
    ]
