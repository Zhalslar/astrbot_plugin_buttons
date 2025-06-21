import json
from typing import Dict, List, Optional, Any


class ButtonStorage:
    """
    按钮配置管理类，仅管理键名和对应值的存取，
    不对值的数据结构做任何约束和处理。

    操作内存数据后会自动同步保存到 JSON 文件。
    """

    def __init__(self, json_path: str):
        """
        初始化并尝试从指定 JSON 文件加载数据，失败时存储为空字典。

        :param json_path: JSON 文件路径
        """
        self.json_path = json_path
        self._storage = self._load_or_create_file(json_path)

    def _load_or_create_file(self, path: str) -> Dict[str, Any]:
        """
        尝试加载 JSON 文件，文件不存在时自动创建空字典文件。

        :param path: JSON 文件路径
        :return: 文件中加载的字典数据或空字典
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("配置文件内容必须是字典")
            return data
        except FileNotFoundError:
            # 文件不存在，创建空字典文件
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            return {}
        except (json.JSONDecodeError, ValueError):
            # 文件内容错误，返回空字典（不覆盖文件）
            return {}

    def add(self, name: str, value: Any) -> None:
        """
        添加或更新指定键及其对应数据，操作后自动保存。

        :param name: 键名
        :param value: 键对应的任意数据
        """
        self._storage[name] = value
        self.save()

    def get(self, name: str) -> Optional[Any]:
        """
        获取指定键对应的数据，找不到返回 None。

        :param name: 键名
        :return: 键对应数据或 None
        """
        return self._storage.get(name)

    def remove(self, name: str) -> bool:
        """
        删除指定键及其对应的数据，操作后自动保存。

        :param name: 键名
        :return: 删除成功返回 True，键不存在返回 False
        """
        if name in self._storage:
            del self._storage[name]
            self.save()
            return True
        return False

    def all(self) -> Dict[str, Any]:
        """
        获取所有键值对。

        :return: 当前所有存储的数据字典
        """
        return self._storage

    def names(self) -> List[str]:
        """
        获取所有键名列表。

        :return: 键名列表
        """
        return list(self._storage.keys())

    def get_first(self) -> Optional[Any]:
        """
        获取存储中第一个键对应的值，如果为空返回 None。
        """
        if not self._storage:
            return None
        first_key = next(iter(self._storage))
        return self._storage[first_key]

    def save(self, path: Optional[str] = None) -> None:
        """
        保存当前存储数据到 JSON 文件。

        :param path: 保存路径，默认使用初始化时的文件路径
        """
        save_path = path or self.json_path
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self._storage, f, ensure_ascii=False, indent=2)

    @property
    def keys_set(self) -> set[str]:
        """
        对外公开的键名集合，方便做关键词匹配等。

        :return: 当前所有键名集合
        """
        return set(self._storage.keys())

    def __getitem__(self, name: str) -> Any:
        """
        支持通过 [] 访问数据，键不存在时抛 KeyError。

        :param name: 键名
        :return: 键对应数据
        """
        return self._storage[name]

    def __contains__(self, name: str) -> bool:
        """
        判断是否存在指定键。

        :param name: 键名
        :return: 是否存在
        """
        return name in self._storage
