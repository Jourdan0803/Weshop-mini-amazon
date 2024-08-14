#!/bin/bash

# 启动 Django 服务器
python3 manage.py runserver 0.0.0.0:8000 --noreload &

# 等待 Django 服务器启动
sleep 5

# 执行测试
python3 test.py