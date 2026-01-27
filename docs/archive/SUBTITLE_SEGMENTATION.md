````markdown
# ✂️ 字幕切割控制功能

## 问题描述

之前生成的字幕可能出现过长的句子，例如：
```
15
00:01:37,000 --> 00:02:06,000  ← 持续29秒！
 So you can see in this part we already put all the functions in it, 
 from the beginning to the operators, e-files, well loop, all the loops, 
 local arrays, arrays, and all the functions to all the basic, 
 basic different function for the calculations parts.
```

这样的长句子：
- ❌ 难以阅读
- ❌ 屏幕放不下
- ❌ 观众来不及看完

---

## ✅ 解决方案

添加了**字幕切割控制**参数，让你可以：

1. **限制每行字符数** - 控制字幕长度
2. **在单词边界切割** - 避免切断单词

---

## 🎛️ 新增功能

### 前端界面

在创建事件页面新增 **Subtitle Settings** 区域：

```
Subtitle Settings
├── Max Characters per Line
│   └── [输入框: 40-200] (推荐: 60-84)
└── ☑ Split on Word Boundaries
    └── Avoid breaking words mid-sentence
```

### 默认值

- **最大字符数**: 84 字符（适合大多数屏幕）
- **单词边界切割**: 启用（避免切断单词）

---

## 📊 推荐设置

### 按语言推荐

| 语言 | 推荐字符数 | 原因 |
|------|-----------|------|
| **英语** | **60-84** | 单词较长，需要更多空间 |
| **中文** | **40-60** | 汉字信息密度高 |
| **日语/韩语** | **50-70** | 中等密度 |
| **西班牙语/法语** | **70-90** | 单词通常较长 |

### 按用途推荐

| 用途 | 字符数 | 单词切割 | 说明 |
|------|--------|---------|------|
| **YouTube视频** | 60-84 | ✅ | 标准推荐 |
| **手机观看** | 40-60 | ✅ | 小屏幕适配 |
| **影院/大屏** | 80-100 | ✅ | 更多空间 |
| **快速浏览** | 40-50 | ✅ | 短句子更易读 |

---

## 🔧 whisper.cpp 参数说明

系统使用以下参数控制切割：

### `--max-len N`
- **作用**: 限制每个字幕段落的最大字符数
- **默认**: 0（无限制）
- **推荐**: 60-84
- **示例**: `--max-len 84`

### `-sow` (split-on-word)
- **作用**: 在单词边界切割，而不是在token边界
- **默认**: 关闭
- **推荐**: 开启
- **效果**:
  ```
  ❌ 关闭: "...all the func-"
              "tions in it..."
  
  ✅ 开启: "...all the"
           "functions in it..."
  ```

---

## 💡 使用示例

### 示例 1: 英语证道（标准设置）

**设置**:
- Language: English
- Whisper Model: Base
- Max Characters: 84
- Split on Word: ✅

**结果**:
```
1
00:00:00,000 --> 00:00:04,000
Welcome to our church service today.

2
00:00:04,000 --> 00:00:08,000
We're going to talk about God's amazing grace.
```

### 示例 2: 中文证道（短句设置）

**设置**:
- Language: 中文
- Whisper Model: Small
- Max Characters: 50
- Split on Word: ✅

**结果**:
```
1
00:00:00,000 --> 00:00:03,000
欢迎来到今天的主日崇拜

2
00:00:03,000 --> 00:00:06,000
今天我们要分享神的恩典
```

### 示例 3: 技术内容（详细模式）

**设置**:
- Language: English
- Whisper Model: Medium
- Max Characters: 70
- Split on Word: ✅

**结果**:
```
15
00:01:37,000 --> 00:01:42,000
So you can see in this part we already put all the functions

16
00:01:42,000 --> 00:01:47,000
from the beginning to the operators, e-files, well loop,

17
00:01:47,000 --> 00:01:52,000
all the loops, local arrays, arrays, and all the functions
```

---

## 🔄 对比效果

### 之前（无控制）
```
1
00:00:00,000 --> 00:00:15,000
Welcome to our church service today. We are going to talk about God's amazing grace and how it transforms our lives. This is an important topic that we should all understand deeply.
```
- ❌ 太长（150+字符）
- ❌ 持续15秒
- ❌ 屏幕放不下

### 之后（max_length=84）
```
1
00:00:00,000 --> 00:00:05,000
Welcome to our church service today. We are going to talk about

2
00:00:05,000 --> 00:00:10,000
God's amazing grace and how it transforms our lives.

3
00:00:10,000 --> 00:00:15,000
This is an important topic that we should all understand deeply.
```
- ✅ 适中长度（60-84字符）
- ✅ 每段5秒
- ✅ 易于阅读

---

## 🎯 如何使用

### 步骤 1: 重启服务器

```bash
# 后端
python api_server.py

# 前端（如果需要）
cd frontend
npm run dev
```

### 步骤 2: 创建新事件

1. 访问 http://localhost:3000/events/create
2. 填写基本信息
3. 在 **Subtitle Settings** 区域：
   - 设置 **Max Characters per Line** (推荐: 84)
   - 勾选 **Split on Word Boundaries** ✅
4. 创建事件

### 步骤 3: 验证设置

查看事件配置：
```bash
cat events/NEW_EVENT_ID/event.json | grep -A 3 "subtitle_settings"
```

应该看到：
```json
"subtitle_settings": {
  "max_length": 84,
  "split_on_word": true
}
```

### 步骤 4: 运行工作流

运行后查看日志：
```
INFO - Using Whisper model: base, Language: en
INFO - Subtitle settings: max_length=84, split_on_word=True
```

---

## 🧪 实验不同设置

### 测试方案

使用**同一个视频**，尝试不同的设置：

| 测试 | 字符数 | 单词切割 | 预期效果 |
|------|--------|---------|----------|
| A | 0 | ❌ | 原始输出（可能很长）|
| B | 84 | ❌ | 限制长度，可能切断单词 |
| C | 84 | ✅ | 限制长度，完整单词 ✅ |
| D | 50 | ✅ | 更短的句子 |

---

## ⚙️ 高级技巧

### 1. 根据视频类型调整

**快节奏内容**（新闻、讲座）:
- Max Length: 50-60
- 更频繁的切换，易于跟上

**慢节奏内容**（冥想、诗歌）:
- Max Length: 80-100
- 允许更长的句子

### 2. 多次处理优化

1. 第一次: max_length=0 (无限制) - 查看原始结果
2. 调整参数重新运行
3. 对比效果，选择最佳设置

### 3. 手动后期调整

生成后可以手动编辑 .srt 文件：
```bash
# 编辑字幕
nano events/EVENT_ID/output/video.srt

# 使用字幕编辑器
# Subtitle Edit (Windows/Linux)
# Aegisub (跨平台)
```

---

## 📝 配置文件示例

完整的事件配置：

```json
{
  "event_id": "2026-01-27_1500_sunday-service",
  "title": "Sunday Service - God's Grace",
  "speaker": "Pastor John",
  "language": "en",
  "whisper_model": "base",
  "subtitle_settings": {
    "max_length": 84,
    "split_on_word": true
  },
  "modules": {
    "subtitles": true
  }
}
```

---

## 🐛 故障排除

### 问题: 设置不生效

**检查**:
```bash
# 1. 确认事件配置
cat events/EVENT_ID/event.json | grep subtitle_settings

# 2. 查看服务器日志
# 应该看到: "Subtitle settings: max_length=84, split_on_word=True"
```

### 问题: 字幕还是太长

**可能原因**:
- whisper.cpp 版本太旧，不支持这些参数
- max_length 设置过大

**解决方法**:
1. 降低 max_length (尝试 50-60)
2. 检查 whisper.cpp 版本：
   ```bash
   /path/to/whisper-cli --help | grep "max-len"
   ```

### 问题: 单词被切断

**解决方法**:
- 确保 `split_on_word` 设置为 `true`
- 检查日志确认参数被应用

---

## 📚 参考资料

### whisper.cpp 官方文档
- [GitHub](https://github.com/ggerganov/whisper.cpp)
- [命令行参数](https://github.com/ggerganov/whisper.cpp#command-line)

### 字幕最佳实践
- Netflix 字幕指南
- YouTube 字幕规范
- 建议每秒 3-4 个单词
- 最多2行文字

---

## 🎉 总结

新功能让你可以：

✅ **控制字幕长度** - 避免过长的句子
✅ **优化阅读体验** - 更易于理解
✅ **适配不同场景** - 灵活调整
✅ **保持单词完整** - 专业的切割方式

**立即试用**，创建一个新事件并体验改进后的字幕质量！

````