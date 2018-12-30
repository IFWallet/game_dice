from celery.schedules import crontab

CELERY_IMPORTS = (
    "app.schedules.deposit",
    "app.schedules.withdraw",
)

CELERY_DEFAULT_QUEUE = 'game_default_queue'
CELERY_CREATE_MISSING_QUEUES = True
CELERY_QUEUES = {
    'game_deposit_queue': {
        'exchange': 'game_deposit_exchange',
        'exchange_type': 'direct',
        'binding_key': 'game_deposit_route_key',
    },
    'game_withdraw_queue': {
        'exchange': 'game_withdraw_exchange',
        'exchange_type': 'direct',
        'binding_key': 'game_withdraw_route_key',
    },
    'game_default_queue': {
        'exchange': 'default_exchange',
        'exchange_type': 'direct',
        'binding_key': 'default_route_key',
    },
}


class MyRouter(object):
    def route_for_task(self, task, args=None, kwargs=None):
        if task.startswith('app.schedules.deposit.'):
            return {'queue': 'game_deposit_queue'}
        elif task.startswith('app.schedules.withdraw.'):
            return {'queue': 'game_withdraw_queue'}
        else:
            return {'queue': 'game_default_queue'}


CELERY_ROUTES = (MyRouter(), )

CELERYBEAT_SCHEDULE = {
        # order
        'game_process_bch_deposit_schedule': {
            'task': 'app.schedules.deposit.bch.process_bch_deposit_task',
            'schedule': 5,
            },
        'game_update_bch_deposit_schedule': {
            'task': 'app.schedules.deposit.bch.update_bch_deposit_task',
            'schedule': crontab(minute='*/1'),
            },
        # reward
        'game_sync_bch_block_schedule': {
            'task': 'app.schedules.withdraw.bch.sync_bch_block_task',
            'schedule': crontab(minute='*/1'),
            },
        'game_update_bch_block_schedule': {
            'task': 'app.schedules.withdraw.bch.update_bch_block_task',
            'schedule': crontab(minute='*/1'),
            },
        #'game_alloc_bch_reward_schedule': {
        #    'task': 'app.schedules.withdraw.bch.alloc_bch_reward_task',
        #    'schedule': crontab(minute='*/5'),
        #    },
        'game_send_bch_reward_schedule': {
            'task': 'app.schedules.withdraw.bch.send_bch_reward_task',
            'schedule': crontab(minute='*/5'),
            },
        }


CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
CELERY_IGNORE_RESULT = True

DEBUG_LOG = '/var/log/game_dice/celery_debug.log'
ERROR_LOG = '/var/log/game_dice/celery_error.log'
