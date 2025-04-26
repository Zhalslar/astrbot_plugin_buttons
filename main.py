import uuid
import random
import string
from astrbot.api.star import Context, Star, register
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)
from astrbot.api.event import filter
from .proto import ProtobufEncoder


@register(
    "astrbot_plugin_buttons",
    "Zhalslar",
    "[仅napcat] 让QQ的野生bot也能发送按钮！",
    "1.0.0",
    "https://github.com/Zhalslar/astrbot_plugin_buttons",
)
class ButtonPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("按钮", alias={"button"})
    async def on_command(self, event: AiocqhttpMessageEvent, input: str | None = None):
        """发按钮"""
        # 默认按钮数据
        if not input:
            input = "千万别点:我是可爱小南梁~ (≧▽≦)"

        # 获取群聊ID和用户ID
        group_id = int(event.get_group_id())
        user_id = int(event.get_sender_id())

        # 处理输入
        input = input.replace("：", ":")
        input = input.replace("，", ",")
        inputs: list[str] = input.split(",")
        inputs_data: list[list[str]] = [args.split(":") for args in inputs]

        # 处理按钮数据
        buttons: list[dict[str, str]] = []
        for input_data in inputs_data:
            if len(input_data) == 2:
                buttons.append({"text": input_data[0], "callback": input_data[1]})
            else:
                yield event.plain_result("输入格式错误")
                return

        # 制作按钮
        buttons_data = []
        for button_info in buttons:
            if button_data := self.make_button(button_info):
                buttons_data.append(button_data)

        # 转化按钮数据
        buttons_data_ = [
            {
                "1": button_data["id"],  # 按钮 ID
                "2": {
                    "1": button_data["render_data"]["label"],  # 按钮文本
                    "2": button_data["render_data"]["visited_label"],  # 点击后的文本
                    "3": button_data["render_data"]["style"],  # 按钮样式
                },
                "3": {
                    "1": button_data["action"]["type"],  # 按钮类型
                    "2": {
                        "1": button_data["action"]["permission"]["type"],  # 权限类型
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
            for button_data in buttons_data
        ]

        # 构造按钮数据包
        button_packet = {
            "53": {
                "1": 46,
                "2": {
                    "1": {
                        "1": [
                            {
                                "1": buttons_data_,
                            }
                        ],
                        "2": "2936169201",
                    }
                },
                "3": 1,
            }
        }

        # 构造数据包
        packet = {
            "1": {"2" if group_id else "1": {"1": group_id if group_id else user_id}},
            "2": {"1": 1, "2": 0, "3": 0},
            "3": {"1": {"2": [button_packet]}},
            "4": random.getrandbits(32),
            "5": random.getrandbits(32),
        }

        # 处理数据包
        processed = self.process_json(packet)

        # 转为protobuf
        encoder = ProtobufEncoder()
        encoded_data = encoder.encode(processed)

        # 转为16进制
        hex_string = encoded_data.hex()

        # 调用napcat的send_packet接口进行发包
        payload = {"cmd": "MessageSvc.PbSendMsg", "data": hex_string}
        await event.bot.api.call_action("send_packet", **payload)
        event.stop_event()

    @staticmethod
    def make_button(info: dict) -> dict | None:
        """制作按钮"""
        text = info.get("text", "")
        clicked_text = info.get("clicked_text", "")
        link = info.get("link")
        callback = info.get("callback")

        # 构建基础消息结构
        button_data = {
            "id": str(uuid.uuid4()),  # 生成唯一 ID
            "render_data": {
                "label": text,  # 按钮文本
                "visited_label": clicked_text,  # 点击后的文本
                "style": random.choice([0, 1]),  # 按钮样式
                **info.get("QQBot", {}).get(
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
                **info.get("QQBot", {}).get("action", {}),  # 扩展 QQBot 的 action 属性
            }
        elif callback:
            button_data["action"] = {
                "type": 2,  # 回调类型
                "permission": {"type": 2},
                "data": callback,  # 回调数据
                "enter": True,  # 回车键行为
                **info.get("QQBot", {}).get("action", {}),  # 扩展 QQBot 的 action 属性
            }
        else:
            return None  # 如果按钮类型未知，返回 False

        return button_data

    @staticmethod
    def is_hex_string(s):
        """判断是否为16进制字符串"""
        if len(s) % 2 != 0:
            return False
        hex_chars = set(string.hexdigits)
        return all(c.lower() in hex_chars for c in s)

    def process_json(self, data, path=None):
        """处理JSON数据包"""
        if path is None:
            path = []
        if isinstance(data, dict):
            result = {}
            for key in data:
                num_key = int(key)
                current_path = path + [str(key)]
                value = data[key]
                processed_value = self.process_json(value, current_path)
                result[num_key] = processed_value
            return result
        elif isinstance(data, list):
            return [
                self.process_json(item, path + [str(i + 1)])
                for i, item in enumerate(data)
            ]
        elif isinstance(data, str):
            if len(path) >= 2 and path[-2:] == ["5", "2"] and self.is_hex_string(data):
                return bytes.fromhex(data)
            if data.startswith("hex->"):
                hex_part = data[5:]
                if self.is_hex_string(hex_part):
                    return bytes.fromhex(hex_part)
                else:
                    return data
            else:
                return data
        else:
            return data
