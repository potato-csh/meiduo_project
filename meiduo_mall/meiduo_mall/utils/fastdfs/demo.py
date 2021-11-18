from fdfs_client.client import Fdfs_client, get_tracker_conf

if __name__ == '__main__':
    tracker_path = get_tracker_conf(r'C:\Users\Potato\PycharmProjects\Working\meiduo_project\meiduo_mall\meiduo_mall\utils'
                         r'\fastdfs\client.conf')
    client = Fdfs_client(tracker_path)
    ret = client.upload_by_filename(r'C:\Users\Potato\Pictures\meiduo_logo.png')
    print(ret)
