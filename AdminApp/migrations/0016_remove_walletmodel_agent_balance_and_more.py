# Generated by Django 5.0.6 on 2024-07-17 10:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AdminApp', '0015_rename_total_amount_agentpurchasemodel_call_amount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='walletmodel',
            name='agent_balance',
        ),
        migrations.RemoveField(
            model_name='walletmodel',
            name='purchase_date',
        ),
        migrations.AddField(
            model_name='walletmodel',
            name='call_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='walletmodel',
            name='chat_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='walletmodel',
            name='messages_remaining',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='walletmodel',
            name='total_messages_received',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='walletmodel',
            name='total_minutes',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='UserPurchaseModel',
            fields=[
                ('userpurchase_id', models.AutoField(primary_key=True, serialize=False)),
                ('purchase_date', models.DateTimeField()),
                ('purchase_amount', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AdminApp.customermodel')),
            ],
        ),
        migrations.CreateModel(
            name='WithdrawalHistoryModel',
            fields=[
                ('agentpurchase_id', models.AutoField(primary_key=True, serialize=False)),
                ('withdrawal_amount', models.FloatField()),
                ('withdrawal_date', models.DateTimeField()),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AdminApp.customermodel')),
            ],
        ),
        migrations.DeleteModel(
            name='AgentPurchaseModel',
        ),
    ]