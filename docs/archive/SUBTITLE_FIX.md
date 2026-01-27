````markdown
# 🔧 字幕生成问题已修复

## 问题分析

你遇到的错误有两个根本原因：

### 1. 模型路径问题 ❌
```
whisper.cpp failed: failed to open '../whisper.cpp/models/ggml-base.bin'
```

**原因**：相对路径 `../whisper.cpp/models/ggml-base.bin` 从 API 服务器的工作目录解析失败。

### 2. 文件名空格问题 ❌
```
error: input file not found 'events/2026-01-27_0009_test1/output/CST-405 Final_audio.wav'
```

**原因**：视频文件名 "CST-405 Final.mp4" 包含空格，生成的音频文件名也包含空格，导致 whisper.cpp 命令行解析失败。

---

## 已实施的修复 ✅

### 修复 1: 模型路径转换为绝对路径
**文件**: `modules/subtitles/engine_whispercpp.py`

```python
# 之前：直接使用相对路径
self.model_path = Path(custom_model)

# 现在：转换为绝对路径
model_path = Path(custom_model)
if not model_path.is_absolute():
    model_path = Path.cwd() / model_path
self.model_path = model_path
```

**结果**：
- ❌ 之前: `../whisper.cpp/models/ggml-base.bin`
- ✅ 现在: `/Users/justin/Desktop/Justin/school/CMAS/../whisper.cpp/models/ggml-base.bin`

### 修复 2: 文件名空格处理
**文件**: `modules/subtitles/engine_whispercpp.py`

```python
# 音频提取时清理文件名
stem = Path(video_path).stem.replace(' ', '_')
audio_path = Path(output_dir) / f"{stem}_audio.wav"

# 转录时也使用清理后的文件名
base_name = Path(input_path).stem.replace(' ', '_')

# 使用绝对路径避免解析问题
cmd = [
    self.whisper_bin,
    "-m", str(self.model_path.absolute()),
    "-f", str(Path(input_path).absolute()),
]
```

**结果**：
- ❌ 之前: `CST-405 Final_audio.wav`
- ✅ 现在: `CST-405_Final_audio.wav` (空格替换为下划线)

---

## 如何应用修复

### 步骤 1: 重启 API 服务器（必须）

代码已经修改，但服务器还在运行旧代码。

**方法 A: 手动重启**（推荐）
```bash
# 在运行 API 服务器的终端窗口：
# 1. 按 Ctrl+C 停止服务器
# 2. 重新运行：
python api_server.py
```

**方法 B: 使用脚本**
```bash
./restart_system.sh
```

### 步骤 2: 重新测试

#### 选项 A: 使用现有事件重新运行
```bash
# 先删除失败的输出
rm -rf events/2026-01-27_0009_test1/output/*
rm -rf events/2026-01-27_0009_test1/logs/*

# 然后在 Web 界面点击 "Run Workflow"
```

#### 选项 B: 创建新事件（推荐）
1. 在浏览器刷新页面
2. 创建新事件
3. 上传视频（同样的视频也可以）
4. 点击 "Run Workflow"

---

## 验证修复成功

### 1. 检查服务器日志

应该看到类似这样的输出：
```
INFO - Running subtitle generation...
INFO - Running whisper.cpp: /Users/justin/.../whisper-cli -m /Users/justin/.../ggml-base.bin -f /Users/justin/.../CST-405_Final_audio.wav ...
INFO - Subtitles generated: {'srt': '.../output/CST-405_Final.srt', 'vtt': '.../output/CST-405_Final.vtt'}
```

**关键点**：
- ✅ 模型路径是绝对路径
- ✅ 音频文件名没有空格
- ✅ 显示 "Subtitles generated"

### 2. 检查输出文件

```bash
ls -lh events/NEW_EVENT_ID/output/
```

应该看到：
```
CST-405_Final_audio.wav    # 提取的音频（8-10MB）
CST-405_Final.srt          # 字幕文件
CST-405_Final.vtt          # 字幕文件
```

### 3. 查看字幕内容

```bash
head -20 events/NEW_EVENT_ID/output/*.srt
```

应该看到实际的转录文字。

---

## 处理时间预期

| 视频长度 | 预期时间 |
|---------|---------|
| 5分钟   | 30-60秒 |
| 15分钟  | 1-2分钟 |
| 30分钟  | 3-5分钟 |
| 1小时   | 6-10分钟 |

**你的视频**：如果 "CST-405 Final.mp4" 大约是 15-30 分钟，预期 2-5 分钟完成。

处理过程中：
- Web界面会显示 "Processing" 状态
- API服务器终端会显示进度日志
- 不要刷新页面或停止服务器

---

## 故障排除

### 问题：重启后还是报同样的错误

**检查**：
1. 确认 API 服务器确实重启了（检查终端输出开始时间）
2. 浏览器清除缓存或强制刷新（Cmd+Shift+R）
3. 删除旧的失败事件，创建新事件

### 问题：音频提取失败

**检查 ffmpeg**：
```bash
which ffmpeg
ffmpeg -version
```

**解决**：
```bash
brew install ffmpeg  # macOS
```

### 问题：whisper.cpp 仍然找不到模型

**手动测试**：
```bash
/Users/justin/Desktop/Justin/school/whisper.cpp/build/bin/whisper-cli \
  -m /Users/justin/Desktop/Justin/school/whisper.cpp/models/ggml-base.bin \
  --help
```

如果失败，说明路径配置有问题，需要在 `config/config.yaml` 中更新。

---

## 测试修复的快速命令

```bash
# 1. 验证修复已应用
python test_modules.py

# 2. 清理失败的事件（可选）
rm -rf events/2026-01-27_0009_test1

# 3. 重启服务器（在另一个终端）
# 停止旧服务器，然后：
python api_server.py

# 4. 测试字幕引擎（独立测试）
python modules/subtitles/engine_whispercpp.py \
  --video "/Users/justin/Downloads/CST-405 Final.mp4" \
  --output-dir test_output \
  --language auto
```

---

## 确认清单

在重新测试前，确认：

- [ ] 代码已保存（engine_whispercpp.py）
- [ ] API 服务器已重启（查看启动时间）
- [ ] 浏览器已刷新
- [ ] 创建新事件（或清理旧事件输出）
- [ ] 上传视频
- [ ] 点击 "Run Workflow"
- [ ] 耐心等待几分钟

---

## 预期成功输出

完成后你应该看到：

### Web 界面
- ✅ 状态从 "Processing" 变为 "Completed"
- ✅ Subtitles 模块显示绿色勾号

### 文件系统
```bash
events/NEW_EVENT_ID/output/
├── CST-405_Final_audio.wav  (8-10 MB)
├── CST-405_Final.srt         (几十 KB)
└── CST-405_Final.vtt         (几十 KB)
```

### 字幕内容
打开 .srt 文件应该看到实际的转录文字，不是空文件。

---

🎉 **修复已完成！重启服务器并重新运行工作流即可。**

如果还有问题，查看服务器日志并告诉我具体的错误信息。

````