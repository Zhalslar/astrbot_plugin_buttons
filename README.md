
<div align="center">

![:name](https://count.getloli.com/@astrbot_plugin_buttons?name=astrbot_plugin_buttons&theme=minecraft&padding=6&offset=0&align=top&scale=1&pixelated=1&darkmode=auto)

# astrbot_plugin_buttons

_✨ [astrbot](https://github.com/AstrBotDevs/AstrBot) 发按钮插件 ✨_  

[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-3.4%2B-orange.svg)](https://github.com/Soulter/AstrBot)
[![GitHub](https://img.shields.io/badge/作者-Zhalslar-blue)](https://github.com/Zhalslar)

</div>

## 🤝 介绍

本插件利用napcat进行发包，实现了让野生bot发送QQ按钮，同时为其他astrbot插件提供易用的发按钮接口。
支持的QQ版本：9.1.55~最新版

> **warning**:  
> 发送按钮被检测时容易被封号，请谨慎使用。<br>
> 如果坚持使用，产生的一切后果由使用者承担。<br>
> 未来可能会被修复，不要过多依赖按钮。

## 📦 安装

- 可以直接在astrbot的插件市场搜索astrbot_plugin_buttons，点击安装，耐心等待安装完成即可  

```bash
# 克隆仓库到插件目录
cd /AstrBot/data/plugins
git clone https://github.com/Zhalslar/astrbot_plugin_buttons

# 控制台重启AstrBot!

```

## ⌨️ 使用说明

### 指令调用

发回调按钮（用短杠线）：按钮标签-回调文本

```plaintext
/按钮 点我-我是笨蛋
```

发链接按钮（用波浪线）：按钮标签~链接

```plaintext
/按钮 B站~https://www.bilibili.com/
```

多个按钮请用逗号隔开（中文逗号和英文逗号都可以）

```plaintext
/按钮 点我-我是笨蛋，彩蛋-我是小南娘，B站~https://www.bilibili.com
```

多行按钮请用|隔开

```plaintext
/按钮 点我-我是笨蛋|彩蛋-我是小南娘，B站~https://www.bilibili.com
```

### 其他插件调用示例

```bash
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("发送按钮")
    async send_buttons(self, event: AstrMessageEvent):
        """发送按钮"""
        buttons = {
            "type": "button",
            "content": [
                [
                    {"label": "点我", "callback": "我是笨蛋"},
                    {"label": "点他", "callback": "我是小男娘"},
                ],
                [
                    {"label": "点她", "callback": "看看腿"},
                    {"label": "B站", "link": "https://www.bilibili.com"},
                ],
            ],
        }
        yield event.plain_result(f"{buttons}")
```

astrbot_plugin_buttons插件会在消息发送前，自动将消息中的按钮字典buttons转化成按钮数据包来发送

### 示例图

![6de3babc31643ab4c0469fa3c6997f5](https://github.com/user-attachments/assets/3642866f-8686-4d6f-8a1d-0bc073869a00)


## 🤝 TODO

- [x] 支持发回调按钮
- [x] 支持发链接按钮
- [x] 为其他插件提供发按钮服务

## 👥 贡献指南

- 🌟 Star 这个项目！（点右上角的星星，感谢支持！）
- 🐛 提交 Issue 报告问题
- 💡 提出新功能建议
- 🔧 提交 Pull Request 改进代码

## 📌 注意事项

- 本插件利用napcat发包接口实现发送按钮，故仅支持napcat。
- 按钮仅在QQ 9.1.55以上版本可见。
- 功能仅限内部交流与小范围使用，请勿滥用。
- 本插件仅供学习交流，使用此插件产生的一切后果由使用者承担。
- 想第一时间得到反馈的可以来作者的插件反馈群（QQ群）：460973561

## 🤝 特别感谢

感谢TianRu大佬的开源的发包代码: [https://github.com/HDTianRu/Packet-plugin](https://github.com/HDTianRu/Packet-plugin)

感谢tinkerbellqwq大佬的初步迁移: [https://github.com/tinkerbellqwq/astrbot_plugin_button](https://github.com/tinkerbellqwq/astrbot_plugin_button)
