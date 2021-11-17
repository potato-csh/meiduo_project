from fdfs_client.client import Fdfs_client, get_tracker_conf

if __name__ == '__main__':
    client = Fdfs_client(r'C:\Users\Potato\PycharmProjects\Working\meiduo_project\meiduo_mall\meiduo_mall\utils'
                         r'\fastdfs\client.conf')
    ret = client.upload_by_filename(r'C:\Users\Potato\Pictures\meiduo_logo.png')
    print(ret)
