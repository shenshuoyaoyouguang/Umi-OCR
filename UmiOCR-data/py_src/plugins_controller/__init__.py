# =======================================
# =============== 插件控制器包 ===============
# =======================================

"""
Umi-OCR 插件控制器包

提供完整的插件生命周期管理功能：
- 插件加载与初始化
- 依赖解析与管理
- 配置管理
- 插件组管理

主要组件：
- PluginsController: 主控制器单例
- BasePlugin: 插件基类
- PluginGroupManager: 插件组管理器基类
- DependencyResolver: 依赖解析器
- ConfigManager: 配置管理器

使用示例：
    from plugins_controller import PluginsController
    
    # 初始化插件系统
    result = PluginsController.init()
    
    # 列出所有插件
    plugins = PluginsController.list_plugins()
    
    # 获取 OCR 插件组管理器
    ocr_manager = PluginsController.get_plugin_group("ocr")
"""

# 主控制器
from .plugins_controller import (
    PluginsController,
    _PluginsControllerClass,
    PLUGINS_PATH,
    PLUGINS_GROUPS,
    PluginMetadata,
    ConfigManager,
    init_plugins,
    get_plugin_info,
    list_plugins,
)

# 插件基类
from .base_plugin import (
    BasePlugin,
    OcrPlugin,
    OutputPlugin,
    TbpuPlugin,
    ImagePlugin,
    PluginGroup,
    PluginInfoDict,
    OcrResult,
    TextBlock,
    is_plugin_class,
    get_plugin_group,
    check_plugin_compatibility,
    LegacyPluginAdapter,
)

# 插件组管理接口
from .plugin_group import (
    PluginInfo,
    PluginGroupManager,
    PluginGroupRegistry,
    PLUGIN_GROUP_OCR,
    PLUGIN_GROUP_OUTPUT,
    PLUGIN_GROUP_TBPU,
    PLUGIN_GROUP_IMAGE,
    SUPPORTED_PLUGIN_GROUPS,
)

# 依赖解析器
from .dependency_resolver import (
    DependencyResolver,
    Dependency,
    Version,
    VersionMatcher,
    DependencyError,
    DependencyErrorType,
    CircularDependencyError,
)

# 插件组管理器
from .managers import (
    OcrPluginManager,
    OutputPluginManager,
    TbpuPluginManager,
    ImagePluginManager,
    # 兼容旧接口
    initOcrPlugins,
    getApiOcr,
    getLocalOptions,
    getParser,
    Parser,
    get_available_parsers,
    has_parser,
)

__all__ = [
    # 主控制器
    "PluginsController",
    "_PluginsControllerClass",
    "PLUGINS_PATH",
    "PLUGINS_GROUPS",
    "PluginMetadata",
    "ConfigManager",
    "init_plugins",
    "get_plugin_info",
    "list_plugins",
    
    # 插件基类
    "BasePlugin",
    "OcrPlugin",
    "OutputPlugin",
    "TbpuPlugin",
    "ImagePlugin",
    "PluginGroup",
    "PluginInfoDict",
    "OcrResult",
    "TextBlock",
    "is_plugin_class",
    "get_plugin_group",
    "check_plugin_compatibility",
    "LegacyPluginAdapter",
    
    # 插件组管理接口
    "PluginInfo",
    "PluginGroupManager",
    "PluginGroupRegistry",
    "PLUGIN_GROUP_OCR",
    "PLUGIN_GROUP_OUTPUT",
    "PLUGIN_GROUP_TBPU",
    "PLUGIN_GROUP_IMAGE",
    "SUPPORTED_PLUGIN_GROUPS",
    
    # 依赖解析器
    "DependencyResolver",
    "Dependency",
    "Version",
    "VersionMatcher",
    "DependencyError",
    "DependencyErrorType",
    "CircularDependencyError",
    
    # 插件组管理器
    "OcrPluginManager",
    "OutputPluginManager",
    "TbpuPluginManager",
    "ImagePluginManager",
    # 兼容接口
    "initOcrPlugins",
    "getApiOcr",
    "getLocalOptions",
    "getParser",
    "Parser",
    "get_available_parsers",
    "has_parser",
]
