import decimal

TIMEZONE = 'Asia/Shanghai'
DEFAULT_LANGUAGES = 'en_US'
SUPPORTED_LANGUAGES = ['en_US', 'zh_Hans_CN', 'zh_Hant_HK']

SESSION_LIFETIME = 86400
SECRET_KEY = '\x07\x8c\xf0\x97E\xa4|\xa6\x00\x1d\x10\xbd]\x15\xb3\xedE\x93\x98\xde\xbcUw9\x8e\x04\x87] \xce'

SQLALCHEMY_DATABASE_URI = 'mysql://ifwallet:hC8b6dooA#Rh3c=P@rm-j6cg474s521349qke.mysql.rds.aliyuncs.com/game_dice'
SQLALCHEMY_TRACK_MODIFICATIONS = True

CACHE_TYPE = "redis"
REDIS_URL = "redis://:@127.0.0.1:6379/1"
ALERT_REDIS_URL = "redis://:@192.168.0.164:6379/1"
CACHE_REDIS_URL = "redis://:@127.0.0.1:6379/2"
CELERY_BROKER_URL = 'redis://:@192.168.0.164:6379/3'
CELERY_RESULT_BACKEND = 'redis://:@192.168.0.164:6379/4'

PAGE_CAPACITY = 20

CLIENT_AUTH = {
        'bitcoin_cash': {
            'host': '192.168.0.165',
            'port': 8332,
            'protocol': 'http',
            'auth': ('ifwallet', 'WZhcAhg6bYHwT9a')
            },
        'bitcoin_sv': {
            'host': '192.168.0.170',
            'port': 8332,
            'protocol': 'http',
            'auth': ('ifwallet', '4h&gxaAR,YHnwQtMp')
            }
        }

CHOICE_ADDRESSES = {
        'BCH': ['bitcoincash:qzugzzywj840yy6a2zls8nj2ja5rgx8jtc6efrwzy5', 'bitcoincash:qqd87nlsmf8qztr2234600tr48k77hyz3c6q7kp662', 'bitcoincash:qrrlkrx4k0fywput47kvmeryfk8rl40x95rv7fqspr'],
        'BSV': ['', '', '']
        }


BITDB_API_KEY = "qpmy6xjrxewz7n8vy2jhx3rka5vr9vjx6c069770tp"
