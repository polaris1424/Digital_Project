# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import multiprocessing

bind = '127.0.0.1:8000'
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '-'
worker_class = "sync"
threads = 2
timeout = 120
loglevel = "info"

