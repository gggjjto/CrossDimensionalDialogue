@echo off
REM 启动支持 pgvector 的 Docker 环境

echo 🚀 启动支持 pgvector 的 Docker 环境...

REM 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未运行，请先启动 Docker
    pause
    exit /b 1
)

REM 停止现有容器
echo 🛑 停止现有容器...
docker-compose down

REM 询问是否删除数据库数据
set /p delete_data="是否删除现有数据库数据？这将清除所有数据 (y/N): "
if /i "%delete_data%"=="y" (
    echo 🗑️  删除数据库卷...
    docker volume rm dahuanya_app-db-data 2>nul
)

REM 启动服务
echo 🚀 启动服务...
docker-compose up -d db

REM 等待数据库启动
echo ⏳ 等待数据库启动...
timeout /t 10 /nobreak >nul

REM 检查 pgvector 扩展
echo 🔍 检查 pgvector 扩展...
docker-compose exec db psql -U %POSTGRES_USER% -d %POSTGRES_DB% -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"

REM 启动其他服务
echo 🚀 启动其他服务...
docker-compose up -d

echo ✅ 环境启动完成！
echo.
echo 📋 服务地址：
echo    - 后端 API: http://localhost:8000
echo    - 前端界面: http://localhost:5173
echo    - 数据库管理: http://localhost:8080
echo    - 邮件测试: http://localhost:1080
echo.
echo 🔧 测试 pgvector：
echo    python backend/app/scripts/test_pgvector.py
echo.
echo 🔧 测试向量搜索：
echo    python backend/app/scripts/test_vector_search.py
echo.
pause
