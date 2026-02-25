# Simple Assistant

简化版语音控制电脑助手

## 当前进度

- ✅ Phase 1: 项目初始化 + 基础音频
- ✅ Phase 2: STT 语音转文字
- ✅ Phase 3: TTS 文字转语音
- ✅ Phase 4: 唤醒系统（语音 + 按键）
- ✅ Phase 5: Skill 基础架构
- ✅ Phase 6: 关键词匹配引擎
- ✅ Phase 7: 内置 Skills 实现
- ✅ Phase 8: 完整系统整合

## 注意事项

### STT 模型下载

首次运行时，faster-whisper 会自动从 Hugging Face 下载模型。如果遇到网络问题：
1. 配置代理或 VPN
2. 手动下载模型到本地缓存目录（~/.cache/huggingface/）

### 模型大小选择

| 模型 | 大小 | 准确度 | 速度 |
|------|------|--------|------|
| tiny | 39MB | 低 | 最快 |
| base | 74MB | 中 | 快 |
| small | 244MB | 中高 | 中 |
| medium | 769MB | 高 | 慢 |
| large | 1550MB | 最高 | 最慢 |

## 项目结构

```
simple-assistant/
├── audio/
│   ├── microphone.py    # 录音功能
│   ├── player.py        # 播放功能
│   ├── stt.py           # 语音转文字 (faster-whisper)
│   └── tts.py           # 文字转语音 (edge-tts - 微软免费 TTS)
├── wake/
│   ├── key_detector.py    # 按键唤醒 (pynput)
│   ├── voice_detector.py  # 语音唤醒 (porcupine)
│   └── wake_system.py     # 整合的唤醒系统
├── skills/
│   ├── base.py           # Skill 基类
│   ├── registry.py       # Skill 注册中心
│   └── builtin/
│       ├── screen.py        # 截屏 Skill
│       ├── camera.py        # 摄像头 Skill
│       ├── system_cmd.py    # 系统命令 Skill
│       └── notification.py  # 系统通知 Skill
├── matcher/
│   ├── base.py           # Matcher 基类
│   └── keyword.py        # 关键词匹配器
├── config.py            # 配置管理
├── pyproject.toml       # 依赖配置
├── .env.example         # 配置示例
├── .env                 # 配置文件
├── test_audio.py        # 音频测试脚本
├── test_stt.py          # STT 测试脚本
├── test_tts.py          # TTS 测试脚本
├── test_wake.py         # 唤醒系统测试脚本
├── test_key_wake.py     # 按键唤醒测试脚本
├── test_skills.py       # Skill 基础架构测试脚本
├── test_matcher.py      # 关键词匹配测试脚本
├── test_builtin_skills.py  # 内置 Skills 测试脚本
├── test_full.py         # 完整功能测试脚本
├── assistant.py         # 电脑助手主程序
├── start.py             # 启动脚本
└── README.md
```

## 安装依赖

```bash
cd simple-assistant
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -e .
```

## 运行测试

### 音频测试
```bash
python test_audio.py
```
测试流程：
1. 录音 5 秒
2. 播放录音

### STT 语音转文字测试
```bash
python test_stt.py
```
测试流程：
1. 录音 5 秒
2. 语音转文字

### TTS 文字转语音测试
```bash
python test_tts.py
```
测试流程：
1. 播放语音
2. 保存语音到文件

### 按键唤醒测试
```bash
python test_key_wake.py
```
测试流程：
1. 按 Cmd+Shift+Space 触发唤醒
2. 程序会用语音反馈

**macOS 权限设置**：
- 首次运行需要在「系统偏好设置 → 安全性与隐私 → 辅助功能」中添加终端

### 唤醒系统测试（语音 + 按键）
```bash
python test_wake.py
```
测试流程：
1. 按键唤醒：按 Cmd+Shift+Space
2. 语音唤醒：说 "hey computer"（需要配置 Access Key）

### Skill 基础架构测试
```bash
python test_skills.py
```
测试流程：
1. 注册两个示例 Skill（hello 和 time）
2. 测试 Skill 执行和注册中心功能

### 关键词匹配引擎测试
```bash
python test_matcher.py
```
测试流程：
1. 注册示例 Skill
2. 测试 8 个用例，验证关键词匹配功能

### 内置 Skills 测试
```bash
python test_builtin_skills.py
```
测试流程：
1. 注册所有内置 Skills
2. 显示所有已注册的 Skills

### 完整功能测试
```bash
python test_full.py
```
测试流程：
1. 注册所有 Skills（示例 + 内置）
2. 测试 10 个用例，验证关键词匹配 + Skill 执行

### 启动电脑助手
```bash
# 1. 激活虚拟环境（如果未激活）
source venv/bin/activate

# 2. 启动助手
python start.py
```

### 使用方法
1. **唤醒方式**：
   - 按键唤醒：按 `Cmd+Shift+Space`
   - 语音唤醒：说 "hey computer"（需要配置 Access Key）

2. **支持的命令**：
   - **截屏**：截图、抓图
   - **摄像头**：拍照、打开摄像头
   - **系统命令**：打开 Safari、打开 Chrome、打开终端、打开 Finder
   - **系统通知**：通知我、提醒我、提示我
   - **时间查询**：几点了、现在几点、时间
   - **问候**：你好、hello、hi

3. **工作流程**：
   - 唤醒 → 听到提示音 → 说出命令 → 系统执行 → 语音反馈

### 其他 TTS 命令
```bash
# 列出所有可用中文语音
python -m audio.tts --list

# 直接播放文字
python -m audio.tts "你好，世界"

# 保存到文件
python -m audio.tts --save "你好" output.mp3
```

**可用中文语音推荐：**
- `zh-CN-XiaoxiaoNeural` (推荐) - 女生，自然
- `zh-CN-XiaoyiNeural` - 女生，温柔
- `zh-CN-YunxiNeural` - 男生，自然
- `zh-CN-YunjianNeural` - 男生，沉稳

## 配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 配置说明

#### STT 配置
- `STT_MODEL_SIZE`: Whisper 模型大小 (tiny/base/small/medium/large)
- `STT_MODEL_PATH`: 本地模型路径（可选，不使用 Hugging Face）
- `STT_LANGUAGE`: 语言 (zh=中文, en=英文)
- `STT_DEVICE`: 设备 (auto/cpu/cuda)

#### TTS 配置
- `TTS_VOICE`: 语音名称（使用 `python -m audio.tts --list` 查看可用语音）
- `TTS_RATE`: 语速 (1.0 = 正常速度)

#### 唤醒系统配置
- `WAKE_ACCESS_KEY`: Porcupine Access Key（从 https://console.picovoice.ai/ 获取，免费）
- `WAKE_KEYWORD`: 语音唤醒词（默认: "hey computer"）
- `WAKE_HOTKEY`: 按键唤醒热键（默认: "<cmd>+<shift>+<space>"）

**如何获取 Porcupine Access Key**：
1. 访问 https://console.picovoice.ai/
2. 注册/登录账号
3. 创建新项目，获取 Access Key
4. 在 .env 文件中设置 WAKE_ACCESS_KEY
