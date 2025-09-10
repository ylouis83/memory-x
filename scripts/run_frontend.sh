#!/usr/bin/env bash
set -euo pipefail

echo "🚀 启动 Memory-X 前端开发服务器..."

root_dir=$(cd "$(dirname "$0")/.." && pwd)
frontend_dir="$root_dir/frontend"

# 检查前端目录是否存在
if [ ! -d "$frontend_dir" ]; then
  echo "❌ 前端目录不存在: $frontend_dir"
  exit 1
fi

cd "$frontend_dir"

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
  echo "📦 首次运行，安装依赖..."
  npm install
fi

# 检查后端服务是否运行
echo "🔍 检查后端服务状态..."
backend_url="http://localhost:5000"
if curl -s "$backend_url/health" > /dev/null 2>&1; then
  echo "✅ 后端服务已运行在 $backend_url"
else
  echo "⚠️ 后端服务未运行，请先启动后端服务："
  echo "   cd $root_dir"
  echo "   source .venv/bin/activate"
  echo "   bash scripts/run_api.sh"
  echo ""
  echo "🔄 仍继续启动前端服务..."
fi

echo "🌐 启动前端开发服务器..."
echo "📍 前端地址: http://localhost:5173"
echo "🔗 API地址: http://localhost:5000"
echo ""

# 启动开发服务器
npm run dev