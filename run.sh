#!/bin/bash

# 检查是否安装了 python3
if ! command -v python3 &> /dev/null
then
    echo "未找到 python3，请先安装 Python。"
    exit
fi

echo "正在安装依赖..."
pip3 install -r requirement.txt

echo "正在应用数据库迁移..."
python3 manage.py makemigrations
python3 manage.py migrate

echo "正在启动服务器..."
python3 manage.py runserver 0.0.0.0:8000
