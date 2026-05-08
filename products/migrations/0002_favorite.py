from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Favorite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="favorited_by", to="products.product")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="favorites", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Yoqtirilgan mahsulot",
                "verbose_name_plural": "Yoqtirilgan mahsulotlar",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(fields=("user", "product"), name="uniq_user_product_favorite"),
        ),
    ]
