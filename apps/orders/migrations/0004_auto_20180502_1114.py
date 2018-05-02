# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20180502_0752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='trade_no',
            field=models.CharField(max_length=100, blank=True, default='', null=True, verbose_name='支付编号'),
        ),
    ]
