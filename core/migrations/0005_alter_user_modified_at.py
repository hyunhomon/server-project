# Generated by Django 5.1.4 on 2024-12-10 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_user_groups_alter_user_user_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='modified_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
