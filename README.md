
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

本插件利用napcat进行发包，实现了让野生bot发送QQ按钮(QQ 9.1.55以上可见)，同时为其他astrbot插件提供易用的发按钮接口。

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

# 控制台重启AstrBot
```

## ⌨️ 使用说明

### 指令调用

打开"data\plugin_data\astrbot_plugin_buttons\buttons_data.json", 按照模板添加按钮数据，键名为按钮名称，键值为按钮内容，键名会被注册成命令来触发这个按钮。

### 外部插件插件调用示例

```bash
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("点歌")
    async song(self, event: AstrMessageEvent):
        """发送按钮进行选歌"""
        keyboard = [
                [
                    {
                        "label": "第1行",            # 按钮文字
                        "callback": "第1行第1个按钮", # 命令型按钮
                        "light": True,              # 是否高亮按钮（默认根据配置选）
                        "only_admin": True,         # 仅管理员可操作（默认 False）
                        "allow_users": [123],       # 指定用户可操作（仅only_admin为False时生效）
                        "allow_roles": [456],       # 指定身份组（仅频道可用）
                        "enter": True,              # 点击是否直接发送（默认 True）
                        "reply": False              # 是否引用回复（默认 False）
                    },
                    {
                        "label": "第1行",
                        "callback": "第1行第2个按钮"
                    }
                ],
                [
                    {
                        "label": "第2行",
                        "link": "https://example.com"
                    }
                ]
            ]
        await self.send_button(event, keyboard)


     async def send_button(
        self, event: AiocqhttpMessageEvent, keyboard: list[list[dict[str, str]]]
    ) -> str | None:
        """调用buttons插件发送按钮"""
        button_plugin = self.context.get_registered_star("astrbot_plugin_buttons")
        if button_plugin.activated:
            cls = button_plugin.star_cls
            await cls.send_button(  # type: ignore
                client=event.bot,
                keyboard=keyboard,
                group_id=event.get_group_id(),
                user_id=event.get_sender_id(),
            )
        else:
            await event.send(
                event.plain_result(
                    "astrbot_plugin_buttons插件未激活，无法调用按钮发送服务"
                )
            )
            return
```

astrbot_plugin_buttons插件会在消息发送前，自动将消息中的按钮字典buttons转化成字典来发送

### 示例图



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
- 想第一时间得到反馈的可以来作者的插件反馈群（QQ群）：460973561（不点star不给进）

## 🤝 特别感谢

感谢TianRu大佬的开源的发包代码: [https://github.com/HDTianRu/Packet-plugin](https://github.com/HDTianRu/Packet-plugin)

感谢tinkerbellqwq大佬的初步迁移: [https://github.com/tinkerbellqwq/astrbot_plugin_button](https://github.com/tinkerbellqwq/astrbot_plugin_button)
