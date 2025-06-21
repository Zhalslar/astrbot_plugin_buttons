import os
from typing import Union
from aiocqhttp import CQHttp
from astrbot.api.star import Context, Star, register
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)
from astrbot.api.event import filter
from astrbot.core.star.star_tools import StarTools
from .core.button import ButtonBuilder
from .core.storage import ButtonStorage
from astrbot import logger


@register(
    "astrbot_plugin_buttons",
    "Zhalslar",
    "[仅napcat] 让QQ的野生bot也能发送按钮！",
    "2.0.0",
    "https://github.com/Zhalslar/astrbot_plugin_buttons",
)
class ButtonPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)

        plugin_data_dir = StarTools.get_data_dir("astrbot_plugin_buttons")
        buttons_data_file = os.path.join(plugin_data_dir, "buttons_data.json")
        self.storage = ButtonStorage(buttons_data_file)
        self.builder = ButtonBuilder(config)  # type: ignore

    @filter.command("按钮", alias={"button", "bt"})
    async def button_command(
        self, event: AiocqhttpMessageEvent, label="点击", callback="我是笨蛋"
    ):
        "发送一个简单的回调按钮"
        await self.send_callback_button(
            client=event.bot,
            buttons={label: callback},
            group_id=int(event.get_group_id()),
            user_id=int(event.get_sender_id()),
        )
        event.stop_event()

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_message(self, event: AiocqhttpMessageEvent):
        """监听消息，触发按钮"""
        for key in self.storage.keys_set:
            if key in event.message_str:
                if keyboard := self.storage.get(key):
                    await self.send_button(
                        client=event.bot,
                        keyboard=keyboard,
                        group_id=int(event.get_group_id()),
                        user_id=int(event.get_sender_id()),
                    )
                    logger.debug(f"尝试发送的按钮数据：{keyboard}")
                    event.stop_event()

    async def send_button(
        self,
        client: CQHttp,
        keyboard: list[list[dict]],
        group_id: Union[int, str, None] = None,
        user_id: Union[int, str, None] = None,
    ) -> None:
        """
        通用按钮发送函数（供插件/模块调用，支持 Napcat）。

        参数：
            client: CQHttp 实例
            keyboard: 二维按钮结构，每行一个列表
            group_id: 群 ID（优先使用）
            user_id: 用户 ID（群 ID 不存在时使用）

        示例：
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

            await send_button(client, keyboard, group_id=12345678)
        """
        if group_id is None and user_id is None:
            raise ValueError("群ID和用户ID不能同时为 None")

        pb_hex = self.builder.build(
            keyboard=keyboard,
            group_id=int(group_id) if group_id else None,
            user_id=int(user_id) if user_id else None,
        )
        await client.api.call_action(
            "send_packet", cmd="MessageSvc.PbSendMsg", data=pb_hex
        )

    async def send_callback_button(
        self,
        client: CQHttp,
        buttons: dict[str, str],
        group_id: Union[int, str, None] = None,
        user_id: Union[int, str, None] = None,
        per_row: int = 3,
    ) -> None:
        """
        快速发送 callback 类型按钮，仅需提供 label → callback 映射。

        示例：
            await send_callback_button(client, {
                "模型": "model",
                "插件": "plugin",
                "重置": "reset"
            }, group_id=123)
        """
        keyboard = self._dict_to_keyboard(buttons, field="callback", per_row=per_row)
        await self.send_button(client, keyboard, group_id=group_id, user_id=user_id)

    async def send_link_button(
        self,
        client: CQHttp,
        buttons: dict[str, str],
        group_id: Union[int, str, None] = None,
        user_id: Union[int, str, None] = None,
        per_row: int = 3,
    ) -> None:
        """
        快速发送 link 类型按钮，仅需提供 label → URL 映射。

        示例：
            await send_link_buttons(client, {
                "官网": "https://example.com",
                "文档": "https://docs.example.com"
            }, group_id=123)
        """
        keyboard = self._dict_to_keyboard(buttons, field="link", per_row=per_row)
        await self.send_button(client, keyboard, group_id=group_id, user_id=user_id)

    @staticmethod
    def _dict_to_keyboard(
        mapping: dict[str, str], field: str, per_row: int = 3
    ) -> list[list[dict]]:
        """将 {label: value} 字典转换为 keyboard 列表结构"""
        items = list(mapping.items())
        keyboard = []
        for i in range(0, len(items), per_row):
            row = [{"label": k, field: v} for k, v in items[i : i + per_row]]
            keyboard.append(row)
        return keyboard
