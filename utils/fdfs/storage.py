from django.core.files.storage import FileSystemStorage
from fdfs_client.client import Fdfs_client


class FdfsStorage(FileSystemStorage):
    """自定义存储类"""

    # def save(self, name, content, max_length=None):
    #     return super().save(name, content, max_length)
    def _save(self, name, content):
        """
        当管理员在管理后台上传文件时，会使用此类保存上传的文件
        :param name: 文件名
        :param content: ImageFieldFile类型的对象，从此对象获取上传的文件内容
        :return:
        """
        # path = super()._save(name, content)
        # print(name, path, type(content))

        # todo: 保存文件到FastDfs服务器上
        client = Fdfs_client('utils/fdfs/client.conf')
        try:
            # 上传文件到Fdfs服务器
            datas = content.read()  # 要上传的文件内容
            # 字典
            result = client.upload_by_buffer(datas)

            # {
            #     "Remote file_id": "group1/M00/00/00/wKjzh0_xaR63RExnAAAaDqbNk5E1398.py",
            #     "Status": "Upload successed.",
            #     "Storage IP": "192.168.243.133",
            # }
            status = result.get('Status')
            if status == 'Upload successed.':
                # 上传图片成功
                path = result.get('Remote file_id')
            else:
                raise Exception('上传图片失败：%s' % status)
        except Exception as e:
            # 上传文件出错
            print(e)
            raise e

        # 上传的文件的路径，Django会自动保存此路径到数据表中
        print(path)
        return path

    def url(self, name):
        # 拼接nginx服务器的ip和端口，再返回给浏览器显示
        path = super().url(name)
        return 'http://127.0.0.1:8888/' + path












