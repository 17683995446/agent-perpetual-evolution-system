"""
Collection Operation Utility - 集合操作工具（4个单词）

提供各种集合（列表、字典等）操作和处理的工具函数。
文件名包含4个单词，非常清晰明了。
"""

from typing import List, Dict, Set, Tuple, Any, Optional, Callable, TypeVar


T = TypeVar('T')


class CollectionOperationUtility:
    """
    集合操作工具类

    提供列表、字典、集合等容器的处理和操作功能。
    """

    @staticmethod
    def remove_duplicates_from_list(input_list: List[T]) -> List[T]:
        """
        从列表中移除重复元素，保持原顺序

        参数:
            input_list: 输入列表

        返回:
            无重复元素的列表
        """
        seen = set()
        result = []
        for item in input_list:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    @staticmethod
    def merge_multiple_dictionaries(*dictionaries: Dict) -> Dict:
        """
        合并多个字典，后面的字典会覆盖前面的

        参数:
            *dictionaries: 要合并的字典

        返回:
            合并后的字典
        """
        result = {}
        for dict_data in dictionaries:
            result.update(dict_data)
        return result

    @staticmethod
    def split_list_into_chunks(input_list: List[T], chunk_size: int) -> List[List[T]]:
        """
        将列表分成指定大小的块

        参数:
            input_list: 输入列表
            chunk_size: 每个块的大小

        返回:
            包含块的列表
        """
        if chunk_size <= 0:
            return [input_list]

        return [
            input_list[i:i + chunk_size]
            for i in range(0, len(input_list), chunk_size)
        ]

    @staticmethod
    def filter_list_by_predicate(
        input_list: List[T],
        predicate: Callable[[T], bool]
    ) -> List[T]:
        """
        根据谓词函数过滤列表

        参数:
            input_list: 输入列表
            predicate: 判断函数，返回 True 表示保留该元素

        返回:
            过滤后的列表
        """
        return [item for item in input_list if predicate(item)]

    @staticmethod
    def get_intersection_of_lists(*lists: List) -> List:
        """
        获取多个列表的交集

        参数:
            *lists: 要取交集的列表

        返回:
            所有列表共有的元素列表
        """
        if not lists:
            return []

        common_elements = set(lists[0])
        for lst in lists[1:]:
            common_elements.intersection_update(lst)

        return list(common_elements)

    @staticmethod
    def reverse_dictionary_keys_values(input_dict: Dict) -> Dict:
        """
        反转字典的键和值

        参数:
            input_dict: 输入字典

        返回:
            键值互换的字典
        """
        return {value: key for key, value in input_dict.items()}

    @staticmethod
    def sort_list_of_dictionaries(
        list_of_dicts: List[Dict],
        sort_key: str,
        reverse: bool = False
    ) -> List[Dict]:
        """
        根据字典的特定键排序字典列表

        参数:
            list_of_dicts: 字典列表
            sort_key: 排序的键
            reverse: 是否降序

        返回:
            排序后的字典列表
        """
        return sorted(
            list_of_dicts,
            key=lambda x: x.get(sort_key, ''),
            reverse=reverse
        )

    @staticmethod
    def find_first_match_in_list(
        input_list: List[T],
        predicate: Callable[[T], bool],
        default_value: Optional[T] = None
    ) -> Optional[T]:
        """
        在列表中查找第一个满足条件的元素

        参数:
            input_list: 输入列表
            predicate: 判断函数
            default_value: 未找到时的默认值

        返回:
            找到的元素或默认值
        """
        for item in input_list:
            if predicate(item):
                return item
        return default_value

    @staticmethod
    def partition_list_by_predicate(
        input_list: List[T],
        predicate: Callable[[T], bool]
    ) -> Tuple[List[T], List[T]]:
        """
        根据谓词函数将列表分为两部分

        参数:
            input_list: 输入列表
            predicate: 判断函数

        返回:
            包含两个列表的元组：(满足条件的, 不满足条件的)
        """
        matching = []
        not_matching = []

        for item in input_list:
            if predicate(item):
                matching.append(item)
            else:
                not_matching.append(item)

        return matching, not_matching

    @staticmethod
    def get_dictionary_safe_get(
        dictionary: Dict,
        key_path: str,
        default_value: Any = None
    ) -> Any:
        """
        安全地从嵌套字典中获取值，支持点分隔的路径

        参数:
            dictionary: 输入字典
            key_path: 点分隔的键路径，如 "a.b.c"
            default_value: 未找到时的默认值

        返回:
            获取到的值或默认值
        """
        current = dictionary
        keys = key_path.split('.')

        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default_value
            current = current[key]

        return current
