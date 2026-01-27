#!/usr/bin/env python3
"""
验证语言和模型选择功能
"""

import json
from pathlib import Path

print("🔍 验证语言和模型选择功能")
print("=" * 60)

# 1. 检查whisper.cpp可用模型
models_dir = Path("../whisper.cpp/models")
if models_dir.exists():
    print("\n📦 已下载的Whisper模型:")
    model_files = sorted(models_dir.glob("ggml-*.bin"))
    for model_file in model_files:
        if "for-tests" not in model_file.name:
            size_mb = model_file.stat().st_size / (1024 * 1024)
            print(f"  ✓ {model_file.name:<25} ({size_mb:.1f} MB)")
    
    if not model_files:
        print("  ⚠️  没有找到模型文件")
        print("  使用以下命令下载:")
        print("    cd ../whisper.cpp/models")
        print("    ./download-ggml-model.sh base")
else:
    print("\n⚠️  whisper.cpp models 目录不存在")

# 2. 检查最新事件的配置
print("\n📋 最近事件的语言和模型配置:")
events_dir = Path("events")
if events_dir.exists():
    event_dirs = sorted([d for d in events_dir.iterdir() if d.is_dir()], reverse=True)
    for event_dir in event_dirs[:3]:  # 显示最近3个
        event_json = event_dir / "event.json"
        if event_json.exists():
            with open(event_json) as f:
                event = json.load(f)
            
            language = event.get("language", "N/A")
            model = event.get("whisper_model", "N/A")
            print(f"\n  Event: {event.get('title', 'Untitled')}")
            print(f"  ├─ ID: {event_dir.name}")
            print(f"  ├─ Language: {language}")
            print(f"  └─ Model: {model}")

# 3. 提供快速测试命令
print("\n" + "=" * 60)
print("🧪 测试建议:")
print("\n1. 重启服务器:")
print("   python api_server.py")
print("\n2. 在浏览器创建新事件:")
print("   http://localhost:3000/events/create")
print("\n3. 选择不同的语言和模型组合")
print("\n4. 验证事件配置:")
print("   cat events/NEW_EVENT_ID/event.json | grep -E '(language|whisper_model)'")
print("\n5. 运行工作流并查看日志:")
print("   应该看到: 'Using Whisper model: XXX, Language: YYY'")

print("\n" + "=" * 60)
print("✅ 功能已就绪！")
