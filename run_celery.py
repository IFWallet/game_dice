#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from app import create_app
from app.ext import celery

app = create_app()
