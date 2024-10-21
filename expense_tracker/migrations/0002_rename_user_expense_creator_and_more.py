# Generated by Django 5.1.2 on 2024-10-21 11:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("expense_tracker", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name="expense",
            old_name="user",
            new_name="creator",
        ),
        migrations.RenameField(
            model_name="expense",
            old_name="amount",
            new_name="total_amount",
        ),
        migrations.RemoveField(
            model_name="expense",
            name="participants",
        ),
        migrations.RemoveField(
            model_name="expense",
            name="split_method",
        ),
        migrations.AlterField(
            model_name="expense",
            name="description",
            field=models.TextField(),
        ),
        migrations.CreateModel(
            name="ExpenseSplit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount_owed", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "expense",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="splits",
                        to="expense_tracker.expense",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
