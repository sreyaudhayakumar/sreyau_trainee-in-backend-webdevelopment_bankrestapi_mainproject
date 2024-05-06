# Generated by Django 5.0.4 on 2024-04-25 11:43

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankapp', '0003_account_account_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('destination_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_transactions', to='bankapp.account')),
                ('source_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_transactions', to='bankapp.account')),
            ],
        ),
    ]