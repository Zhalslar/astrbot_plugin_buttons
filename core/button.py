import uuid
import random
from .packet_utils import process_json
from .protobuf import Protobuf


class ButtonBuilder:
    def __init__(self, config):
        # 解析按钮样式代码（例如 "5.间隔加深" => "5"）
        self.default_style_code: str = (
            config.get("default_style", "1.全部不加深").split(".", 1)[0].strip()
        )
        # 是否仅管理员可点击按钮
        self.default_only_admin: bool = config.get("default_only_admin", False)

        # 默认允许操作的用户 ID 列表（仅在 only_admin 为 False 时生效）
        self.default_allow_users: list[int] = config.get("default_allow_users", [])

        # 默认允许的身份组（频道专用, 仅在 only_admin 为 False 时生效）
        self.default_allow_roles: list[int] = config.get("default_allow_roles", [])

        # 默认是否点击即发送
        self.default_enter: bool = config.get("default_enter", True)

        # 默认是否引用回复原消息
        self.default_reply: bool = config.get("default_reply", False)

    def build(
        self,
        keyboard: list[list[dict]],
        group_id: int | None,
        user_id: int | None,
    ) -> str:
        buttons_data = self._make_buttons_data(keyboard)
        button_payload = self._build_button_payload(buttons_data)

        if group_id:
            target_type = "2"
            target_id = group_id
        elif user_id:
            target_type = "1"
            target_id = user_id
        else:
            raise ValueError("群ID和用户ID不能同时为 None")

        packet = {
            "1": {target_type: {"1": target_id}},
            "2": {"1": 1, "2": 0, "3": 0},
            "3": {"1": {"2": [button_payload]}},
            "4": random.getrandbits(32),
            "5": random.getrandbits(32),
        }
        return Protobuf.encode(process_json(packet)).hex()

    def _make_buttons_data(self, keyboard: list[list[dict]]) -> list[list[dict]]:
        result = []
        for row_idx, row in enumerate(keyboard):
            rendered_row = []
            for col_idx, info in enumerate(row):
                btn = self._build_button(info, row_idx, col_idx)
                if btn:
                    rendered_row.append(btn)
            result.append(rendered_row)
        return result

    def _build_button(self, info: dict, row: int, col: int) -> dict:
        label = info.get("label", "").strip()
        if not label:
            return {}

        visited_label = info.get("visited_label", f"{label}✔")
        btn_id = info.get("id", str(uuid.uuid4()))
        appid = info.get("appid", 102089849)
        light = info.get("light", None)
        if light is not None:
            style = 1 if light else 0
        else:
            style = self._select_style("link" in info, row, col)


        # 自定义 render_data 覆盖默认值
        render_data = {
            "label": label,
            "visited_label": visited_label,
            "style": style,
            **info.get("extra_render", {}),
        }

        # 构建 action
        if "link" in info:
            action_type = 0
            action_data = info["link"]
        elif "callback" in info:
            action_type = 2
            action_data = info["callback"]
        else:
            return {}

        # 权限处理：扁平字段转结构化 permission
        if info.get("only_admin") or self.default_only_admin:
            permission = {"type": 1}
        elif "allow_users" in info or self.default_allow_users:
            uids = info.get("allow_users") or self.default_allow_users
            permission = {
                "type": 0,
                "specify_user_ids": [str(uid) for uid in uids],
            }
        elif "allow_roles" in info or self.default_allow_roles:
            uids = info.get("allow_roles") or self.default_allow_roles
            permission = {
                "type": 3,
                "specify_role_ids": [str(rid) for rid in uids],
            }
        else:
            permission = {"type": 2}

        action = {
            "type": action_type,
            "permission": permission,
            "data": action_data,
            "enter": info.get("enter", self.default_enter),
            "reply": info.get("reply", self.default_reply),
            **info.get("extra_action", {}),
        }

        return {
            "id": btn_id,
            "render_data": render_data,
            "action": action,
            "appid": appid,
        }

    def _select_style(self, link: bool, row: int, col: int) -> int:
        match self.default_style_code:
            case "1":
                return 0
            case "2":
                return 1
            case "3":
                return random.choice([0, 1])
            case "4":
                return 1 if link else 0
            case "5":
                return (
                    1
                    if (row % 2 == 0 and col % 2 == 1)
                    or (row % 2 == 1 and col % 2 == 0)
                    else 0
                )
            case _:
                return 1

    def _build_button_payload(self, buttons_data: list[list[dict]]) -> dict:
        rows = []
        for line in buttons_data:
            row = []
            for button in line:
                row.append(
                    {
                        "1": button["id"],
                        "2": {
                            "1": button["render_data"]["label"],
                            "2": button["render_data"]["visited_label"],
                            "3": button["render_data"]["style"],
                        },
                        "3": {
                            "1": button["action"]["type"],
                            "2": {
                                "1": button["action"]["permission"]["type"],
                                "2": button["action"]["permission"].get(
                                    "specify_role_ids", []
                                ),
                                "3": button["action"]["permission"].get(
                                    "specify_user_ids", []
                                ),
                            },
                            "4": "err",
                            "5": button["action"]["data"],
                            "7": 1 if button["action"].get("reply") else 0,
                            "8": 1 if button["action"].get("enter") else 0,
                        },
                    }
                )
            rows.append({"1": row})
        return {
            "53": {
                "1": 46,
                "2": {"1": {"1": rows, "2": "1145140000"}},
                "3": 1,
            }
        }
