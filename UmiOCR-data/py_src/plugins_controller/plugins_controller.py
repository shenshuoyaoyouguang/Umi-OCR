# =======================================
# =============== 加载插件 ===============
# =======================================

import os
import site
import importlib
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field

from umi_log import logger

# 导入新的插件系统组件
from .base_plugin import BasePlugin, is_plugin_class, get_plugin_group, check_plugin_compatibility, LegacyPluginAdapter
from .dependency_resolver import DependencyResolver, Dependency, DependencyErrorType
from .managers import (
    OcrPluginManager,
    OutputPluginManager,
    TbpuPluginManager,
    ImagePluginManager,
)

# 插件 总目录
PLUGINS_PATH = "plugins"
# 插件组 组名（保持向后兼容）
PLUGINS_GROUPS = ["ocr", "output", "tbpu", "image"]


# ===========================================
# 配置管理器（最小实现，可被外部替换）
# ===========================================

@dataclass
class PluginConfig:
    """插件配置数据类"""
    plugin_id: str
    group: str
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """
    插件配置管理器
    
    管理所有插件的配置信息，提供配置验证和存储功能。
    这是一个最小实现，可由外部更完整的实现替换。
    """
    
    def __init__(self):
        self._configs: Dict[str, PluginConfig] = {}
        self._validators: Dict[str, callable] = {}
    
    def register_plugin(self, plugin_id: str, group: str, 
                        global_options: Optional[Dict] = None,
                        local_options: Optional[Dict] = None) -> bool:
        """
        注册插件配置
        
        Args:
            plugin_id: 插件唯一标识
            group: 所属插件组
            global_options: 全局配置选项
            local_options: 局部配置选项
            
        Returns:
            注册是否成功
        """
        if plugin_id not in self._configs:
            self._configs[plugin_id] = PluginConfig(
                plugin_id=plugin_id,
                group=group,
                settings={
                    "global_options": global_options or {},
                    "local_options": local_options or {},
                }
            )
            logger.debug(f"插件配置已注册: {plugin_id}")
        return True
    
    def get_config(self, plugin_id: str) -> Optional[PluginConfig]:
        """获取插件配置"""
        return self._configs.get(plugin_id)
    
    def set_config(self, plugin_id: str, key: str, value: Any) -> bool:
        """设置配置项"""
        if plugin_id in self._configs:
            self._configs[plugin_id].settings[key] = value
            return True
        return False
    
    def validate_config(self, plugin_id: str) -> Tuple[bool, List[str]]:
        """
        验证插件配置
        
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        config = self._configs.get(plugin_id)
        if not config:
            errors.append(f"插件 {plugin_id} 未注册配置")
            return False, errors
        
        # 执行自定义验证器
        if plugin_id in self._validators:
            try:
                validator = self._validators[plugin_id]
                valid, msgs = validator(config)
                if not valid:
                    errors.extend(msgs)
            except Exception as e:
                errors.append(f"配置验证失败: {e}")
        
        return len(errors) == 0, errors
    
    def register_validator(self, plugin_id: str, validator: callable) -> None:
        """注册配置验证器"""
        self._validators[plugin_id] = validator
    
    def list_plugins(self, group: Optional[str] = None) -> List[str]:
        """列出所有或指定组的插件"""
        if group is None:
            return list(self._configs.keys())
        return [p for p, c in self._configs.items() if c.group == group]


# ===========================================
# 插件信息封装
# ===========================================

@dataclass
class PluginMetadata:
    """插件元数据封装类"""
    plugin_id: str
    name: str
    version: str
    group: str
    author: str = ""
    description: str = ""
    dependencies: List[Dependency] = field(default_factory=list)
    api_class: Optional[type] = None
    global_options: Optional[Dict] = None
    local_options: Optional[Dict] = None
    module: Optional[Any] = None
    is_legacy: bool = False
    
    @classmethod
    def from_module(cls, name: str, module: Any) -> Optional["PluginMetadata"]:
        """
        从模块创建插件元数据
        
        Args:
            name: 插件包名
            module: 导入的模块
            
        Returns:
            PluginMetadata 实例，验证失败返回 None
        """
        if not hasattr(module, "PluginInfo"):
            return None
        
        plugin_info = module.PluginInfo
        if not isinstance(plugin_info, dict):
            return None
        
        # 提取依赖信息
        dependencies = []
        deps_data = plugin_info.get("dependencies", [])
        for dep in deps_data:
            if isinstance(dep, str):
                dependencies.append(Dependency(id=dep))
            elif isinstance(dep, dict):
                dependencies.append(Dependency(
                    id=dep.get("id", ""),
                    version=dep.get("version", ">=0.0.0"),
                    optional=dep.get("optional", False)
                ))
        
        # 检测是否为旧式插件（未继承 BasePlugin）
        api_class = plugin_info.get("api_class")
        is_legacy = False
        if api_class and not issubclass(api_class, BasePlugin):
            is_legacy = True
            logger.debug(f"检测到旧式插件: {name}")
        
        return cls(
            plugin_id=plugin_info.get("id", name),
            name=plugin_info.get("name", name),
            version=plugin_info.get("version", "0.0.0"),
            group=plugin_info.get("group", ""),
            author=plugin_info.get("author", ""),
            description=plugin_info.get("description", ""),
            dependencies=dependencies,
            api_class=api_class,
            global_options=plugin_info.get("global_options"),
            local_options=plugin_info.get("local_options"),
            module=module,
            is_legacy=is_legacy
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（保持向后兼容）"""
        return {
            "group": self.group,
            "api_class": self.api_class,
            "global_options": self.global_options,
            "local_options": self.local_options,
            "id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "dependencies": [(d.id, d.version) for d in self.dependencies],
        }


# ===========================================
# 插件控制器（重构后）
# ===========================================

class _PluginsControllerClass:
    """
    插件控制器 - 重构版本
    
    集成新插件系统的核心组件：
    - 插件组管理器（Plugin Group Managers）
    - 依赖解析器（Dependency Resolver）
    - 配置管理器（Config Manager）
    
    保持完全向后兼容：
    - pluginsDict 格式不变
    - optionsDict 格式不变
    - init() 返回值不变
    - 支持旧式插件
    """
    
    def __init__(self):
        # 向后兼容的数据结构
        self.pluginsDict: Dict[str, Dict[str, Any]] = {}
        self.optionsDict: Dict[str, Dict[str, Any]] = {}
        
        # 初始化兼容结构
        for group in PLUGINS_GROUPS:
            self.pluginsDict[group] = {}
            self.optionsDict[group] = {}
        
        # 新组件实例
        self._config_manager = ConfigManager()
        self._dependency_resolver = DependencyResolver()
        self._group_managers: Dict[str, Any] = {}
        
        # 插件元数据缓存
        self._plugin_metadata: Dict[str, PluginMetadata] = {}
        
        # 初始化状态
        self._initialized = False
        self._init_errors: Dict[str, str] = {}
        
        # 初始化插件组管理器
        self._init_group_managers()
    
    def _init_group_managers(self) -> None:
        """初始化所有插件组管理器"""
        self._group_managers = {
            "ocr": OcrPluginManager(),
            "output": OutputPluginManager(),
            "tbpu": TbpuPluginManager(),
            "image": ImagePluginManager(),
        }
        logger.debug("插件组管理器初始化完成")
    
    # ===========================
    # 核心初始化方法（向后兼容）
    # ===========================
    
    def init(self) -> Dict[str, Any]:
        """
        初始化并加载插件（保持完全向后兼容）
        
        Returns:
            {"options": optionsDict, "errors": errors}
            与旧版本格式完全一致
        """
        if self._initialized:
            logger.warning("插件控制器已初始化，跳过重复初始化")
            return {"options": self.optionsDict, "errors": {}}
        
        errors = {}
        
        # 1. 添加包搜索路径
        if not os.path.exists(PLUGINS_PATH):
            os.makedirs(PLUGINS_PATH)
            logger.error(f"插件目录不存在: {PLUGINS_PATH}")
            return {"options": self.optionsDict, "errors": {}}
        
        site.addsitedir(PLUGINS_PATH)
        
        # 2. 第一阶段：扫描并加载所有插件模块
        loaded_plugins = self._scan_and_load_plugins(errors)
        
        # 3. 第二阶段：解析依赖关系
        load_order = self._resolve_dependencies(loaded_plugins, errors)
        
        # 4. 第三阶段：按拓扑顺序初始化插件
        self._initialize_plugins_in_order(load_order, loaded_plugins, errors)
        
        # 5. 第四阶段：初始化各插件组管理器
        group_errors = self._init_group_managers_with_plugins()
        errors.update(group_errors)
        
        # 6. 保存初始化状态
        self._initialized = True
        self._init_errors = errors.copy()
        
        # 7. 记录加载统计
        total_plugins = sum(len(plugins) for plugins in self.pluginsDict.values())
        logger.info(f"插件系统初始化完成，共加载 {total_plugins} 个插件，"
                   f"失败 {len(errors)} 个")
        
        return {"options": self.optionsDict, "errors": errors}
    
    def _scan_and_load_plugins(self, errors: Dict[str, str]) -> Dict[str, PluginMetadata]:
        """
        扫描并加载所有插件模块
        
        Args:
            errors: 错误信息字典
            
        Returns:
            插件元数据字典 {plugin_id: PluginMetadata}
        """
        loaded_plugins = {}
        plugList = os.listdir(PLUGINS_PATH)
        
        for name in plugList:
            initPath = os.path.join(PLUGINS_PATH, name, "__init__.py")
            if not os.path.exists(initPath):
                continue
            
            try:
                # 导入模块
                module = importlib.import_module(name)
                
                # 解析插件信息
                metadata = PluginMetadata.from_module(name, module)
                if not metadata:
                    errors[name] = "__init__.py 中未定义有效的 PluginInfo"
                    continue
                
                # 验证插件组
                if not metadata.group or metadata.group not in PLUGINS_GROUPS:
                    errors[name] = f'group "{metadata.group}" 不属于已定义的插件类型'
                    continue
                
                # 使用插件ID作为主键
                plugin_id = metadata.plugin_id
                
                # 检查重复ID
                if plugin_id in loaded_plugins:
                    errors[name] = f"插件ID冲突: {plugin_id} 已存在"
                    continue
                
                # 注册到依赖解析器
                self._dependency_resolver.add_plugin(
                    plugin_id,
                    metadata.dependencies,
                    metadata.version
                )
                
                loaded_plugins[plugin_id] = metadata
                self._plugin_metadata[plugin_id] = metadata
                
                logger.debug(f"插件已扫描: {plugin_id} ({name})")
                
            except Exception as e:
                errors[name] = f"动态导入包失败: {e}"
                logger.error(f"加载插件 {name} 失败: {e}", exc_info=True)
        
        return loaded_plugins
    
    def _resolve_dependencies(self, loaded_plugins: Dict[str, PluginMetadata], 
                              errors: Dict[str, str]) -> List[str]:
        """
        解析插件依赖关系，返回加载顺序
        
        Args:
            loaded_plugins: 已加载的插件字典
            errors: 错误信息字典
            
        Returns:
            按拓扑排序的插件ID列表
        """
        try:
            load_order = self._dependency_resolver.resolve()
            
            # 检查依赖错误
            for dep_error in self._dependency_resolver.get_errors():
                if dep_error.error_type == DependencyErrorType.VERSION_MISMATCH:
                    logger.warning(f"依赖版本不匹配: {dep_error}")
                elif dep_error.error_type == DependencyErrorType.CIRCULAR:
                    logger.error(f"循环依赖: {dep_error}")
            
            # 检查缺失的依赖
            for plugin_id, dep_id in self._dependency_resolver.get_missing():
                metadata = loaded_plugins.get(plugin_id)
                if metadata:
                    # 查找是否为可选依赖
                    dep_info = next((d for d in metadata.dependencies if d.id == dep_id), None)
                    if dep_info and not dep_info.optional:
                        errors[plugin_id] = f"缺少必需依赖: {dep_id}"
            
            return load_order
            
        except Exception as e:
            logger.error(f"依赖解析失败: {e}", exc_info=True)
            # 失败时按原始顺序加载
            return list(loaded_plugins.keys())
    
    def _initialize_plugins_in_order(self, load_order: List[str],
                                     loaded_plugins: Dict[str, PluginMetadata],
                                     errors: Dict[str, str]) -> None:
        """
        按顺序初始化插件
        
        Args:
            load_order: 加载顺序列表
            loaded_plugins: 插件元数据字典
            errors: 错误信息字典
        """
        for plugin_id in load_order:
            if plugin_id not in loaded_plugins:
                continue
            
            metadata = loaded_plugins[plugin_id]
            
            try:
                # 注册到配置管理器
                self._config_manager.register_plugin(
                    plugin_id,
                    metadata.group,
                    metadata.global_options,
                    metadata.local_options
                )
                
                # 适配旧式插件
                if metadata.is_legacy and metadata.api_class:
                    adapted_class = self._adapt_legacy_plugin(metadata)
                    if adapted_class:
                        metadata.api_class = adapted_class
                        metadata.is_legacy = False
                
                # 转换为旧格式并存储
                plugin_info = metadata.to_dict()
                self.pluginsDict[metadata.group][plugin_id] = plugin_info
                self.optionsDict[metadata.group][plugin_id] = {
                    "global_options": metadata.global_options,
                    "local_options": metadata.local_options,
                }
                
                # 注册到对应的组管理器
                manager = self._group_managers.get(metadata.group)
                if manager:
                    manager.register_plugin(plugin_id, plugin_info)
                
                logger.debug(f"插件初始化成功: {plugin_id}")
                
            except Exception as e:
                errors[plugin_id] = f"初始化失败: {e}"
                logger.error(f"插件 {plugin_id} 初始化失败: {e}", exc_info=True)
    
    def _adapt_legacy_plugin(self, metadata: PluginMetadata) -> Optional[type]:
        """
        适配旧式插件类
        
        Args:
            metadata: 插件元数据
            
        Returns:
            适配后的类，或 None
        """
        try:
            if metadata.group == "ocr":
                return LegacyPluginAdapter.adapt_ocr_plugin(
                    metadata.api_class,
                    metadata.to_dict()
                )
            elif metadata.group == "tbpu":
                return LegacyPluginAdapter.adapt_tbpu_plugin(
                    metadata.api_class,
                    metadata.to_dict()
                )
            # 其他类型可以按需添加
            logger.debug(f"旧式插件适配成功: {metadata.plugin_id}")
            return metadata.api_class
        except Exception as e:
            logger.error(f"适配旧式插件 {metadata.plugin_id} 失败: {e}")
            return None
    
    def _init_group_managers_with_plugins(self) -> Dict[str, str]:
        """
        使用已加载的插件初始化各组管理器
        
        Returns:
            错误信息字典
        """
        errors = {}
        
        # OCR 管理器特殊处理（保持兼容）
        try:
            from ..ocr.api import initOcrPlugins
            ocr_errs = initOcrPlugins(self.pluginsDict["ocr"])
            if ocr_errs:
                errors.update(ocr_errs)
        except Exception as e:
            logger.error(f"OCR 插件管理器初始化失败: {e}", exc_info=True)
            errors["ocr_manager"] = str(e)
        
        # 其他管理器初始化
        for group_name, manager in self._group_managers.items():
            if group_name == "ocr":
                continue  # 已处理
            try:
                group_errors = manager.init_plugins(self.pluginsDict[group_name])
                errors.update(group_errors)
            except Exception as e:
                logger.error(f"{group_name} 管理器初始化失败: {e}", exc_info=True)
                errors[f"{group_name}_manager"] = str(e)
        
        return errors
    
    # ===========================
    # 新增功能方法
    # ===========================
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        获取插件详细信息
        
        Args:
            plugin_id: 插件唯一标识
            
        Returns:
            插件信息字典，不存在返回 None
        """
        # 先从元数据缓存查找
        if plugin_id in self._plugin_metadata:
            return self._plugin_metadata[plugin_id].to_dict()
        
        # 从各组中查找
        for group_plugins in self.pluginsDict.values():
            if plugin_id in group_plugins:
                return group_plugins[plugin_id]
        
        return None
    
    def get_plugin_group(self, group_name: str) -> Optional[Any]:
        """
        获取插件组管理器
        
        Args:
            group_name: 插件组名称（ocr/output/tbpu/image）
            
        Returns:
            插件组管理器实例，不存在返回 None
        """
        return self._group_managers.get(group_name)
    
    def check_dependencies(self, plugin_id: str) -> Dict[str, Any]:
        """
        检查插件依赖状态
        
        Args:
            plugin_id: 插件唯一标识
            
        Returns:
            检查结果字典：
            {
                "valid": bool,           # 依赖是否全部满足
                "missing": [...],        # 缺失的依赖列表
                "version_mismatch": [...],# 版本不匹配的列表
                "circular": [...]        # 循环依赖信息
            }
        """
        result = {
            "valid": True,
            "missing": [],
            "version_mismatch": [],
            "circular": []
        }
        
        metadata = self._plugin_metadata.get(plugin_id)
        if not metadata:
            result["valid"] = False
            result["missing"].append(f"插件 {plugin_id} 未找到")
            return result
        
        # 检查每个依赖
        for dep in metadata.dependencies:
            if dep.id not in self._plugin_metadata:
                if not dep.optional:
                    result["missing"].append(dep.id)
                    result["valid"] = False
            else:
                actual_version = self._plugin_metadata[dep.id].version
                if not dep.check_version(actual_version):
                    result["version_mismatch"].append({
                        "id": dep.id,
                        "required": dep.version,
                        "actual": actual_version
                    })
                    result["valid"] = False
        
        # 检查循环依赖
        for error in self._dependency_resolver.get_errors():
            if (error.plugin_id == plugin_id and 
                error.error_type == DependencyErrorType.CIRCULAR):
                result["circular"].append(str(error))
                result["valid"] = False
        
        return result
    
    def list_plugins(self, group: Optional[str] = None) -> List[str]:
        """
        列出所有或指定组的插件
        
        Args:
            group: 插件组名称，None 表示所有组
            
        Returns:
            插件ID列表
        """
        if group:
            return list(self.pluginsDict.get(group, {}).keys())
        
        # 返回所有插件
        all_plugins = []
        for group_plugins in self.pluginsDict.values():
            all_plugins.extend(group_plugins.keys())
        return all_plugins
    
    def get_plugins_by_group(self) -> Dict[str, List[str]]:
        """
        按组获取所有插件
        
        Returns:
            {group_name: [plugin_id, ...]}
        """
        return {
            group: list(plugins.keys())
            for group, plugins in self.pluginsDict.items()
        }
    
    def validate_plugin_config(self, plugin_id: str) -> Tuple[bool, List[str]]:
        """
        验证插件配置
        
        Args:
            plugin_id: 插件唯一标识
            
        Returns:
            (是否有效, 错误信息列表)
        """
        return self._config_manager.validate_config(plugin_id)
    
    def get_config_manager(self) -> ConfigManager:
        """获取配置管理器实例"""
        return self._config_manager
    
    def get_dependency_resolver(self) -> DependencyResolver:
        """获取依赖解析器实例"""
        return self._dependency_resolver
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized
    
    def get_init_errors(self) -> Dict[str, str]:
        """获取初始化时的错误信息"""
        return self._init_errors.copy()
    
    def reload_plugin(self, plugin_id: str) -> Tuple[bool, str]:
        """
        重新加载指定插件
        
        Args:
            plugin_id: 插件唯一标识
            
        Returns:
            (是否成功, 错误信息)
        """
        # 查找插件所属组
        metadata = self._plugin_metadata.get(plugin_id)
        if not metadata:
            return False, f"插件 {plugin_id} 不存在"
        
        try:
            # 重新导入模块
            module = importlib.reload(metadata.module)
            
            # 重新解析元数据
            new_metadata = PluginMetadata.from_module(plugin_id, module)
            if not new_metadata:
                return False, "重新加载后 PluginInfo 无效"
            
            # 更新依赖解析器中的依赖关系（如果依赖发生变化）
            if new_metadata.dependencies != metadata.dependencies:
                self._dependency_resolver.update_plugin_dependencies(
                    plugin_id, new_metadata.dependencies, new_metadata.version
                )
                logger.debug(f"插件 {plugin_id} 的依赖关系已更新")
            
            # 更新缓存
            self._plugin_metadata[plugin_id] = new_metadata
            
            # 更新存储
            plugin_info = new_metadata.to_dict()
            self.pluginsDict[new_metadata.group][plugin_id] = plugin_info
            self.optionsDict[new_metadata.group][plugin_id] = {
                "global_options": new_metadata.global_options,
                "local_options": new_metadata.local_options,
            }
            
            # 更新管理器
            manager = self._group_managers.get(new_metadata.group)
            if manager:
                manager.unregister_plugin(plugin_id)
                manager.register_plugin(plugin_id, plugin_info)
            
            logger.info(f"插件 {plugin_id} 重新加载成功")
            return True, ""
            
        except Exception as e:
            logger.error(f"重新加载插件 {plugin_id} 失败: {e}", exc_info=True)
            return False, str(e)


# 全局单例实例
PluginsController = _PluginsControllerClass()


# ===========================================
# 便捷函数（向后兼容）
# ===========================================

def init_plugins() -> Dict[str, Any]:
    """初始化插件（便捷函数）"""
    return PluginsController.init()


def get_plugin_info(plugin_id: str) -> Optional[Dict[str, Any]]:
    """获取插件信息（便捷函数）"""
    return PluginsController.get_plugin_info(plugin_id)


def list_plugins(group: Optional[str] = None) -> List[str]:
    """列出插件（便捷函数）"""
    return PluginsController.list_plugins(group)


# ===========================================
# 使用示例
# ===========================================

if __name__ == "__main__":
    """
    使用示例：
    
    # 初始化插件系统
    result = PluginsController.init()
    print(f"Options: {result['options']}")
    print(f"Errors: {result['errors']}")
    
    # 列出所有插件
    all_plugins = PluginsController.list_plugins()
    print(f"所有插件: {all_plugins}")
    
    # 列出 OCR 插件
    ocr_plugins = PluginsController.list_plugins("ocr")
    print(f"OCR 插件: {ocr_plugins}")
    
    # 获取插件信息
    info = PluginsController.get_plugin_info("my_plugin")
    print(f"插件信息: {info}")
    
    # 获取插件组管理器
    ocr_manager = PluginsController.get_plugin_group("ocr")
    api = ocr_manager.get_api_ocr("paddleocr", {"language": "zh"})
    
    # 检查依赖
    deps_status = PluginsController.check_dependencies("my_plugin")
    print(f"依赖状态: {deps_status}")
    
    # 验证配置
    valid, errors = PluginsController.validate_plugin_config("my_plugin")
    print(f"配置有效: {valid}, 错误: {errors}")
    """
    pass