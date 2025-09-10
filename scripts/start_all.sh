#!/usr/bin/env bash
set -euo pipefail

echo "🚀 启动 Memory-X 完整应用程序（后端 + 前端）"
echo "=" * 60

root_dir=$(cd "$(dirname "$0")/.." && pwd)
cd "$root_dir"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
  echo "📦 创建虚拟环境..."
  bash scripts/setup_venv.sh
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
  echo "📦 安装前端依赖..."
  cd frontend
  npm install
  cd ..
fi

echo ""
echo "🔧 启动服务..."
echo ""

# 启动后端服务（后台运行）
echo "🖥️ 启动后端 API 服务..."
bash scripts/run_api.sh &
BACKEND_PID=$!

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 检查后端是否启动成功
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
  echo "✅ 后端服务启动成功: http://localhost:5000"
else
  echo "❌ 后端服务启动失败"
  kill $BACKEND_PID 2>/dev/null || true
  exit 1
fi

# 启动前端服务
echo "🌐 启动前端开发服务器..."
echo ""
echo "📍 访问地址:"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

cd frontend
npm run dev

# 清理：当前端服务停止时，也停止后端服务
trap "kill $BACKEND_PID 2>/dev/null || true" EXIT