# ===========================================
# =============== 插件组管理接口 ===============
# ===========================================
"""
插件组管理接口定义模块。

该模块定义了插件组管理的基础架构，包括：
- PluginInfo: 插件信息数据类
- PluginGroupManager: 插件组管理器抽象基类
- PluginGroupRegistry: 插件组注册表

使用示例：
    # 注册自定义插件组管理器
    @PluginGroupRegistry.register
    class MyPluginManager(PluginGroupManager):
        group_name = "my_group"
        
        def init_plugins(self, plugins: dict) -> dict:
            # 初始化逻辑
            return {}
    
    # 获取管理器
    manager_class = PluginGroupRegistry.get_manager("my_group")
"""

import abc
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field


@dataclass
class PluginInfo:
    """
    插件信息数据类，用于描述插件的元数据。
    
    属性说明：
        group: 插件所属分组（如 "ocr", "output", "tbpu", "image"）
        id: 插件唯一标识符，通常使用包名
        name: 插件显示名称，用于UI展示
        version: 插件版本号，格式建议 "x.y.z"
        global_options: 全局配置选项字典，用于插件级别的配置
        local_options: 局部配置选项字典，用于实例级别的配置
        api_class: API实现类，将被实例化后使用
        dependencies: 依赖插件列表，格式为 ["group:id", ...]
    
    示例：
        PluginInfo(
            group="ocr",
            id="my_ocr_plugin",
            name="我的OCR插件",
            version="1.0.0",
            global_options={"model_path": "./model"},
            local_options={"language": "zh"},
            api_class=MyOcrApi,
            dependencies=[]
        )
    """
    group: str
    id: str
    name: str
    version: str
    api_class: type
    global_options: Optional[dict] = None
    local_options: Optional[dict] = None
    dependencies: list = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后的验证，确保必要字段不为空。"""
        if not self.group:
            raise ValueError("PluginInfo.group 不能为空")
        if not self.id:
            raise ValueError("PluginInfo.id 不能为空")
        if not self.name:
            raise ValueError("PluginInfo.name 不能为空")
        if not self.version:
            raise ValueError("PluginInfo.version 不能为空")
        if not self.api_class:
            raise ValueError("PluginInfo.api_class 不能为空")


class PluginGroupManager(abc.ABC):
    """
    插件组管理器抽象基类。
    
    所有插件组管理器必须继承此类，并实现其抽象方法。
    每个插件组（如 ocr、output、tbpu、image）应有对应的管理器。
    
    类属性：
        group_name: 插件组名称，子类必须定义此属性
    
    使用示例：
        class OcrPluginManager(PluginGroupManager):
            group_name = "ocr"
            
            def init_plugins(self, plugins: dict) -> dict:
                self._plugins = plugins
                return {}
            
            def get_api(self, key: str, config: dict) -> Any:
                if key in self._plugins:
                    return self._plugins[key]["api_class"](config)
                return None
    """
    
    group_name: str = ""
    
    def __init__(self):
        """初始化管理器，子类可重写此方法。"""
        self._plugins: dict = {}
    
    @abc.abstractmethod
    def init_plugins(self, plugins: dict) -> dict:
        """
        初始化插件组。
        
        此方法在插件加载完成后被调用，用于执行插件组的初始化工作。
        子类应在此方法中保存插件信息，并进行必要的初始化操作。
        
        参数：
            plugins: 插件信息字典，格式为 {plugin_id: PluginInfo}
        
        返回：
            错误信息字典，格式为 {plugin_id: error_message}。
            如果全部成功，返回空字典 {}。
        """
        pass
    
    @abc.abstractmethod
    def get_api(self, key: str, config: dict) -> Any:
        """
        获取API实例。
        
        根据插件ID和配置信息，创建并返回API实例。
        
        参数：
            key: 插件唯一标识符
            config: 实例配置字典
        
        返回：
            API实例对象，或失败时返回以 "[Error]" 开头的错误信息字符串
        """
        pass
    
    @abc.abstractmethod
    def get_options(self, key: str) -> dict:
        """
        获取插件配置选项。
        
        参数：
            key: 插件唯一标识符
        
        返回：
            包含 global_options 和 local_options 的字典，
            格式为 {"global_options": {...}, "local_options": {...}}
        """
        pass
    
    @abc.abstractmethod
    def list_plugins(self) -> list:
        """
        列出所有插件ID。
        
        返回：
            插件ID列表
        """
        pass
    
    @abc.abstractmethod
    def has_plugin(self, key: str) -> bool:
        """
        检查插件是否存在。
        
        参数：
            key: 插件唯一标识符
        
        返回：
            如果插件存在返回True，否则返回False
        """
        pass


class PluginGroupRegistry:
    """
    插件组注册表。
    
    用于注册和管理所有插件组管理器类。
    提供类装饰器和静态方法用于注册和查询管理器。
    
    使用示例：
        # 方式1：使用装饰器注册
        @PluginGroupRegistry.register
        class OcrPluginManager(PluginGroupManager):
            group_name = "ocr"
            ...
        
        # 方式2：手动注册
        PluginGroupRegistry.register(OcrPluginManager)
        
        # 获取管理器
        manager_class = PluginGroupRegistry.get_manager("ocr")
        
        # 列出所有组
        groups = PluginGroupRegistry.list_groups()
    """
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, manager_class: type) -> type:
        """
        注册插件组管理器类。
        
        可作为类装饰器使用，或直接调用。
        
        参数：
            manager_class: 继承自 PluginGroupManager 的类
        
        返回：
            注册的类（便于装饰器使用）
        
        异常：
            TypeError: 如果 manager_class 不是 PluginGroupManager 的子类
            ValueError: 如果 group_name 为空或已注册
        """
        # 验证继承关系
        if not issubclass(manager_class, PluginGroupManager):
            raise TypeError(
                f"管理器类 {manager_class.__name__} 必须继承自 PluginGroupManager"
            )
        
        # 验证 group_name
        group_name = getattr(manager_class, "group_name", None)
        if not group_name:
            raise ValueError(
                f"管理器类 {manager_class.__name__} 必须定义 group_name 类属性"
            )
        
        # 检查重复注册
        if group_name in cls._registry:
            existing = cls._registry[group_name].__name__
            raise ValueError(
                f"插件组 '{group_name}' 已被类 {existing} 注册，"
                f"无法重复注册 {manager_class.__name__}"
            )
        
        cls._registry[group_name] = manager_class
        return manager_class
    
    @classmethod
    def get_manager(cls, group_name: str) -> Optional[type]:
        """
        获取指定组的插件组管理器类。
        
        参数：
            group_name: 插件组名称
        
        返回：
            管理器类，如果不存在返回 None
        """
        return cls._registry.get(group_name)
    
    @classmethod
    def list_groups(cls) -> List[str]:
        """
        列出所有已注册的插件组名称。
        
        返回：
            插件组名称列表
        """
        return list(cls._registry.keys())
    
    @classmethod
    def is_registered(cls, group_name: str) -> bool:
        """
        检查插件组是否已注册。
        
        参数：
            group_name: 插件组名称
        
        返回：
            如果已注册返回True，否则返回False
        """
        return group_name in cls._registry
    
    @classmethod
    def unregister(cls, group_name: str) -> bool:
        """
        注销插件组管理器。
        
        参数：
            group_name: 插件组名称
        
        返回：
            如果成功注销返回True，如果该组不存在返回False
        """
        if group_name in cls._registry:
            del cls._registry[group_name]
            return True
        return False
    
    @classmethod
    def clear(cls):
        """清空所有注册的插件组管理器。主要用于测试。"""
        cls._registry.clear()


# ========================= 预定义的插件组常量 =========================

# 支持的插件组类型
PLUGIN_GROUP_OCR = "ocr"
PLUGIN_GROUP_OUTPUT = "output"
PLUGIN_GROUP_TBPU = "tbpu"
PLUGIN_GROUP_IMAGE = "image"

# 所有支持的插件组列表
SUPPORTED_PLUGIN_GROUPS = [
    PLUGIN_GROUP_OCR,
    PLUGIN_GROUP_OUTPUT,
    PLUGIN_GROUP_TBPU,
    PLUGIN_GROUP_IMAGE,
]


# ========================= 与现有系统的集成说明 =========================

"""
【与现有系统的集成说明】

1. 与 plugins_controller.py 的集成：
   
   修改 PLUGINS_GROUPS 定义：
   ```python
   from .plugin_group import (
       PluginGroupRegistry, 
       SUPPORTED_PLUGIN_GROUPS,
       PLUGIN_GROUP_OCR,
   )
   
   PLUGINS_GROUPS = SUPPORTED_PLUGIN_GROUPS
   ```
   
   修改插件加载逻辑：
   ```python
   def init(self):
       # ... 加载插件代码 ...
       
       # 为每个插件组调用对应的管理器
       for group_name in PLUGINS_GROUPS:
           manager_class = PluginGroupRegistry.get_manager(group_name)
           if manager_class:
               manager = manager_class()
               errors = manager.init_plugins(self.pluginsDict[group_name])
               # 保存管理器实例供后续使用
               self._managers[group_name] = manager
   ```

2. 与 ocr/api/__init__.py 的集成：
   
   将现有的 initOcrPlugins、getApiOcr、getLocalOptions 函数
   封装到一个 PluginGroupManager 的子类中：
   
   ```python
   from plugins_controller.plugin_group import (
       PluginGroupManager, 
       PluginGroupRegistry
   )
   
   @PluginGroupRegistry.register
   class OcrPluginManager(PluginGroupManager):
       group_name = "ocr"
       
       def __init__(self):
           super().__init__()
           self._api_dict = {}
           self._all_dict = {}
       
       def init_plugins(self, plugins: dict) -> dict:
           self._plugins = plugins
           for p_id, p_info in plugins.items():
               self._api_dict[p_id] = p_info["api_class"]
               self._all_dict[p_id] = p_info
           return {}
       
       def get_api(self, key: str, config: dict) -> Any:
           if key in self._api_dict:
               try:
                   return self._api_dict[key](config)
               except Exception as e:
                   return f"[Error] Failed to generate API instance {key}: {e}"
           return f'[Error] "{key}" not in ApiDict.'
       
       def get_options(self, key: str) -> dict:
           if key in self._all_dict:
               return {
                   "global_options": self._all_dict[key].get("global_options"),
                   "local_options": self._all_dict[key].get("local_options"),
               }
           return {"global_options": None, "local_options": None}
       
       def list_plugins(self) -> list:
           return list(self._plugins.keys())
       
       def has_plugin(self, key: str) -> bool:
           return key in self._plugins
   ```

3. 向后兼容性：
   
   为了保持向后兼容，可以保留原有的全局函数，
   但让它们委托给新的管理器类：
   
   ```python
   _manager = OcrPluginManager()
   
   def initOcrPlugins(plugins):
       return _manager.init_plugins(plugins)
   
   def getApiOcr(apiKey, argd):
       return _manager.get_api(apiKey, argd)
   
   def getLocalOptions(apiKey):
       return _manager.get_options(apiKey)["local_options"]
   ```
"""
