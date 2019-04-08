from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData


# TimedJSONWebSignatureSerializer: 可以生成带有有效期的token
def generate_save_user_token(open_id):
    """对open_id进行加密"""
    # 1. 创建加密的序列化器对象 secret_key
    serializer = TJWSSerializer(settings.SECRET_KEY, 600)
    # 2. 调用jumps(JSON字典)方法进行加密 加密后的数据默认是bytes类型
    data = {
        'openid': open_id
    }
    token = serializer.dumps(data)
    # 3. 把加密后的openid_id返回
    return token.decode()


def check_save_user_token(access_token):
    """
    将assess_token 还原为 openid
    :param access_token: 加密后的openid
    :return: openid
    """
    # 1. 创建序列化器对象, 指定秘钥和过期时间
    serializer = TJWSSerializer(settings.SECRET_KEY, 600)
    # 2. 解密
    try:
        data = serializer.loads(access_token)
    except BadData:
        return None
    # 3. 返回 openid
    return data.get('openid')
