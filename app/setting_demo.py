import decimal

TIMEZONE = 'Asia/Shanghai'
DEFAULT_LANGUAGES = 'en_US'
SUPPORTED_LANGUAGES = ['en_US', 'zh_Hans_CN', 'zh_Hant_HK']

SESSION_LIFETIME = 86400
SECRET_KEY = 'Your Secret Key'

SQLALCHEMY_DATABASE_URI = 'mysql://user:password@mysql_server/game_dice'
SQLALCHEMY_TRACK_MODIFICATIONS = True

CACHE_TYPE = "redis"
REDIS_URL = "redis://:@127.0.0.1:6379/1"
ALERT_REDIS_URL = "redis://:@127.0.0.1:6379/1"
CACHE_REDIS_URL = "redis://:@127.0.0.1:6379/2"
CELERY_BROKER_URL = 'redis://:@127.0.0.1:6379/3'
CELERY_RESULT_BACKEND = 'redis://:@127.0.0.1:6379/4'

PAGE_CAPACITY = 20

CLIENT_AUTH = {
        'bitcoin_cash': {
            'host': '192.168.0.1',
            'port': 8332,
            'protocol': 'http',
            'auth': ('rpcuser', 'rpcpassword')
            },
        'bitcoin_sv': {
            'host': '192.168.0.2',
            'port': 8332,
            'protocol': 'http',
            'auth': ('rpcuser', 'rpcpassword')
            }
        }

CHOICE_ADDRESSES = {
        'BCH': ['bitcoincash:qzugzzywj840yy6a2zls8nj2ja5rgx8jtc6efrwzy5', 'bitcoincash:qqd87nlsmf8qztr2234600tr48k77hyz3c6q7kp662', 'bitcoincash:qrrlkrx4k0fywput47kvmeryfk8rl40x95rv7fqspr'],
        'BSV': ['', '', '']
        }


