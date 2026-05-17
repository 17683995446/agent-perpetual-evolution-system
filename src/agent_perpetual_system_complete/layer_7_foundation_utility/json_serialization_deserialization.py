"""
JSON Serialization Deserialization - JSON序列化反序列化工具（4个单词）

提供JSON数据的序列化和反序列化功能。
文件名包含4个单词，非常清晰明了。
"""

import json
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, date
from pathlib import Path


class JSONSerializationDeserialization:
    """
    JSON序列化反序列化工具类

    提供JSON数据的序列化、反序列化、文件读写等功能。
    """

    @staticmethod
    def serialize_object_to_json_string(
        data: Any,
        indent: Optional[int] = 2,
        ensure_ascii: bool = False
    ) -> str:
        """
        将Python对象序列化为JSON字符串

        参数:
            data: 要序列化的Python对象
            indent: 缩进空格数，None 表示压缩格式
            ensure_ascii: 是否确保ASCII

        返回:
            JSON格式字符串
        """
        return json.dumps(
            data,
            indent=indent,
            ensure_ascii=ensure_ascii,
            default=JSONSerializationDeserialization._default_serialization_handler
        )

    @staticmethod
    def deserialize_json_string_to_object(json_string: str) -> Any:
        """
        将JSON字符串反序列化为Python对象

        参数:
            json_string: JSON格式字符串

        返回:
            Python对象
        """
        return json.loads(json_string)

    @staticmethod
    def write_data_to_json_file(
        data: Any,
        file_path: Union[str, Path],
        indent: Optional[int] = 2,
        ensure_ascii: bool = False
    ) -> None:
        """
        将Python对象写入JSON文件

        参数:
            data: 要写入的Python对象
            file_path: 文件路径
            indent: 缩进空格数
            ensure_ascii: 是否确保ASCII
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(
                data,
                f,
                indent=indent,
                ensure_ascii=ensure_ascii,
                default=JSONSerializationDeserialization._default_serialization_handler
            )

    @staticmethod
    def read_data_from_json_file(file_path: Union[str, Path]) -> Any:
        """
        从JSON文件读取数据并反序列化

        参数:
            file_path: 文件路径

        返回:
            反序列化后的Python对象
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def try_deserialize_json_string(json_string: str, default_value: Any = None) -> Any:
        """
        尝试反序列化JSON字符串，失败返回默认值

        参数:
            json_string: JSON字符串
            default_value: 失败时的默认值

        返回:
            反序列化的对象或默认值
        """
        try:
            return json.loads(json_string)
        except (json.JSONDecodeError, TypeError):
            return default_value

    @staticmethod
    def safe_serialize_object_to_string(data: Any, default_value: str = "{}") -> str:
        """
        安全地将对象序列化为JSON字符串，失败返回默认值

        参数:
            data: 要序列化的对象
            default_value: 失败时的默认值

        返回:
            JSON字符串或默认值
        """
        try:
            return json.dumps(
                data,
                ensure_ascii=False,
                default=JSONSerializationDeserialization._default_serialization_handler
            )
        except (TypeError, ValueError):
            return default_value

    @staticmethod
    def _default_serialization_handler(obj: Any) -> Any:
        """
        默认的序列化处理器，处理无法直接序列化的对象

        参数:
            obj: 要序列化的对象

        返回:
            可序列化的表示
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        if hasattr(obj, 'to_dict'):
            return obj.to_dict()

        if hasattr(obj, '__dict__'):
            return obj.__dict__

        return str(obj)

    @staticmethod
    def format_json_string_prettily(json_string: str, indent: int = 2) -> str:
        """
        格式化JSON字符串，使其更易读

        参数:
            json_string: 原始JSON字符串
            indent: 缩进空格数

        返回:
            格式化后的JSON字符串
        """
        data = json.loads(json_string)
        return json.dumps(data, indent=indent, ensure_ascii=False)

    @staticmethod
    def merge_multiple_json_objects(*json_objects: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并多个JSON对象（字典）

        参数:
            *json_objects: 要合并的字典对象

        返回:
            合并后的字典
        """
        result = {}
        for json_obj in json_objects:
            if isinstance(json_obj, dict):
                result.update(json_obj)
        return result

    @staticmethod
    def extract_value_from_json(json_data: Dict[str, Any], key_path: str, default_value: Any = None) -> Any:
        """
        从嵌套JSON对象中按路径提取值

        参数:
            json_data: JSON对象
            key_path: 点分隔的键路径，如 "a.b.c"
            default_value: 未找到时的默认值

        返回:
            提取的值或默认值
        """
        current = json_data
        keys = key_path.split('.')

        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default_value
            current = current[key]

        return current
