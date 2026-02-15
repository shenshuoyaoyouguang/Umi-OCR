# ===============================================
# =============== 插件组管理器基类 ===============
# ===============================================

"""
插件组管理器基类

为特定类型的插件组提供统一管理接口。
所有具体类型的插件管理器都应继承此类。
"""

from typing import Dict, Any, Optional, List, Callable
from umi_log import logger


class PluginGroupManager:
    """
    插件组管理器基类
    
    管理同一类型的所有插件，提供插件注册、查询、实例化等功能。
    支持延迟初始化和依赖注入。
    
    Attributes:
        group_name: 插件组名称
        plugins_dict: 插件信息字典
        options_dict: 插件配置选项字典
        _api_classes: API 类缓存
        _instances: 插件实例缓存
    """
    
    def __init__(self, group_name: str):
        """
        初始化插件组管理器
        
        Args:
            group_name: 插件组名称（如 'ocr', 'output', 'tbpu', 'image'）
        """
        self.group_name = group_name
        self.plugins_dict: Dict[str, Dict[str, Any]] = {}
        self.options_dict: Dict[str, Dict[str, Any]] = {}
        self._api_classes: Dict[str, type] = {}
        self._instances: Dict[str, Any] = {}
        
    def register_plugin(self, name: str, plugin_info: Dict[str, Any]) -> bool:
        """
        注册一个插件
        
        Args:
            name: 插件名称
            plugin_info: 插件信息字典，包含 api_class, global_options, local_options 等
            
        Returns:
            注册是否成功
        """
        try:
            # 验证必要字段
            if "api_class" not in plugin_info:
                logger.error(f'插件 {name} 缺少 api_class 字段')
                return False
                
            # 设置默认值
            if "global_options" not in plugin_info:
                plugin_info["global_options"] = None
            if "local_options" not in plugin_info:
                plugin_info["local_options"] = None
                
            # 注册插件
            self.plugins_dict[name] = plugin_info
            self.options_dict[name] = {
                "global_options": plugin_info["global_options"],
                "local_options": plugin_info["local_options"],
            }
            
            # 缓存 API 类
            self._api_classes[name] = plugin_info["api_class"]
            
            logger.debug(f'插件 {name} 已注册到组 {self.group_name}')
            return True
            
        except Exception as e:
            logger.error(f'注册插件 {name} 失败: {e}')
            return False
    
    def unregister_plugin(self, name: str) -> bool:
        """
        注销一个插件
        
        Args:
            name: 插件名称
            
        Returns:
            注销是否成功
        """
        if name in self.plugins_dict:
            del self.plugins_dict[name]
            del self.options_dict[name]
            
            if name in self._api_classes:
                del self._api_classes[name]
            if name in self._instances:
                del self._instances[name]
                
            logger.debug(f'插件 {name} 已从组 {self.group_name} 注销')
            return True
        return False
    
    def get_plugin_names(self) -> List[str]:
        """
        获取所有已注册插件的名称列表
        
        Returns:
            插件名称列表
        """
        return list(self.plugins_dict.keys())
    
    def get_plugin_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定插件的详细信息
        
        Args:
            name: 插件名称
            
        Returns:
            插件信息字典，不存在则返回 None
        """
        return self.plugins_dict.get(name)
    
    def get_global_options(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定插件的全局配置选项
        
        Args:
            name: 插件名称
            
        Returns:
            全局配置选项字典，不存在则返回 None
        """
        if name in self.options_dict:
            return self.options_dict[name].get("global_options")
        return None
    
    def get_local_options(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定插件的局部配置选项
        
        Args:
            name: 插件名称
            
        Returns:
            局部配置选项字典，不存在则返回 None
        """
        if name in self.options_dict:
            return self.options_dict[name].get("local_options")
        return None
    
    def has_plugin(self, name: str) -> bool:
        """
        检查指定插件是否已注册
        
        Args:
            name: 插件名称
            
        Returns:
            插件是否存在
        """
        return name in self.plugins_dict
    
    def create_instance(self, name: str, *args, **kwargs) -> Any:
        """
        创建指定插件的实例
        
        Args:
            name: 插件名称
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            插件实例，失败则返回错误信息字符串
        """
        if name not in self._api_classes:
            return f'[Error] "{name}" not found in {self.group_name} plugins.'
        
        try:
            api_class = self._api_classes[name]
            instance = api_class(*args, **kwargs)
            return instance
        except Exception as e:
            logger.error(f'创建插件 {name} 实例失败', exc_info=True)
            return f"[Error] Failed to create instance of {name}: {e}"
    
    def get_or_create_instance(self, name: str, *args, **kwargs) -> Any:
        """
        获取或创建插件实例（带缓存）
        
        Args:
            name: 插件名称
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            插件实例
        """
        cache_key = f"{name}_{hash(str(args))}_{hash(str(kwargs))}"
        
        if cache_key not in self._instances:
            instance = self.create_instance(name, *args, **kwargs)
            if isinstance(instance, str) and instance.startswith("[Error]"):
                return instance
            self._instances[cache_key] = instance
            
        return self._instances[cache_key]
    
    def clear_cache(self):
        """清除实例缓存"""
        self._instances.clear()
        logger.debug(f'组 {self.group_name} 的实例缓存已清除')
    
    def init_plugins(self, plugins: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """
        批量初始化插件
        
        Args:
            plugins: 插件信息字典，键为插件名，值为插件信息
            
        Returns:
            错误信息字典，键为插件名，值为错误信息
        """
        errors = {}
        
        for name, plugin_info in plugins.items():
            if not self.register_plugin(name, plugin_info):
                errors[name] = f"Failed to register plugin {name}"
                
        return errors
