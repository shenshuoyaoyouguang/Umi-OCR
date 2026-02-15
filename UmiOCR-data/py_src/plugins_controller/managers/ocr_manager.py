# ===============================================
# =============== OCR 插件管理器 ===============
# ===============================================

"""
OCR 插件管理器

管理 OCR 引擎插件的生命周期，提供与现有 ocr.api 模块的兼容接口。
"""

from typing import Dict, Any, Optional, List
from .base_manager import PluginGroupManager
from umi_log import logger


class OcrPluginManager(PluginGroupManager):
    """
    OCR 插件管理器
    
    管理所有 OCR 引擎插件，提供统一的接口来获取 OCR API 实例。
    与现有 `ocr.api` 模块完全兼容。
    
    Attributes:
        ApiDict: 兼容旧接口的 API 类字典
        AllDict: 兼容旧接口的插件信息字典
    """
    
    def __init__(self):
        """初始化 OCR 插件管理器"""
        super().__init__("ocr")
        # 为了兼容旧接口
        self.ApiDict: Dict[str, type] = {}
        self.AllDict: Dict[str, Dict[str, Any]] = {}
        
    def register_plugin(self, name: str, plugin_info: Dict[str, Any]) -> bool:
        """
        注册 OCR 插件
        
        重写父类方法以更新兼容字典
        
        Args:
            name: 插件名称
            plugin_info: 插件信息字典
            
        Returns:
            注册是否成功
        """
        success = super().register_plugin(name, plugin_info)
        if success:
            # 更新兼容字典
            self.ApiDict[name] = plugin_info["api_class"]
            self.AllDict[name] = plugin_info
        return success
    
    def unregister_plugin(self, name: str) -> bool:
        """
        注销 OCR 插件
        
        重写父类方法以更新兼容字典
        
        Args:
            name: 插件名称
            
        Returns:
            注销是否成功
        """
        success = super().unregister_plugin(name)
        if success:
            # 更新兼容字典
            if name in self.ApiDict:
                del self.ApiDict[name]
            if name in self.AllDict:
                del self.AllDict[name]
        return success
    
    def get_api_ocr(self, api_key: str, argd: Dict[str, Any]) -> Any:
        """
        获取 OCR API 实例
        
        与现有 `ocr.api.getApiOcr` 函数完全兼容。
        
        Args:
            api_key: OCR 引擎名称
            argd: 配置参数字典
            
        Returns:
            OCR API 实例，失败返回 [Error] 开头的错误字符串
        """
        # 复制参数字典，避免修改原始数据
        processed_argd = argd.copy()
        
        # 检测并恢复 int 类型（兼容旧逻辑）
        for k in list(processed_argd.keys()):
            n = processed_argd[k]
            if isinstance(n, float):
                rounded = round(n)
                if abs(n - rounded) <= 1e-7:
                    processed_argd[k] = rounded
        
        # 使用父类方法创建实例
        result = self.create_instance(api_key, processed_argd)
        
        # 如果返回的是错误字符串，记录日志
        if isinstance(result, str) and result.startswith("[Error]"):
            logger.error(f'生成 OCR API 实例 {api_key} 失败: {result}')
            
        return result
    
    def get_local_options(self, api_key: str) -> Dict[str, Any]:
        """
        获取指定 OCR 引擎的局部配置选项
        
        与现有 `ocr.api.getLocalOptions` 函数完全兼容。
        
        Args:
            api_key: OCR 引擎名称
            
        Returns:
            局部配置选项字典，不存在则返回空字典
        """
        if api_key in self.AllDict:
            return self.AllDict[api_key].get("local_options")
        return None
    
    def init_plugins(self, plugins: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """
        批量初始化 OCR 插件
        
        与现有 `ocr.api.initOcrPlugins` 函数完全兼容。
        
        Args:
            plugins: 插件信息字典
            
        Returns:
            错误信息字典
        """
        errors = {}
        
        for name, plugin_info in plugins.items():
            if not self.register_plugin(name, plugin_info):
                errors[name] = f"Failed to register OCR plugin {name}"
                
        logger.info(f'OCR 插件初始化完成，共 {len(self.plugins_dict)} 个插件')
        return errors
    
    def get_available_engines(self) -> List[str]:
        """
        获取所有可用的 OCR 引擎名称
        
        Returns:
            OCR 引擎名称列表
        """
        return self.get_plugin_names()
    
    def get_engine_info(self, engine_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定 OCR 引擎的详细信息
        
        Args:
            engine_name: OCR 引擎名称
            
        Returns:
            引擎信息字典，不存在则返回 None
        """
        return self.get_plugin_info(engine_name)


# 全局单例实例（兼容旧接口）
_ocr_manager = OcrPluginManager()


# 兼容旧接口的函数
def initOcrPlugins(plugins: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """
    初始化 OCR 插件（兼容旧接口）
    
    Args:
        plugins: 插件信息字典
        
    Returns:
        错误信息字典
    """
    return _ocr_manager.init_plugins(plugins)


def getApiOcr(api_key: str, argd: Dict[str, Any]) -> Any:
    """
    获取 OCR API 实例（兼容旧接口）
    
    Args:
        api_key: OCR 引擎名称
        argd: 配置参数字典
        
    Returns:
        OCR API 实例或错误字符串
    """
    return _ocr_manager.get_api_ocr(api_key, argd)


def getLocalOptions(api_key: str) -> Dict[str, Any]:
    """
    获取局部配置选项（兼容旧接口）
    
    Args:
        api_key: OCR 引擎名称
        
    Returns:
        局部配置选项字典
    """
    return _ocr_manager.get_local_options(api_key)


# 导出兼容字典
ApiDict = _ocr_manager.ApiDict
AllDict = _ocr_manager.AllDict
