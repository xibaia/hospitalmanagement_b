#!/bin/bash

# 检查是否安装了 Python 3.12
PYTHON_BIN="${PYTHON_BIN:-python3.12}"

if ! command -v "$PYTHON_BIN" &> /dev/null
then
    PROJECT_PYTHON="$(find .uv-python -name python3.12 -type f 2>/dev/null | head -n 1)"
    if [ -n "$PROJECT_PYTHON" ]; then
        PYTHON_BIN="$PROJECT_PYTHON"
    fi
fi

if ! command -v "$PYTHON_BIN" &> /dev/null && [ ! -x "$PYTHON_BIN" ]
then
    echo "未找到 Python 3.12，请先安装 Python 3.12，或通过 PYTHON_BIN 指定解释器。"
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "正在创建虚拟环境..."
    "$PYTHON_BIN" -m venv .venv
fi

echo "正在激活虚拟环境..."
source .venv/bin/activate

echo "正在安装依赖..."
python -m pip install -r requirement.txt

echo "正在应用数据库迁移..."
python manage.py migrate

echo "正在启动服务器..."
python manage.py runserver 0.0.0.0:8000
