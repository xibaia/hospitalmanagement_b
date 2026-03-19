@echo off
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 未找到 python，请先安装 Python。
    pause
    exit /b
)

echo 正在安装依赖...
pip install -r requirement.txt

echo 正在应用数据库迁移...
python manage.py makemigrations
python manage.py migrate

echo 正在启动服务器...
python manage.py runserver 0.0.0.0:8000
pause
