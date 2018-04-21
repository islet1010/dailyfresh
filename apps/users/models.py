from django.contrib.auth.models import AbstractUser
from django.db import models
from tinymce.models import HTMLField

from utils.models import BaseModel


class User(BaseModel, AbstractUser):
    """用户模型类"""

    class Meta(object):
        # 指定表名 app01_user
        db_table = 'df_user'


class Address(BaseModel):
    """地址"""

    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, null=True, verbose_name="邮政编码")
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    user = models.ForeignKey(User, verbose_name="所属用户")

    class Meta:
        db_table = "df_address"


class TestModel(BaseModel):
    """测试用"""

    name = models.CharField(max_length=20)

    # 商品详情，使用第三方的: HTMLField
    goods_detail = HTMLField(default='', verbose_name='商品详情')





