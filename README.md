# Windows Topper

Windows 窗口置顶管理器 — 浏览和管理所有运行窗口的置顶状态。

![](docs/screenshot.png)

## 功能

- **窗口列表** — 枚举所有可见顶层窗口，以树形结构展示父子层级关系
- **置顶控制** — 双击列表项或选中后点击按钮，快速切换窗口置顶状态
- **窗口选取** — 点击 🎯 选取窗口，再用鼠标点击目标窗口直接切换置顶
- **颜色标识** — 置顶窗口蓝色高亮、焦点窗口橙色标注、组合状态特殊色
- **焦点追踪** — 实时高亮当前焦点所在的窗口
- **搜索过滤** — 按窗口名/进程名/类名实时过滤
- **本窗口置顶** — 将管理器自身窗口置顶，方便随时操作
- **Fluent Design** — 圆角、亚克力质感的 Fluent 风格界面，支持浅色/深色主题（跟随系统）

## 用法

1. 运行 `WindowsTopper.exe`
2. 窗口列表自动展示所有可见窗口
3. 双击任意窗口切换其置顶状态
4. 点击 🎯 选取窗口 → 点击目标窗口快速切换
5. 使用搜索框过滤窗口

## 下载

从 Releases 下载最新版本。

## 构建

```powershell
pip install -r requirements.txt
pyinstaller --noconsole --onefile main.py -n WindowsTopper
```

## 依赖

- Python 3.13+
- PyQt5
- pywin32

## 许可证

[MIT](LICENSE)
