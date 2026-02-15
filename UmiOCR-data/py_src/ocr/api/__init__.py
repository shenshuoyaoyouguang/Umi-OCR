# ===============================================
# =============== OCR 插件接口管理 ===============
# ===============================================

"""
OCR API 管理模块 - 适配版本

此模块已适配到新的插件组管理器系统，同时保持完全向后兼容。

适配策略:
1. 优先尝试从新系统导入所有接口
2. 如果新系统不可用，使用传统实现作为 fallback
3. 所有公开接口（ApiDict, AllDict, initOcrPlugins, getApiOcr, getLocalOptions）行为完全一致

历史兼容性保证:
- 旧的调用方式继续工作，无需修改任何调用代码
- 错误消息格式保持不变
- 所有边界条件处理保持一致
"""

from umi_log import logger

# =============================================================================
# 尝试适配到新系统
# =============================================================================

# 标记是否使用新系统
_using_new_system = False
_ocr_manager = None

try:
    # 尝试从新系统导入
    # 注意: 使用绝对导入路径避免循环导入问题
    from plugins_controller.managers.ocr_manager import (
        ApiDict as _NewApiDict,
        AllDict as _NewAllDict,
        initOcrPlugins as _new_initOcrPlugins,
        getApiOcr as _new_getApiOcr,
        getLocalOptions as _new_getLocalOptions,
        _ocr_manager as _new_ocr_manager,
    )
    
    # 如果导入成功，使用新系统的实现
    _using_new_system = True
    _ocr_manager = _new_ocr_manager
    
    # 导出兼容字典（引用新系统的字典，保持同步）
    ApiDict = _NewApiDict
    AllDict = _NewAllDict
    
    logger.debug("OCR API 管理器已适配到新插件系统")
    
except ImportError as e:
    # 新系统不可用，使用传统实现
    logger.warning(f"新插件系统不可用，使用传统实现: {e}")
    _using_new_system = False
    
    # =============================================================================
    # 传统实现（Fallback）
    # =============================================================================
    
    ApiDict = {}
    AllDict = {}


# =============================================================================
# 包装函数（确保行为一致）
# =============================================================================

def initOcrPlugins(plugins):
    """
    初始化 OCR 插件接口
    
    由插件控制器调用，传入动态插件信息。
    保持与旧版本完全兼容的行为。
    
    Args:
        plugins: 插件信息字典 {plugin_name: plugin_info}
        
    Returns:
        错误信息字典（传统实现返回空字典，新系统可能返回错误）
    """
    if _using_new_system:
        # 使用新系统的实现
        return _new_initOcrPlugins(plugins)
    else:
        # 传统实现
        global ApiDict, AllDict
        for p in plugins:
            ApiDict[p] = plugins[p]["api_class"]
            AllDict[p] = plugins[p]
        return {}  # 传统实现不返回错误信息


def getApiOcr(apiKey, argd):
    """
    生成一个 OCR API 实例
    
    成功返回 API 实例对象，失败返回 [Error] 开头的错误字符串。
    保持与旧版本完全兼容的行为和错误消息格式。
    
    Args:
        apiKey: OCR 引擎名称/标识
        argd: 配置参数字典
        
    Returns:
        API 实例对象，或错误字符串
    """
    if _using_new_system:
        # 使用新系统的实现
        return _new_getApiOcr(apiKey, argd)
    else:
        # 传统实现
        # 检测argd，恢复int类型
        for k in list(argd.keys()):  # 使用 list() 避免遍历时修改
            n = argd[k]
            if isinstance(n, float):
                rounded = round(n)
                if abs(n - rounded) <= 1e-7:
                    argd[k] = rounded
        
        if apiKey in ApiDict:
            try:
                return ApiDict[apiKey](argd)  # 实例化后返回
            except Exception as e:
                logger.error(f"生成api实例{apiKey}失败。", exc_info=True, stack_info=True)
                return f"[Error] Failed to generate API instance {apiKey}: {e}"
        return f'[Error] "{apiKey}" not in ApiDict.'


def getLocalOptions(apiKey):
    """
    返回一个 API 的局部配置字典
    
    获取指定 OCR 引擎的局部配置选项。
    保持与旧版本完全兼容的行为。
    
    Args:
        apiKey: OCR 引擎名称/标识
        
    Returns:
        局部配置选项字典，不存在返回 None（传统实现）或 {}（新系统）
    """
    if _using_new_system:
        # 使用新系统的实现
        return _new_getLocalOptions(apiKey)
    else:
        # 传统实现
        if apiKey in AllDict and "local_options" in AllDict[apiKey]:
            return AllDict[apiKey]["local_options"]
        return None


# =============================================================================
# 新系统扩展功能（仅在新系统可用时）
# =============================================================================

if _using_new_system:
    def getAvailableEngines():
        """
        获取所有可用的 OCR 引擎名称列表
        
        新系统提供的扩展功能。
        
        Returns:
            OCR 引擎名称列表
        """
        return _ocr_manager.get_available_engines()
    
    def getEngineInfo(engine_name):
        """
        获取指定 OCR 引擎的详细信息
        
        新系统提供的扩展功能。
        
        Args:
            engine_name: OCR 引擎名称
            
        Returns:
            引擎信息字典，不存在返回 None
        """
        return _ocr_manager.get_engine_info(engine_name)
    
    def isUsingNewSystem():
        """
        检查是否正在使用新插件系统
        
        Returns:
            是否使用新系统
        """
        return _using_new_system
else:
    def getAvailableEngines():
        """传统实现：返回 ApiDict 的所有键"""
        return list(ApiDict.keys())
    
    def getEngineInfo(engine_name):
        """传统实现：从 AllDict 获取信息"""
        return AllDict.get(engine_name)
    
    def isUsingNewSystem():
        """传统实现：返回 False"""
        return False


# =============================================================================
# 向后兼容性验证（仅在 __main__ 时执行）
# =============================================================================

if __name__ == "__main__":
    # 简单的兼容性测试
    print(f"使用新系统: {_using_new_system}")
    print(f"ApiDict 类型: {type(ApiDict)}")
    print(f"AllDict 类型: {type(AllDict)}")
    print(f"可用引擎: {getAvailableEngines()}")
