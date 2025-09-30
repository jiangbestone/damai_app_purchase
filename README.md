# 大麦票务自动化抢票工具

一个基于 Appium 的大麦网自动化抢票工具，支持 Android 设备，专为演唱会、话剧等热门票务抢购场景设计。

## ✨ 功能特性

- 🎯 **智能抢票**：自动搜索演出、选择场次、选择票价、提交订单
- 👥 **多用户支持**：支持为多个用户同时抢票
- 🚀 **性能优化**：针对抢票场景进行极致性能优化，提升抢票成功率
- 🔄 **重试机制**：内置智能重试机制，提高抢票稳定性
- ⚡ **快速点击**：使用原生手势点击，响应速度更快
- 📱 **Android 专用**：专为大麦 Android APP 设计

## 🎭 支持场景

- 演唱会门票抢购
- 话剧/音乐剧门票抢购
- 体育赛事门票抢购
- 其他大麦平台热门票务

> **注意**：目前仅支持抢票功能，预约功能暂未实现

## 📋 环境要求

### 系统要求
- **操作系统**：Windows/macOS/Linux
- **Python 版本**：Python 3.7+
- **Android 设备**：Android 5.0+ (API Level 21+)

### 必需软件
- [Node.js](https://nodejs.org/) (用于安装 Appium)
- [Android SDK](https://developer.android.com/studio) 或 [Android Studio](https://developer.android.com/studio)
- [Java JDK 8+](https://www.oracle.com/java/technologies/javase-downloads.html)

### Python 依赖
```
appium-python-client>=3.0.0
selenium>=4.0.0
```

## 🚀 安装配置

### 1. 安装 Appium
```bash
npm install -g appium
npm install -g appium-doctor
```

### 2. 安装 UiAutomator2 驱动
```bash
appium driver install uiautomator2
```

### 3. 验证环境
```bash
appium-doctor --android
```

### 4. 克隆项目
```bash
git clone <your-repo-url>
cd damai_appium
```

### 5. 安装 Python 依赖
```bash
pip install appium-python-client selenium 
```

### 6. 设备准备
1. 在 Android 设备上安装大麦 APP
2. 开启开发者选项和 USB 调试
3. 连接设备到电脑，确保 `adb devices` 能识别设备
4. 在大麦 APP 中登录你的账号

## ⚙️ 配置说明

编辑 `config.json` 文件：

```json
{
  "server_url": "http://127.0.0.1:4723/",
  "keyword": "刘若英",
  "users": [
    "用户姓名1",
    "用户姓名2"
  ],
  "city": "演出地点",
  "date": "演出时间",
  "time": "抢票时间",
  "price": "目标票价",
  "price_index": 3,
  "if_commit_order": true
}
```

### 配置参数说明

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `server_url` | string | Appium 服务器地址 | `"http://127.0.0.1:4723/"` |
| `keyword` | string | 搜索关键词（艺人/演出名称） | `"刘若英"` |
| `users` | array | 购票用户列表 | `["用户1", "用户2"]` |
| `city` | string | 演出城市 | `"南京"` |
| `date` | string | 演出日期 | `"2025-11-02"` |
| `time` | string | 开抢时间 | `"13:17:00"` |
| `price` | string | 目标票价 | `"1099"` |
| `price_index` | number | 票价选项索引（从0开始） | `3` |
| `if_commit_order` | boolean | 是否自动提交订单 | `true` |

## 🎯 使用方法

### 1. 启动 Appium 服务
```bash
appium --address 0.0.0.0 --port 4723 --relaxed-security
```

### 2. 运行抢票程序
```bash
python damai_app.py
```

### 3. 监控执行过程
程序会显示详细的执行进度，包括：
- 连接状态
- 搜索进度
- 选择状态
- 抢票结果

## 🔧 性能优化特性

- **极速点击**：使用 `mobile: clickGesture` 原生手势
- **智能等待**：优化的 WebDriverWait 策略
- **性能配置**：针对抢票场景的 Appium 配置优化
- **坐标缓存**：预收集元素坐标，批量快速点击
- **动画禁用**：关闭不必要的动画效果

## ⚠️ 注意事项

1. **合法使用**：请遵守大麦网的使用条款，仅用于个人正常购票需求
2. **设备要求**：确保 Android 设备性能良好，网络连接稳定
3. **时间同步**：建议与网络时间同步，确保抢票时机准确
4. **账号安全**：使用前请确保大麦账号已登录且状态正常
5. **测试建议**：建议先用非热门票务进行测试
6. **网络环境**：建议使用稳定的网络环境，避免网络波动影响抢票

## 🐛 常见问题

### Q: Appium 连接失败
A: 检查 Appium 服务是否启动，设备是否正确连接，USB 调试是否开启

### Q: 找不到元素
A: 大麦 APP 界面可能更新，需要根据最新界面调整元素定位策略

### Q: 抢票失败
A: 可能是网络延迟或服务器压力大，建议优化网络环境或调整重试策略

### Q: 程序卡住不动
A: 检查设备屏幕是否亮起，大麦 APP 是否在前台运行

## 📄 免责声明

本工具仅供学习和研究使用，使用者应当：

1. 遵守相关法律法规和大麦网服务条款
2. 不得用于商业用途或恶意抢票
3. 承担使用本工具可能产生的一切后果
4. 理解自动化工具存在的风险和不确定性

开发者不对使用本工具造成的任何损失承担责任。

## 📝 更新日志

### V2 版本更新
- ✅ 优化界面元素定位策略
- ✅ 增加重试机制
- ✅ 性能优化配置
- ✅ 多用户选择逻辑优化
- ✅ 使用 WebDriverWait 提升效率
- ✅ 原生手势点击优化

### 未来计划
- 🔄 实现预约功能
- 🔄 支持更多票务平台
- 🔄 图形化配置界面
- 🔄 实时日志监控

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📞 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

---

本项目是在项目ticket-purchase的基础上进行修改的，感谢项目ticket-purchase的作者提供的思路和代码。
https://github.com/WECENG/ticket-purchase

**⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！**