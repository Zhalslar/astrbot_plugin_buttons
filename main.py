import ast
import uuid
import random
import string

from aiocqhttp import CQHttp
from astrbot.api.star import Context, Star, register
from astrbot.core.config.astrbot_config import AstrBotConfig
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)
import astrbot.api.message_components as Comp
from astrbot.api.event import filter
from .proto import ProtobufEncoder


@register(
    "astrbot_plugin_buttons",
    "Zhalslar",
    "[仅napcat] 让QQ的野生bot也能发送按钮！",
    "1.0.1",
    "https://github.com/Zhalslar/astrbot_plugin_buttons",
)
class ButtonPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.encoder = ProtobufEncoder()
        self.button_style = config.get("button_style", "1")  # 按钮样式
        self.default_button_input: str = config.get(
            "default_button_input", "菜单-help"
        )  # 默认按钮数据

    @filter.command("按钮", alias={"button"})
    async def on_command(self, event: AiocqhttpMessageEvent, input: str | None = None):
        """发按钮，input为按钮数据，格式为：按钮文本-按钮回调/n按钮文本-按钮回调"""
        # 默认按钮数据
        if not input:
            input = self.default_button_input

        # 处理输入数据
        input = input.replace("，", ",")
        input = input.replace("～", "~")

        # 录入按钮信息
        buttons_info: list[list[dict]] = []

        for line in input.split("|"):  # 按行分割
            line_buttons: list[dict] = []

            for element in line.split(","):  # 按逗号分割每行的按钮
                if "~" in element:  # 链接按钮格式
                    label, link = element.split("~", 1)
                    line_buttons.append({"label": label, "link": link})
                elif "-" in element:  # 回调按钮格式
                    label, callback = element.split("-", 1)
                    line_buttons.append({"label": label, "callback": callback})
                else:
                    yield event.plain_result(f"无效的按钮格式: {element}")
                    return

            buttons_info.append(line_buttons)
            print(buttons_info)

        client = event.bot
        group_id = event.get_group_id()
        user_id = event.get_sender_id()
        await self.send_button(client, buttons_info, group_id, user_id)
        event.stop_event()

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AiocqhttpMessageEvent):
        """
        监听消息中的按钮发送事件，并发送按钮，按钮消息结构示例如下（字符串型字典）
        {
            "type": "button",
            "content": [
                [
                    {"label": "点我", "callback": "我是笨蛋"},
                    {"label": "点他", "callback": "我是小男娘"},
                ],
                [
                    {"label": "点她", "callback": "看看腿"},
                    {"label": "点你", "link": "看看玉足"},
                ],
            ],
        }
        """
        chain = event.get_result().chain
        seg = chain[0]
        # 仅允许只含有单条文本的消息链通过
        if not (len(chain) == 1 and isinstance(seg, Comp.Plain)):
            return
        # 将字符串转换为字典
        try:
            extracted_dict = ast.literal_eval(seg.text)
        except (ValueError, SyntaxError):
            return
        # 检测type键值是否为button
        if extracted_dict.get("type") != "button":
            return
        buttons_info = extracted_dict.get("content", [])
        client = event.bot
        group_id = event.get_group_id()
        user_id = event.get_sender_id()
        await self.send_button(client, buttons_info, group_id, user_id)
        chain.clear()  # 清空消息段
        event.stop_event()

    async def send_button(
        self,
        client: CQHttp,
        buttons_info: list[list[dict]],
        group_id: int | str | None,
        user_id: int | str | None,
    ) -> str | None:
        """发按钮，buttons_info为按钮数据"""

        # 检查信息格式
        for line in buttons_info:
            for button_info in line:
                # 确保是字典，并且包含 "label" 和 "callback" 或 "link"
                if (
                    not isinstance(button_info, dict)
                    or "label" not in button_info
                    or ("callback" not in button_info and "link" not in button_info)
                    or not button_info["label"]
                    or not (button_info.get("callback") or button_info.get("link"))
                ):
                    return "输入格式错误"

        # 制作按钮, 将 buttons_info 转化为 buttons_data
        buttons_data: list[list[dict]] = [
            [
                button_data
                for button_info in line
                if (button_data := self._make_button(button_info)) is not None
            ]
            for line in buttons_info
        ]

        # 转化按钮数据
        buttons_data_ = [
            {
                "1": [
                    {
                        "1": button_data["id"],  # 按钮 ID
                        "2": {
                            "1": button_data["render_data"]["label"],  # 按钮文本
                            "2": button_data["render_data"][
                                "visited_label"
                            ],  # 点击后的文本
                            "3": button_data["render_data"]["style"],  # 按钮样式
                        },
                        "3": {
                            "1": button_data["action"]["type"],  # 按钮类型
                            "2": {
                                "1": button_data["action"]["permission"][
                                    "type"
                                ],  # 权限类型
                                "2": button_data["action"]["permission"].get(
                                    "specify_role_ids", []
                                ),  # 指定角色 ID
                                "3": button_data["action"]["permission"].get(
                                    "specify_user_ids", []
                                ),  # 指定用户 ID
                            },
                            "4": "err",  # 错误信息
                            "5": button_data["action"]["data"],  # 按钮数据
                            "7": 1
                            if button_data["action"].get("reply", False)
                            else 0,  # 回复行为
                            "8": 1
                            if button_data["action"].get("enter", False)
                            else 0,  # 回车键行为
                        },
                    }
                    for button_data in lines
                ]
            }
            for lines in buttons_data
        ]

        # 构造按钮数据包
        button_packet = {
            "53": {
                "1": 46,
                "2": {
                    "1": {
                        "1": buttons_data_,
                        "2": "1145140000",
                    }
                },
                "3": 1,
            }
        }

        # 构造数据包
        packet = {
            "1": {
                "2" if group_id else "1": {
                    "1": int(group_id) if group_id else int(user_id)  # type: ignore
                }
            },  # type: ignore
            "2": {"1": 1, "2": 0, "3": 0},
            "3": {"1": {"2": [button_packet]}},
            "4": random.getrandbits(32),  # 需要保证唯一性，每个数据包都应该用不同的值
            "5": random.getrandbits(32),  # 同上
        }

        # 处理JSON数据包
        processed = self._process_json(packet)

        # 转为protobuf
        encoded_data = self.encoder.encode(processed)

        # 转为16进制
        hex_string = encoded_data.hex()

        # 调用napcat的send_packet接口进行发包
        payload = {"cmd": "MessageSvc.PbSendMsg", "data": hex_string}
        await client.api.call_action("send_packet", **payload)

    def _make_button(self, button_info: dict) -> dict:
        """制作按钮"""
        label = button_info.get("label", "").strip()
        clicked_text = button_info.get("clicked_text", "").strip()
        link = button_info.get("link")
        callback = button_info.get("callback")

        if "0" in self.button_style:
            button_style = 0
        elif "1" in self.button_style:
            button_style = 1
        elif "2" in self.button_style:
            button_style = random.choice([0, 1])
        elif "3" in self.button_style and link:
            button_style = 1
        else:
            button_style = 1

        # 构建基础消息结构
        button_data = {
            "id": str(uuid.uuid4()),  # 生成唯一 ID
            "render_data": {
                "label": label,  # 按钮文本
                "visited_label": clicked_text,  # 点击后的文本
                "style": button_style,  # 按钮样式
                **button_info.get("QQBot", {}).get(
                    "render_data", {}
                ),  # 扩展 QQBot 的 render_data 属性
            },
            "appid": 102089849,  # 应用 ID
        }

        # 根据按钮类型构建 action 属性
        if link:
            button_data["action"] = {
                "type": 0,  # 链接类型
                "permission": {"type": 2},
                "data": link,  # 链接地址
                **button_info.get("QQBot", {}).get(
                    "action", {}
                ),  # 扩展 QQBot 的 action 属性
            }
        elif callback:
            button_data["action"] = {
                "type": 2,  # 回调类型
                "permission": {"type": 2},
                "data": callback,  # 回调数据
                "enter": True,  # 回车键行为
                **button_info.get("QQBot", {}).get(
                    "action", {}
                ),  # 扩展 QQBot 的 action 属性
            }
        else:
            return {}  # 如果既没有链接也没有回调，则返回空字典

        return button_data

    @staticmethod
    def _is_hex_string(s):
        """判断是否为16进制字符串"""
        if len(s) % 2 != 0:
            return False
        hex_chars = set(string.hexdigits)
        return all(c.lower() in hex_chars for c in s)

    def _process_json(self, data, path=None):
        """处理JSON数据包"""
        if path is None:
            path = []
        if isinstance(data, dict):
            result = {}
            for key in data:
                num_key = int(key)
                current_path = path + [str(key)]
                value = data[key]
                processed_value = self._process_json(value, current_path)
                result[num_key] = processed_value
            return result
        elif isinstance(data, list):
            return [
                self._process_json(item, path + [str(i + 1)])
                for i, item in enumerate(data)
            ]
        elif isinstance(data, str):
            if len(path) >= 2 and path[-2:] == ["5", "2"] and self._is_hex_string(data):
                return bytes.fromhex(data)
            if data.startswith("hex->"):
                hex_part = data[5:]
                if self._is_hex_string(hex_part):
                    return bytes.fromhex(hex_part)
                else:
                    return data
            else:
                return data
        else:
            return data
