# 使用官方 Python 运行时作为父镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（用于 xhtml2pdf）
RUN apt-get update && apt-get install -y \
    libpangocairo-1.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# 将当前目录内容复制到容器的 /app 中
COPY . /app

# 安装 requirement.txt 中指定的任何所需软件包
RUN pip install --no-cache-dir -r requirement.txt

# 暴露端口 8000 供外部访问
EXPOSE 8000

# 启动服务器
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
