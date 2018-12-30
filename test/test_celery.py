#!/user/local/python
# -*- coding: utf-8 -*-

import pytest

from app.schedules.deposit import process_bch_deposit_task
from app.schedules.deposit import update_bch_deposit_task

from app.schedules.withdraw import sync_bch_block_task
from app.schedules.withdraw import update_bch_block_task
from app.schedules.withdraw import alloc_bch_reward_task
from app.schedules.withdraw import send_bch_reward_task


def test_celery(client):
    #t_process_bch_deposit_task()
    t_update_bch_deposit_task()

    #t_sync_bch_block_task()
    #t_update_bch_block_task()
    #t_alloc_bch_reward_task()
    t_send_bch_reward_task()

    assert False

def t_process_bch_deposit_task():
    process_bch_deposit_task()

def t_update_bch_deposit_task():
    update_bch_deposit_task()

def t_sync_bch_block_task():
    sync_bch_block_task()

def t_update_bch_block_task():
    update_bch_block_task()

def t_alloc_bch_reward_task():
    alloc_bch_reward_task()

def t_send_bch_reward_task():
    send_bch_reward_task()
