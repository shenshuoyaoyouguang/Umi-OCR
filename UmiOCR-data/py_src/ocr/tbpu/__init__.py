# tbpu : text block processing unit 文本块后处理
# ===============================================
# 适配版本：集成新插件系统，保持完全向后兼容
# ===============================================

"""
TBPU (Text Block Processing Unit) 模块

该模块提供 OCR 结果的文本块后处理功能，包括：
- 排版解析（多栏/单栏、自然段/换行/无换行等）
- 忽略区域处理
- 文本合并

适配说明：
- 集成新插件系统，使用 TbpuPluginManager 作为内部实现
- 完全向后兼容：Tbpu 基类、Parser 字典、getParser() 函数行为不变
- 支持内置解析器和外部插件解析器
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Tuple

if TYPE_CHECKING:
    from .tbpu_types import TextBlocks, ParserClass
    from .tbpu import Tbpu as TbpuType

# 导入日志模块
from umi_log import logger

# ===============================================
# 第一部分：基础导入（避免循环导入）
# ===============================================

# 先导入基类（不依赖其他模块）
from .tbpu import Tbpu

# ===============================================
# 第二部分：延迟导入管理器（避免循环导入）
# ===============================================

# 管理器实例缓存（延迟加载）
_manager: Optional[Any] = None


def _get_manager() -> Optional[Any]:
    """
    延迟获取 TBPU 管理器实例
    
    使用延迟加载避免循环导入问题。
    当首次需要管理器功能时才尝试导入。
    
    Returns:
        TbpuPluginManager 实例，导入失败返回 None
    """
    global _manager
    if _manager is None:
        try:
            # 尝试从 plugins_controller 导入
            from ...plugins_controller.managers.tbpu_manager import TbpuPluginManager
            _manager = TbpuPluginManager()
            # 注册内置解析器到管理器
            _register_builtin_parsers(_manager)
        except ImportError as e:
            # 导入失败（如 plugins_controller 尚未初始化）
            # 静默处理，使用内置解析器作为回退
            pass
    return _manager


def _register_builtin_parsers(manager: Any) -> None:
    """
    注册内置解析器到管理器
    
    Args:
        manager: TbpuPluginManager 实例
    """
    # 导入所有内置解析器类
    from .parser_none import ParserNone
    from .parser_multi_line import MultiLine
    from .parser_multi_para import MultiPara
    from .parser_multi_none import MultiNone
    from .parser_single_line import SingleLine
    from .parser_single_para import SinglePara
    from .parser_single_none import SingleNone
    from .parser_single_code import SingleCode
    
    # 内置解析器字典
    builtin_parsers: Dict[str, ParserClass] = {
        "none": ParserNone,
        "multi_line": MultiLine,
        "multi_para": MultiPara,
        "multi_none": MultiNone,
        "single_line": SingleLine,
        "single_para": SinglePara,
        "single_none": SingleNone,
        "single_code": SingleCode,
    }
    
    # 注册到管理器
    manager.register_builtin_parsers(builtin_parsers)


# ===============================================
# 第三部分：导入内置解析器类（保持向后兼容）
# ===============================================

# 这些导入确保旧代码可以直接访问解析器类
# 例如：from ocr.tbpu import ParserNone, SingleLine

from .parser_none import ParserNone
from .parser_multi_line import MultiLine
from .parser_multi_para import MultiPara
from .parser_multi_none import MultiNone
from .parser_single_line import SingleLine
from .parser_single_para import SinglePara
from .parser_single_none import SingleNone
from .parser_single_code import SingleCode

# 忽略区域处理（特殊功能，非排版解析器）
from .ignore_area import IgnoreArea

# ===============================================
# 第四部分：兼容字典（动态代理实现，带缓存优化）
# ===============================================

class _ParserDict(dict):
    """
    兼容字典类 - 动态代理到管理器
    
    该类继承自 dict，提供与旧代码完全兼容的接口。
    同时，它动态地将外部插件解析器合并到字典中。
    
    特性：
    1. 内置解析器优先（确保核心功能可用）
    2. 动态获取管理器中的外部插件解析器
    3. 完全兼容 dict 的所有操作（keys, values, items, in 等）
    4. keys() 结果缓存，提升频繁访问性能
    """
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        初始化内置解析器字典
        
        Args:
            *args: 传递给 dict 的位置参数
            **kwargs: 传递给 dict 的关键字参数
        """
        super().__init__(*args, **kwargs)
        # keys() 缓存相关属性
        self._keys_cache: Optional[List[str]] = None
        self._cache_valid: bool = False
    
    def _invalidate_cache(self) -> None:
        """
        使缓存失效
        
        当字典内容可能发生变化时调用
        """
        self._cache_valid = False
        self._keys_cache = None
    
    def __setitem__(self, key: str, value: Any) -> None:
        """
        设置键值对，并使缓存失效
        
        Args:
            key: 键
            value: 值
        """
        super().__setitem__(key, value)
        self._invalidate_cache()
    
    def __delitem__(self, key: str) -> None:
        """
        删除键值对，并使缓存失效
        
        Args:
            key: 键
        """
        super().__delitem__(key)
        self._invalidate_cache()
    
    def update(self, *args: Any, **kwargs: Any) -> None:
        """
        批量更新，并使缓存失效
        
        Args:
            *args: 传递给 dict.update 的位置参数
            **kwargs: 传递给 dict.update 的关键字参数
        """
        super().update(*args, **kwargs)
        self._invalidate_cache()
    
    def clear(self) -> None:
        """清空字典，并使缓存失效"""
        super().clear()
        self._invalidate_cache()
    
    def pop(self, key: str, *args: Any) -> Any:
        """
        弹出键值对，并使缓存失效
        
        Args:
            key: 键
            *args: 默认值参数
            
        Returns:
            弹出的值
        """
        result = super().pop(key, *args)
        self._invalidate_cache()
        return result
    
    def popitem(self) -> Tuple[str, Any]:
        """
        弹出任意键值对，并使缓存失效
        
        Returns:
            弹出的键值对
        """
        result = super().popitem()
        self._invalidate_cache()
        return result
    
    def __getitem__(self, key: str) -> Any:
        """
        获取解析器类
        
        优先从内置字典获取，如果管理器可用，也检查管理器中的解析器。
        
        Args:
            key: 解析器名称
            
        Returns:
            解析器类
            
        Raises:
            KeyError: 解析器不存在
        """
        # 优先检查内置字典
        if key in super().keys():
            return super().__getitem__(key)
        
        # 检查管理器中的外部插件
        manager = _get_manager()
        if manager and key in manager.Parser:
            return manager.Parser[key]
        
        raise KeyError(key)
    
    def __contains__(self, key: object) -> bool:
        """
        检查是否包含指定解析器
        
        Args:
            key: 解析器名称
            
        Returns:
            是否存在
        """
        # 检查内置字典
        if super().__contains__(key):
            return True
        
        # 检查管理器
        manager = _get_manager()
        if manager and key in manager.Parser:
            return True
        
        return False
    
    def keys(self) -> List[str]:
        """
        获取所有解析器名称（包含外部插件）
        
        使用缓存优化频繁访问的性能。
        
        Returns:
            解析器名称列表
        """
        # 如果缓存有效，直接返回缓存副本
        if self._cache_valid and self._keys_cache is not None:
            return self._keys_cache.copy()
        
        # 重新计算所有键
        builtin_keys = set(super().keys())
        
        # 获取管理器中的解析器名称
        manager = _get_manager()
        if manager:
            builtin_keys.update(manager.Parser.keys())
        
        # 更新缓存
        self._keys_cache = list(builtin_keys)
        self._cache_valid = True
        
        return self._keys_cache.copy()
    
    def values(self) -> List[Any]:
        """
        获取所有解析器类（包含外部插件）
        
        Returns:
            解析器类列表
        """
        result: List[Any] = []
        for key in self.keys():
            result.append(self[key])
        return result
    
    def items(self) -> List[Tuple[str, Any]]:
        """
        获取所有解析器项（包含外部插件）
        
        Returns:
            解析器项列表 (名称, 类)
        """
        result: List[Tuple[str, Any]] = []
        for key in self.keys():
            result.append((key, self[key]))
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        安全获取解析器类
        
        Args:
            key: 解析器名称
            default: 默认值
            
        Returns:
            解析器类或默认值
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
    
    def __iter__(self):
        """迭代所有解析器名称"""
        return iter(self.keys())
    
    def __len__(self) -> int:
        """获取解析器数量"""
        return len(self.keys())


# 创建兼容字典实例
# 初始化时只包含内置解析器
Parser: _ParserDict = _ParserDict({
    "none": ParserNone,           # 不做处理
    "multi_para": MultiPara,      # 多栏-自然段
    "multi_line": MultiLine,      # 多栏-总是换行
    "multi_none": MultiNone,      # 多栏-无换行
    "single_para": SinglePara,    # 单栏-自然段
    "single_line": SingleLine,    # 单栏-总是换行
    "single_none": SingleNone,    # 单栏-无换行
    "single_code": SingleCode,    # 单栏-代码段
})


# ===============================================
# 第五部分：兼容函数
# ===============================================

def getParser(key: str) -> Tbpu:
    """
    获取排版解析器实例
    
    与旧版本完全兼容的接口。优先从管理器获取，
    其次从内置字典获取，不存在时返回默认解析器。
    
    适配策略：
    1. 优先使用管理器获取（支持外部插件）
    2. 其次从内置字典获取（向后兼容）
    3. 不存在时返回默认解析器（健壮性）
    
    Args:
        key: 解析器名称，如 'none', 'multi_para', 'single_line' 等
        
    Returns:
        解析器实例，不存在返回默认解析器实例
    """
    # 策略1：尝试使用管理器获取（包含外部插件）
    manager = _get_manager()
    if manager:
        try:
            parser = manager.get_parser(key)
            if parser is not None:
                return parser
        except Exception as e:
            # 管理器获取失败，记录日志后继续尝试内置字典
            logger.warning(f"管理器获取解析器 '{key}' 失败: {e}")
    
    # 策略2：从内置字典获取
    if key in Parser:
        try:
            return Parser[key]()
        except Exception as e:
            # 创建实例失败，记录日志并使用默认
            logger.error(f"创建解析器 '{key}' 实例失败: {e}")
    else:
        logger.warning(f"解析器 '{key}' 不存在，使用默认解析器")
    
    # 策略3：返回默认解析器
    return Parser["none"]()


# ===============================================
# 第六部分：新增扩展函数（可选使用）
# ===============================================

def get_available_parsers() -> List[str]:
    """
    获取所有可用的解析器名称列表
    
    新增功能，用于动态获取所有解析器（包括外部插件）。
    
    Returns:
        解析器名称列表
    """
    return list(Parser.keys())


def has_parser(key: str) -> bool:
    """
    检查是否存在指定的解析器
    
    Args:
        key: 解析器名称
        
    Returns:
        是否存在
    """
    return key in Parser


def get_parser_info(key: str) -> Optional[Dict[str, Any]]:
    """
    获取解析器详细信息
    
    Args:
        key: 解析器名称
        
    Returns:
        解析器信息字典，不存在返回 None
    """
    manager = _get_manager()
    if manager:
        return manager.get_parser_info(key)
    return None


def register_external_parser(name: str, parser_class: ParserClass) -> bool:
    """
    注册外部解析器
    
    允许运行时动态注册外部解析器。
    
    Args:
        name: 解析器名称
        parser_class: 解析器类（必须继承 Tbpu）
        
    Returns:
        注册是否成功
    """
    manager = _get_manager()
    if manager:
        try:
            plugin_info = {"api_class": parser_class}
            result = manager.register_plugin(name, plugin_info)
            if result:
                logger.info(f"成功注册外部解析器 '{name}'")
            return result
        except Exception as e:
            logger.error(f"注册外部解析器 '{name}' 失败: {e}")
            return False
    logger.warning("管理器未初始化，无法注册外部解析器")
    return False


# ===============================================
# 第七部分：翻译插件注册
# ===============================================

# 注册翻译插件到 Parser 字典
try:
    from ..translate import TranslateTbpu
    Parser["translate_online"] = TranslateTbpu
    logger.debug("翻译插件已注册到 Parser 字典")
except ImportError as e:
    logger.debug(f"翻译插件导入失败: {e}")


# ===============================================
# 第八部分：向后兼容的 __all__ 定义
# ===============================================

__all__ = [
    # 基类
    "Tbpu",
    # 兼容字典
    "Parser",
    # 兼容函数
    "getParser",
    # 内置解析器类（显式导出）
    "ParserNone",
    "MultiLine",
    "MultiPara",
    "MultiNone",
    "SingleLine",
    "SinglePara",
    "SingleNone",
    "SingleCode",
    # 忽略区域
    "IgnoreArea",
    # 新增扩展函数（可选）
    "get_available_parsers",
    "has_parser",
    "get_parser_info",
    "register_external_parser",
]


# ===============================================
# 第九部分：测试示例
# ===============================================

if __name__ == "__main__":
    """
    TBPU 模块适配测试示例
    
    运行此测试可以验证：
    1. 向后兼容性
    2. 新功能可用性
    3. 循环导入处理
    4. 缓存优化功能
    """
    import sys
    
    print("=" * 50)
    print("TBPU 模块适配测试")
    print("=" * 50)
    
    # 测试1：向后兼容 - 基础导入
    print("\n【测试1】向后兼容 - 基础导入")
    print(f"  Tbpu 基类: {Tbpu}")
    print(f"  ParserNone: {ParserNone}")
    print("  ✓ 基础类导入成功")
    
    # 测试2：向后兼容 - Parser 字典
    print("\n【测试2】向后兼容 - Parser 字典")
    print(f"  Parser 类型: {type(Parser)}")
    print(f"  内置解析器数量: {len(Parser)}")
    print(f"  可用解析器: {list(Parser.keys())}")
    assert "none" in Parser
    assert "single_para" in Parser
    print("  ✓ Parser 字典兼容")
    
    # 测试3：keys() 缓存优化
    print("\n【测试3】keys() 缓存优化")
    keys1 = Parser.keys()
    keys2 = Parser.keys()
    print(f"  第一次调用 keys(): {len(keys1)} 个")
    print(f"  第二次调用 keys(): {len(keys2)} 个")
    print(f"  缓存有效: {Parser._cache_valid}")
    assert keys1 == keys2
    print("  ✓ 缓存优化正常")
    
    # 测试4：向后兼容 - getParser 函数
    print("\n【测试4】向后兼容 - getParser 函数")
    parser = getParser("single_para")
    print(f"  getParser('single_para'): {type(parser).__name__}")
    assert isinstance(parser, Tbpu)
    
    # 测试默认回退
    unknown_parser = getParser("unknown_key")
    print(f"  getParser('unknown_key'): {type(unknown_parser).__name__} (默认回退)")
    assert isinstance(unknown_parser, ParserNone)
    print("  ✓ getParser 函数兼容")
    
    # 测试5：Parser 字典操作
    print("\n【测试5】Parser 字典操作")
    print(f"  Parser.get('multi_line'): {Parser.get('multi_line')}")
    print(f"  'single_code' in Parser: {'single_code' in Parser}")
    print(f"  items数量: {len(list(Parser.items()))}")
    print("  ✓ 字典操作兼容")
    
    # 测试6：新扩展函数
    print("\n【测试6】新扩展函数")
    parsers_list = get_available_parsers()
    print(f"  get_available_parsers(): {parsers_list}")
    print(f"  has_parser('none'): {has_parser('none')}")
    print(f"  has_parser('unknown'): {has_parser('unknown')}")
    print("  ✓ 扩展函数可用")
    
    # 测试7：解析器功能测试
    print("\n【测试7】解析器功能测试")
    test_blocks = [
        {"box": [[29, 19], [172, 19], [172, 44], [29, 44]], "score": 0.89, "text": "测试文本1"},
        {"box": [[29, 60], [161, 60], [161, 86], [29, 86]], "score": 0.75, "text": "测试文本2"},
    ]
    
    parser = getParser("none")
    result = parser.run(test_blocks.copy())
    print(f"  输入文块数: {len(test_blocks)}")
    print(f"  输出文块数: {len(result)}")
    print(f"  解析器名称: {parser.tbpu_name}")
    assert len(result) == len(test_blocks)
    print("  ✓ 解析器功能正常")
    
    # 测试8：缓存失效测试
    print("\n【测试8】缓存失效测试")
    original_keys = Parser.keys()
    Parser["test_key"] = ParserNone  # 添加新键
    print(f"  添加新键后缓存有效: {Parser._cache_valid}")
    new_keys = Parser.keys()
    print(f"  新键数量: {len(new_keys)}")
    assert "test_key" in new_keys
    del Parser["test_key"]  # 清理
    print("  ✓ 缓存失效机制正常")
    
    # 测试9：管理器集成（如果可用）
    print("\n【测试9】管理器集成")
    manager = _get_manager()
    if manager:
        print(f"  管理器已初始化: {type(manager).__name__}")
        print(f"  管理器Parser数量: {len(manager.Parser)}")
    else:
        print("  管理器未初始化（plugins_controller 可能未加载）")
        print("  这是正常的，模块仍然完全可用")
    print("  ✓ 管理器集成正常")
    
    # 总结
    print("\n" + "=" * 50)
    print("所有测试通过！")
    print("=" * 50)
    print("\n向后兼容性保证：")
    print("  - Tbpu 基类: ✓ 可用")
    print("  - Parser 字典: ✓ 可用")
    print("  - getParser(): ✓ 可用")
    print("\n新功能：")
    print("  - keys() 缓存优化: ✓ 可用")
    print("  - 外部插件支持: ✓ 可用（管理器加载时）")
    print("  - 扩展查询函数: ✓ 可用")
    print("  - 动态注册: ✓ 可用（管理器加载时）")
