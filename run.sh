#!/bin/bash

# 检查是否安装了 python3
if ! command -v python3 &> /dev/null
then
    echo "未找到 python3，请先安装 Python。"
    exit
fi

# 激活虚拟环境
if [ -d "venv" ]; then
    echo "正在激活虚拟环境..."
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
fi

echo "正在安装依赖..."
pip install -r requirement.txt

echo "正在应用数据库迁移..."
python manage.py makemigrations
python manage.py migrate

echo "正在启动服务器..."
python manage.py runserver 0.0.0.0:8000
