#!/bin/bash
# 清理失败的事件并重启服务器

echo "🧹 清理失败的事件..."
if [ -d "events/2026-01-27_0009_test1" ]; then
    rm -rf events/2026-01-27_0009_test1
    echo "✓ 已删除失败的事件"
fi

echo ""
echo "🔄 准备重启API服务器..."
echo ""
echo "请手动执行以下步骤："
echo "1. 在运行API服务器的终端按 Ctrl+C 停止服务器"
echo "2. 运行: python api_server.py"
echo "3. 在浏览器刷新页面"
echo "4. 创建新事件并上传视频"
echo "5. 运行工作流"
echo ""
echo "或者使用以下命令自动重启（如果在后台运行）："
echo "  pkill -f 'python.*api_server.py' && python api_server.py &"
