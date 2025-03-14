# Generated by Django 5.0.3 on 2024-05-05 15:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smart_user_management', '0004_delete_blacklistedtoken'),
        ('token_blacklist', '0012_alter_outstandingtoken_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtendedBlacklistedToken',
            fields=[
                ('blacklistedtoken_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='token_blacklist.blacklistedtoken')),
                ('full_token', models.TextField()),
            ],
            bases=('token_blacklist.blacklistedtoken',),
        ),
    ]
