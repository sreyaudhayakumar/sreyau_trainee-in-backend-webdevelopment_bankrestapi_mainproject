# Generated by Django 5.0.4 on 2024-04-24 05:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.IntegerField(choices=[(1, '1 - Savings Account'), (2, '2 - Current Account'), (3, '3 - Fixed Deposit Account'), (4, '4 - Recurring Deposit Account')])),
                ('balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('guardian_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('pin_code', models.CharField(max_length=10)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('occupation', models.CharField(max_length=100)),
                ('photo', models.ImageField(blank=True, upload_to='user_photos/')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
