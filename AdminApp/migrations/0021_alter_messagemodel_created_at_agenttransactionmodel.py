# Generated by Django 5.0.6 on 2024-07-23 09:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminApp', '0020_walletmodel_total_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagemodel',
            name='created_at',
            field=models.DateTimeField(),
        ),
        migrations.CreateModel(
            name='AgentTransactionModel',
            fields=[
                ('agent_transaction_id', models.AutoField(primary_key=True, serialize=False)),
                ('transaction_amount', models.FloatField()),
                ('transaction_date', models.DateTimeField()),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AdminApp.customermodel')),
            ],
        ),
    ]
