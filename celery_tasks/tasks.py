# 在celery服务器所在的项目中，
# 需要手动添加如下代码，初始化django环境
# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# django.setup()

from time import sleep

from celery.app.base import Celery
from django.core.mail import send_mail
from django.template import loader

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods
from dailyfresh import settings

# 创建celery客户端
# 参数1：自定义名称
# 参数２：中间人
app = Celery('dailyfresh', broker='redis://127.0.0.1:6379/1')


@app.task
def send_active_mail(username, email, token):
    """发送激活邮件"""
    subject = '天天生鲜激活邮件'         # 标题，必须指定
    message = ''                       # 正文
    from_email = settings.EMAIL_FROM   # 发件人
    recipient_list = [email]           # 收件人
    # 正文 （带有html样式）
    html_message = ('<h3>尊敬的%s：感谢注册天天生鲜</h3>'
                    '请点击以下链接激活您的帐号:<br/>'
                    '<a href="http://127.0.0.1:8000/users/active/%s">'
                    'http://127.0.0.1:8000/users/active/%s</a>'
                    ) % (username, token, token)

    send_mail(subject, message, from_email, recipient_list,
              html_message=html_message)
    pass


@app.task
def generate_static_index_page():
    """生成静态首页"""
    sleep(2)
    # 查询首页商品数据：商品类别，轮播图， 促销活动
    categories = GoodsCategory.objects.all()
    slide_skus = IndexSlideGoods.objects.all().order_by('index')
    promotions = IndexPromotion.objects.all().order_by('index')[0:2]

    for c in categories:
        # 查询当前类型所有的文字商品和图片商品
        text_skus = IndexCategoryGoods.objects.filter(
            display_type=0, category=c)
        image_skus = IndexCategoryGoods.objects.filter(
            display_type=1, category=c)[0:4]
        # 动态给对象新增实例属性
        c.text_skus = text_skus
        c.image_skus = image_skus

    # 获取用户添加到购物车商品的总数量
    cart_count = 0

    context = {
        'categories': categories,
        'slide_skus': slide_skus,
        'promotions': promotions,
        'cart_count': cart_count,
    }

    # 渲染生成静态的首页:index.html
    template = loader.get_template('index.html')
    html_str = template.render(context)
    # 生成首页
    path = '/home/python/Desktop/static/index.html'
    with open(path, 'w') as file:
        file.write(html_str)




















