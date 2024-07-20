# Generated by Django 5.0.6 on 2024-07-18 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminApp', '0017_remove_customermodel_messages_remaining_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CoinsModel',
        ),
        migrations.AddField(
            model_name='customermodel',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userpurchasemodel',
            name='purchase_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='withdrawalhistorymodel',
            name='withdrawal_date',
            field=models.DateTimeField(),
        ),
    ]
