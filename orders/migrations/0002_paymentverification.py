from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentVerification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("payment_method", models.CharField(choices=[("card", "Karta"), ("cash", "Naqd"), ("click", "Click"), ("payme", "Payme")], default="cash", max_length=16)),
                ("card_type", models.CharField(blank=True, default="", max_length=32)),
                ("card_last4", models.CharField(blank=True, default="", max_length=4)),
                ("card_valid", models.BooleanField(default=False)),
                ("passport_series", models.CharField(blank=True, default="", max_length=2)),
                ("passport_number", models.CharField(blank=True, default="", max_length=7)),
                ("passport_pinfl", models.CharField(blank=True, default="", max_length=14)),
                ("passport_valid", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("order", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="payment_verification", to="orders.order")),
            ],
            options={
                "verbose_name": "To'lov tekshiruvi",
                "verbose_name_plural": "To'lov tekshiruvlari",
                "ordering": ["-created_at"],
            },
        ),
    ]
