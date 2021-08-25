from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import BadData

from .constants import ACCESS_TOKEN_EXPIRES


def check_access_token(access_token_openid):
    """
    反序列化access_token_openid
    :param access_token_openid:openid密文
    :return:openid明文
    """
    # 初始化序列化对象
    s = Serializer(settings.SECRET_KEY, ACCESS_TOKEN_EXPIRES)

    # 反序列化openid密文
    try:
        data = s.loads(access_token_openid)
    except BadData:  # openid密文过期
        return None
    else:
        return data.get('openid')


def generate_access_token(openid):
    """
    初始化openid，过程是可逆的
    :param openid: openid明文
    :return: token（openid密文）
    """
    # 创建序列化对象
    # s = Serialzier('秘钥:越复杂越安全', '过期时间')
    s = Serializer(settings.SECRET_KEY, ACCESS_TOKEN_EXPIRES)

    # 准备序列化字典
    data = {'openid': openid}

    # 调用dumps方法进行序列化:类型是bytes
    token = s.dumps(data)

    # 返回序列化后的数据
    return token.decode()
