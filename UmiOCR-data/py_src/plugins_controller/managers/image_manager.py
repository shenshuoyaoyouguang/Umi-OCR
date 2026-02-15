# ===============================================
# =============== 图像处理插件管理器 ===============
# ===============================================

"""
图像处理插件管理器

管理图像预处理插件，支持图像增强、滤波、变换等功能。
为未来图像增强功能预留扩展接口。
"""

from typing import Dict, Any, Optional, List, Callable
from .base_manager import PluginGroupManager
from umi_log import logger


class ImagePluginManager(PluginGroupManager):
    """
    图像处理插件管理器
    
    管理所有图像预处理插件，提供统一的接口来处理图像。
    支持图像增强、滤波、几何变换、色彩调整等功能。
    
    该管理器为未来图像增强功能预留，当前可能暂无实际插件。
    
    Attributes:
        _processors: 处理器名称到处理函数的映射
        _pipeline: 默认处理流程
    """
    
    def __init__(self):
        """初始化图像处理插件管理器"""
        super().__init__("image")
        # 处理器缓存
        self._processors: Dict[str, Callable] = {}
        # 默认处理流程
        self._pipeline: List[str] = []
        
    def register_plugin(self, name: str, plugin_info: Dict[str, Any]) -> bool:
        """
        注册图像处理插件
        
        Args:
            name: 插件名称
            plugin_info: 插件信息字典，可包含:
                - api_class: 插件类
                - process_func: 处理函数（可选，如果 api_class 有 process 方法则使用该方法）
                - supported_formats: 支持的图像格式列表（可选）
                - description: 插件描述（可选）
                
        Returns:
            注册是否成功
        """
        success = super().register_plugin(name, plugin_info)
        if success:
            # 缓存处理函数
            if "process_func" in plugin_info:
                self._processors[name] = plugin_info["process_func"]
            elif "api_class" in plugin_info:
                # 检查类是否有 process 方法
                api_class = plugin_info["api_class"]
                if hasattr(api_class, "process"):
                    self._processors[name] = lambda img, cls=api_class: cls().process(img)
                    
        return success
    
    def unregister_plugin(self, name: str) -> bool:
        """
        注销图像处理插件
        
        Args:
            name: 插件名称
            
        Returns:
            注销是否成功
        """
        if name in self._processors:
            del self._processors[name]
        if name in self._pipeline:
            self._pipeline.remove(name)
            
        return super().unregister_plugin(name)
    
    def get_processor(self, name: str) -> Optional[Callable]:
        """
        获取指定名称的图像处理器
        
        Args:
            name: 处理器名称
            
        Returns:
            处理函数，不存在则返回 None
        """
        return self._processors.get(name)
    
    def process_image(self, image: Any, processor_name: str, **kwargs) -> Any:
        """
        使用指定处理器处理图像
        
        Args:
            image: 输入图像
            processor_name: 处理器名称
            **kwargs: 额外的处理参数
            
        Returns:
            处理后的图像，失败返回 None 或原图
        """
        if processor_name not in self._processors:
            logger.warning(f'图像处理器 {processor_name} 不存在')
            return image
            
        try:
            processor = self._processors[processor_name]
            return processor(image, **kwargs)
        except Exception as e:
            logger.error(f'图像处理失败 ({processor_name}): {e}')
            return image
    
    def process_pipeline(self, image: Any, pipeline: Optional[List[str]] = None) -> Any:
        """
        按流程依次处理图像
        
        Args:
            image: 输入图像
            pipeline: 处理流程列表，为 None 则使用默认流程
            
        Returns:
            处理后的图像
        """
        if pipeline is None:
            pipeline = self._pipeline
            
        result = image
        for processor_name in pipeline:
            result = self.process_image(result, processor_name)
            
        return result
    
    def set_default_pipeline(self, pipeline: List[str]):
        """
        设置默认处理流程
        
        Args:
            pipeline: 处理器名称列表
        """
        # 验证所有处理器都存在
        for name in pipeline:
            if name not in self._processors:
                logger.warning(f'设置默认流程时处理器 {name} 不存在')
                
        self._pipeline = pipeline
        logger.info(f'默认图像处理流程已设置: {pipeline}')
    
    def get_default_pipeline(self) -> List[str]:
        """
        获取默认处理流程
        
        Returns:
            处理器名称列表
        """
        return self._pipeline.copy()
    
    def get_available_processors(self) -> List[str]:
        """
        获取所有可用的处理器名称
        
        Returns:
            处理器名称列表
        """
        return list(self._processors.keys())
    
    def get_processor_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定处理器的详细信息
        
        Args:
            name: 处理器名称
            
        Returns:
            处理器信息字典，不存在则返回 None
        """
        return self.get_plugin_info(name)
    
    def has_processor(self, name: str) -> bool:
        """
        检查是否存在指定的处理器
        
        Args:
            name: 处理器名称
            
        Returns:
            是否存在
        """
        return name in self._processors
    
    def get_supported_formats(self, name: str) -> List[str]:
        """
        获取指定处理器支持的图像格式
        
        Args:
            name: 处理器名称
            
        Returns:
            支持的格式列表，默认为 ['jpg', 'png', 'bmp', 'tiff']
        """
        plugin_info = self.get_plugin_info(name)
        if plugin_info and "supported_formats" in plugin_info:
            return plugin_info["supported_formats"]
        return ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp']
    
    def create_processor_instance(self, name: str, *args, **kwargs) -> Any:
        """
        创建处理器实例
        
        与 create_instance 相同，但语义更明确。
        
        Args:
            name: 处理器名称
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            处理器实例
        """
        return self.create_instance(name, *args, **kwargs)


# 全局单例实例
_image_manager = ImagePluginManager()


# 便捷的模块级函数
def get_processor(processor_name: str) -> Optional[Callable]:
    """
    获取指定名称的图像处理器
    
    Args:
        processor_name: 处理器名称
        
    Returns:
        处理函数
    """
    return _image_manager.get_processor(processor_name)


def process_image(image: Any, processor_name: str, **kwargs) -> Any:
    """
    使用指定处理器处理图像
    
    Args:
        image: 输入图像
        processor_name: 处理器名称
        **kwargs: 额外的处理参数
        
    Returns:
        处理后的图像
    """
    return _image_manager.process_image(image, processor_name, **kwargs)


def process_pipeline(image: Any, pipeline: Optional[List[str]] = None) -> Any:
    """
    按流程依次处理图像
    
    Args:
        image: 输入图像
        pipeline: 处理流程列表
        
    Returns:
        处理后的图像
    """
    return _image_manager.process_pipeline(image, pipeline)


def get_available_processors() -> List[str]:
    """
    获取所有可用的处理器名称
    
    Returns:
        处理器名称列表
    """
    return _image_manager.get_available_processors()


def has_processor(name: str) -> bool:
    """
    检查是否存在指定的处理器
    
    Args:
        name: 处理器名称
        
    Returns:
        是否存在
    """
    return _image_manager.has_processor(name)
