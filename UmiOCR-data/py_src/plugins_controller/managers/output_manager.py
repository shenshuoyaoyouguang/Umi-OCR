# ===============================================
# =============== 输出插件管理器 ===============
# ===============================================

"""
输出插件管理器

管理输出格式插件（txt、json、pdf、csv、md 等），
支持多种输出格式的动态注册和实例化。
"""

from typing import Dict, Any, Optional, List, Type
from .base_manager import PluginGroupManager
from umi_log import logger


class OutputPluginManager(PluginGroupManager):
    """
    输出插件管理器
    
    管理所有输出格式插件，支持 txt、json、pdf、csv、md 等格式的输出。
    每个输出插件负责将 OCR 结果输出到指定格式的文件。
    
    Attributes:
        _formats: 支持的格式名称到插件名的映射
    """
    
    def __init__(self):
        """初始化输出插件管理器"""
        super().__init__("output")
        # 格式到插件名的映射缓存
        self._formats: Dict[str, str] = {}
        
    def register_plugin(self, name: str, plugin_info: Dict[str, Any]) -> bool:
        """
        注册输出插件
        
        Args:
            name: 插件名称
            plugin_info: 插件信息字典，可包含 format 字段指定支持的格式
            
        Returns:
            注册是否成功
        """
        success = super().register_plugin(name, plugin_info)
        if success:
            # 如果有 format 字段，缓存格式映射
            if "format" in plugin_info:
                format_name = plugin_info["format"]
                self._formats[format_name] = name
            else:
                # 默认使用插件名作为格式名
                self._formats[name] = name
        return success
    
    def unregister_plugin(self, name: str) -> bool:
        """
        注销输出插件
        
        Args:
            name: 插件名称
            
        Returns:
            注销是否成功
        """
        # 清除格式映射
        formats_to_remove = [f for f, n in self._formats.items() if n == name]
        for fmt in formats_to_remove:
            del self._formats[fmt]
            
        return super().unregister_plugin(name)
    
    def get_output(self, format_name: str, argd: Dict[str, Any]) -> Any:
        """
        获取指定格式的输出器实例
        
        Args:
            format_name: 输出格式名称（如 'txt', 'json', 'pdf' 等）
            argd: 配置参数字典，包含 outputDir, outputFileName, ignoreBlank 等
            
        Returns:
            输出器实例，失败返回 [Error] 开头的错误字符串
        """
        # 先查找格式映射
        plugin_name = self._formats.get(format_name, format_name)
        
        if not self.has_plugin(plugin_name):
            return f'[Error] Output format "{format_name}" not found.'
        
        return self.create_instance(plugin_name, argd)
    
    def get_available_formats(self) -> List[str]:
        """
        获取所有支持的输出格式
        
        Returns:
            格式名称列表
        """
        return list(self._formats.keys())
    
    def get_format_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定格式的详细信息
        
        Args:
            format_name: 格式名称
            
        Returns:
            格式信息字典，不存在则返回 None
        """
        plugin_name = self._formats.get(format_name)
        if plugin_name:
            return self.get_plugin_info(plugin_name)
        return None
    
    def is_format_supported(self, format_name: str) -> bool:
        """
        检查是否支持指定的输出格式
        
        Args:
            format_name: 格式名称
            
        Returns:
            是否支持
        """
        return format_name in self._formats or self.has_plugin(format_name)
    
    def get_outputter_for_file(self, file_path: str, argd: Dict[str, Any]) -> Any:
        """
        根据文件路径自动选择合适的输出器
        
        Args:
            file_path: 文件路径
            argd: 配置参数字典
            
        Returns:
            输出器实例
        """
        # 从文件扩展名推断格式
        ext = file_path.lower().split('.')[-1] if '.' in file_path else ''
        
        # 常见扩展名映射
        ext_mapping = {
            'txt': 'txt',
            'json': 'json',
            'jsonl': 'jsonl',
            'pdf': 'pdf',
            'csv': 'csv',
            'md': 'md',
            'markdown': 'md',
        }
        
        format_name = ext_mapping.get(ext, 'txt')  # 默认使用 txt
        return self.get_output(format_name, argd)


# 全局单例实例
_output_manager = OutputPluginManager()


# 便捷的模块级函数
def get_output(format_name: str, argd: Dict[str, Any]) -> Any:
    """
    获取指定格式的输出器实例
    
    Args:
        format_name: 输出格式名称
        argd: 配置参数字典
        
    Returns:
        输出器实例或错误字符串
    """
    return _output_manager.get_output(format_name, argd)


def get_available_formats() -> List[str]:
    """
    获取所有支持的输出格式
    
    Returns:
        格式名称列表
    """
    return _output_manager.get_available_formats()


def is_format_supported(format_name: str) -> bool:
    """
    检查是否支持指定的输出格式
    
    Args:
        format_name: 格式名称
        
    Returns:
        是否支持
    """
    return _output_manager.is_format_supported(format_name)
