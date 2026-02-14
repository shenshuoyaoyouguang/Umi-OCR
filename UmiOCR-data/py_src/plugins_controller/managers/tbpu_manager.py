# ===============================================
# =============== 后处理插件管理器 ===============
# ===============================================

"""
TBPU (Text Block Processing Unit) 插件管理器

管理文本块后处理插件，提供与现有 ocr.tbpu 模块的兼容接口。
支持排版解析、忽略区域、文本合并等功能。
"""

from typing import Dict, Any, Optional, List, Type
from .base_manager import PluginGroupManager
from umi_log import logger


class TbpuPluginManager(PluginGroupManager):
    """
    后处理插件管理器
    
    管理所有文本块后处理插件，提供统一的接口来获取解析器实例。
    与现有 `ocr.tbpu` 模块完全兼容。
    
    Attributes:
        Parser: 兼容旧接口的解析器类字典
    """
    
    # 默认解析器名称
    DEFAULT_PARSER = "none"
    
    def __init__(self):
        """初始化后处理插件管理器"""
        super().__init__("tbpu")
        # 为了兼容旧接口
        self.Parser: Dict[str, Type] = {}
        
    def register_plugin(self, name: str, plugin_info: Dict[str, Any]) -> bool:
        """
        注册后处理插件
        
        重写父类方法以更新兼容字典
        
        Args:
            name: 插件名称/键名
            plugin_info: 插件信息字典
            
        Returns:
            注册是否成功
        """
        success = super().register_plugin(name, plugin_info)
        if success:
            # 更新兼容字典
            self.Parser[name] = plugin_info["api_class"]
        return success
    
    def unregister_plugin(self, name: str) -> bool:
        """
        注销后处理插件
        
        重写父类方法以更新兼容字典
        
        Args:
            name: 插件名称
            
        Returns:
            注销是否成功
        """
        success = super().unregister_plugin(name)
        if success:
            # 更新兼容字典
            if name in self.Parser:
                del self.Parser[name]
        return success
    
    def get_parser(self, key: str) -> Any:
        """
        获取排版解析器实例
        
        与现有 `ocr.tbpu.getParser` 函数完全兼容。
        
        Args:
            key: 解析器名称，如 'none', 'multi_para', 'single_line' 等
            
        Returns:
            解析器实例，不存在则返回默认解析器实例
        """
        if key in self.Parser:
            try:
                return self.Parser[key]()
            except Exception as e:
                logger.error(f'创建解析器 {key} 实例失败: {e}')
                # 失败时返回默认解析器
                return self._get_default_parser()
        else:
            logger.warning(f'解析器 {key} 不存在，使用默认解析器')
            return self._get_default_parser()
    
    def _get_default_parser(self) -> Any:
        """
        获取默认解析器实例
        
        Returns:
            默认解析器实例
        """
        if self.DEFAULT_PARSER in self.Parser:
            return self.Parser[self.DEFAULT_PARSER]()
        # 如果连默认解析器都没有，返回一个空对象
        logger.error('默认解析器不存在')
        return None
    
    def get_parser_names(self) -> List[str]:
        """
        获取所有可用的解析器名称
        
        Returns:
            解析器名称列表
        """
        return list(self.Parser.keys())
    
    def get_parser_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        获取指定解析器的详细信息
        
        Args:
            key: 解析器名称
            
        Returns:
            解析器信息字典，不存在则返回 None
        """
        return self.get_plugin_info(key)
    
    def has_parser(self, key: str) -> bool:
        """
        检查是否存在指定的解析器
        
        Args:
            key: 解析器名称
            
        Returns:
            是否存在
        """
        return key in self.Parser
    
    def init_plugins(self, plugins: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """
        批量初始化后处理插件
        
        Args:
            plugins: 插件信息字典，键为插件名，值为插件信息
            
        Returns:
            错误信息字典
        """
        errors = {}
        
        for name, plugin_info in plugins.items():
            if not self.register_plugin(name, plugin_info):
                errors[name] = f"Failed to register TBPU plugin {name}"
                
        logger.info(f'TBPU 插件初始化完成，共 {len(self.plugins_dict)} 个插件')
        return errors
    
    def register_builtin_parsers(self, parsers: Dict[str, Type]):
        """
        注册内置解析器
        
        用于注册项目内置的解析器类（非动态插件）。
        
        Args:
            parsers: 解析器类字典，键为名称，值为类
        """
        for name, parser_class in parsers.items():
            plugin_info = {"api_class": parser_class}
            self.register_plugin(name, plugin_info)


# 全局单例实例（兼容旧接口）
_tbpu_manager = TbpuPluginManager()


# 兼容旧接口的函数和字典
def getParser(key: str) -> Any:
    """
    获取排版解析器实例（兼容旧接口）
    
    Args:
        key: 解析器名称
        
    Returns:
        解析器实例
    """
    return _tbpu_manager.get_parser(key)


# 导出兼容字典
Parser = _tbpu_manager.Parser


# 便捷函数
def get_available_parsers() -> List[str]:
    """
    获取所有可用的解析器名称
    
    Returns:
        解析器名称列表
    """
    return _tbpu_manager.get_parser_names()


def has_parser(key: str) -> bool:
    """
    检查是否存在指定的解析器
    
    Args:
        key: 解析器名称
        
    Returns:
        是否存在
    """
    return _tbpu_manager.has_parser(key)
