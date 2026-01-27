#!/usr/bin/env python3
"""
测试模块功能的脚本
用于验证字幕生成和缩略图合成是否正常工作
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.subtitles.engine_whispercpp import WhisperCppEngine
from modules.thumbnail.composer_pillow import ThumbnailComposer


def test_subtitle_engine():
    """测试字幕引擎"""
    print("\n" + "="*60)
    print("测试字幕生成引擎")
    print("="*60)
    
    engine = WhisperCppEngine(model="base")
    
    print(f"✓ whisper.cpp 可用: {engine.available}")
    print(f"✓ 模型路径: {engine.model_path}")
    print(f"✓ 模型存在: {engine.check_model()}")
    
    if not engine.available:
        print("\n⚠️  whisper.cpp 未安装或未配置")
        print("请在 Dependencies 页面安装或配置 whisper.cpp")
        return False
    
    if not engine.check_model():
        print("\n⚠️  模型文件不存在")
        print("请下载模型文件到 models/ 目录")
        print("或配置自定义模型路径")
        return False
    
    print("\n✓ 字幕引擎准备就绪")
    return True


def test_thumbnail_composer():
    """测试缩略图合成器"""
    print("\n" + "="*60)
    print("测试缩略图合成器")
    print("="*60)
    
    composer = ThumbnailComposer()
    
    # 创建测试输出目录
    test_output = Path("test_output")
    test_output.mkdir(exist_ok=True)
    
    # 测试基本缩略图生成
    output_path = test_output / "test_thumbnail.jpg"
    
    success, error = composer.compose(
        output_path=str(output_path),
        title="测试证道标题\nGod's Amazing Grace",
        scripture="约翰福音 3:16"
    )
    
    if success:
        print(f"\n✓ 缩略图生成成功: {output_path}")
        print(f"  文件大小: {output_path.stat().st_size / 1024:.1f} KB")
        return True
    else:
        print(f"\n✗ 缩略图生成失败: {error}")
        return False


def test_event_workflow():
    """测试事件工作流"""
    print("\n" + "="*60)
    print("测试事件工作流")
    print("="*60)
    
    # 检查是否有测试事件
    events_dir = Path("events")
    event_dirs = [d for d in events_dir.iterdir() if d.is_dir() and d.name != "."]
    
    if not event_dirs:
        print("\n⚠️  没有找到测试事件")
        print("请在Web界面创建一个事件并上传视频")
        return False
    
    # 使用最新的事件
    latest_event = sorted(event_dirs)[-1]
    print(f"\n✓ 找到事件: {latest_event.name}")
    
    # 检查事件配置
    event_json = latest_event / "event.json"
    if event_json.exists():
        import json
        with open(event_json) as f:
            event_data = json.load(f)
        
        print(f"  标题: {event_data.get('title')}")
        print(f"  讲员: {event_data.get('speaker')}")
        print(f"  视频: {len(event_data.get('inputs', {}).get('video_files', []))} 个")
        
        if event_data.get('inputs', {}).get('video_files'):
            video_path = event_data['inputs']['video_files'][0]
            print(f"  视频路径: {video_path}")
            print(f"  视频存在: {Path(video_path).exists()}")
    
    # 检查输出
    output_dir = latest_event / "output"
    if output_dir.exists():
        output_files = list(output_dir.iterdir())
        print(f"\n✓ 输出文件数量: {len(output_files)}")
        for f in output_files:
            print(f"  - {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    else:
        print("\n⚠️  输出目录为空")
        print("运行工作流后会生成输出文件")
    
    return True


def main():
    """主函数"""
    print("\n" + "="*60)
    print("Church Media Automation System - 模块测试")
    print("="*60)
    
    results = {
        "字幕引擎": test_subtitle_engine(),
        "缩略图合成": test_thumbnail_composer(),
        "事件工作流": test_event_workflow()
    }
    
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 所有测试通过！系统已准备就绪。")
        print("\n下一步:")
        print("1. 在Web界面创建一个新事件")
        print("2. 上传视频文件")
        print("3. 点击 'Run Workflow' 运行处理")
        print("4. 在事件的 output/ 目录查看生成的文件")
    else:
        print("\n⚠️  部分测试未通过")
        print("请检查上面的错误信息并解决问题")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
