# ===============================================
# =============== 插件基类定义 ==================
# ===============================================

"""
Umi-OCR 插件系统基类定义模块

本模块定义了所有插件类型的抽象基类，提供统一的接口规范和类型检查机制。
支持旧式插件的向后兼容性，允许不继承基类的插件通过鸭子类型兼容。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum


# ============================================================
# 类型定义
# ============================================================

class PluginGroup(str, Enum):
    """插件组类型枚举"""
    OCR = "ocr"           # OCR引擎插件
    OUTPUT = "output"     # 输出格式插件
    TBPU = "tbpu"         # 文本后处理插件
    IMAGE = "image"       # 图像处理插件


# 插件信息字典类型
PluginInfoDict = Dict[str, Any]

# OCR结果类型
OcrResult = Dict[str, Any]

# 文本块类型
TextBlock = Dict[str, Any]


# ============================================================
# 向后兼容性检查工具
# ============================================================

def _has_required_methods(obj: Any, methods: List[str]) -> bool:
    """
    检查对象是否实现了必需的方法列表（鸭子类型检查）
    
    Args:
        obj: 要检查的对象
        methods: 必需的方法名列表
        
    Returns:
        是否实现了所有必需方法
    """
    return all(callable(getattr(obj, method, None)) for method in methods)


# ============================================================
# 基础插件类
# ============================================================

class BasePlugin(ABC):
    """
    所有插件的抽象基类
    
    所有Umi-OCR插件必须继承此类或实现相同的接口。
    提供插件生命周期管理、配置管理和信息查询的统一接口。
    
    必需类属性:
        PluginInfo (dict): 插件信息字典，包含以下键：
            - id (str): 插件唯一标识符
            - name (str): 插件显示名称
            - version (str): 版本号，如 "1.0.0"
            - author (str): 作者信息
            - description (str): 插件描述
            - group (str): 所属组 ("ocr"/"output"/"tbpu"/"image")
            - dependencies (list): 依赖插件ID列表
            - global_options (dict|None): 全局配置选项
            - local_options (dict|None): 局部配置选项
    
    示例:
        ```python
        class MyPlugin(BasePlugin):
            PluginInfo = {
                "id": "my_plugin",
                "name": "我的插件",
                "version": "1.0.0",
                "author": "作者名",
                "description": "插件描述",
                "group": "ocr",
                "dependencies": [],
                "global_options": None,
                "local_options": None,
            }
            
            def initialize(self, config: dict) -> bool:
                # 初始化逻辑
                return True
                
            def shutdown(self) -> None:
                # 关闭逻辑
                pass
        ```
    """
    
    # 插件信息字典，子类必须定义
    PluginInfo: Optional[PluginInfoDict] = None
    
    def __init__(self):
        """初始化插件基类"""
        self._initialized = False
        self._config: Dict[str, Any] = {}
        self._enabled = True
    
    @property
    def plugin_info(self) -> PluginInfoDict:
        """
        获取插件信息字典
        
        Returns:
            包含插件元信息的字典
            
        Raises:
            AttributeError: 如果子类未定义 PluginInfo
        """
        if self.PluginInfo is None:
            raise AttributeError(
                f"插件类 {self.__class__.__name__} 必须定义 PluginInfo 属性"
            )
        return self.PluginInfo
    
    @property
    def plugin_id(self) -> str:
        """获取插件唯一标识符"""
        return self.plugin_info.get("id", "")
    
    @property
    def plugin_name(self) -> str:
        """获取插件显示名称"""
        return self.plugin_info.get("name", "")
    
    @property
    def plugin_group(self) -> str:
        """获取插件所属组"""
        return self.plugin_info.get("group", "")
    
    @property
    def is_initialized(self) -> bool:
        """检查插件是否已初始化"""
        return self._initialized
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件
        
        在插件加载完成后调用，用于执行初始化逻辑。
        子类应重写此方法实现自定义初始化。
        
        Args:
            config: 全局配置字典
            
        Returns:
            初始化是否成功
        """
        self._config = config or {}
        self._initialized = True
        return True
    
    @abstractmethod
    def shutdown(self) -> None:
        """
        关闭插件
        
        在插件卸载或程序退出时调用，用于释放资源。
        子类应重写此方法实现自定义清理逻辑。
        """
        self._initialized = False
        self._config = {}
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        return self._config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """
        设置配置项
        
        Args:
            key: 配置键名
            value: 配置值
        """
        self._config[key] = value
    
    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        """
        支持鸭子类型的子类检查
        
        允许不继承 BasePlugin 但实现了相同接口的类被视为插件。
        """
        if cls is BasePlugin:
            required_attrs = ["PluginInfo"]
            if all(hasattr(subclass, attr) for attr in required_attrs):
                return True
        return NotImplemented


# ============================================================
# OCR引擎插件基类
# ============================================================

class OcrPlugin(BasePlugin):
    """
    OCR引擎插件基类
    
    用于实现OCR文本识别功能的插件。子类必须实现OCR引擎的
    启动、停止和识别方法。
    
    必需方法:
        - __init__(globalArgd): 接收全局配置初始化
        - start(argd) -> str: 启动引擎
        - stop(): 停止引擎
        - runPath(imgPath) -> dict: 图片路径识别
        - runBytes(imageBytes) -> dict: 字节流识别
        - runBase64(imageBase64) -> dict: Base64识别
    
    示例:
        ```python
        class MyOcrPlugin(OcrPlugin):
            PluginInfo = {
                "id": "my_ocr",
                "name": "我的OCR引擎",
                "group": "ocr",
                # ... 其他信息
            }
            
            def __init__(self, globalArgd: dict):
                super().__init__()
                self.api = None
                
            def start(self, argd: dict) -> str:
                # 启动引擎
                return ""  # 空字符串表示成功
                
            def runPath(self, imgPath: str) -> dict:
                # 执行识别
                return {"code": 100, "data": [...]}
        ```
    
    向后兼容:
        支持旧式插件类（如只定义了 Api 类而无继承的情况），
        只要实现了必要的方法即可通过鸭子类型兼容。
    """
    
    def __init__(self, globalArgd: Dict[str, Any]):
        """
        初始化OCR插件
        
        Args:
            globalArgd: 全局配置字典，包含 numThread 等参数
        """
        super().__init__()
        self._global_argd = globalArgd
        self._api_instance: Optional[Any] = None
    
    @abstractmethod
    def start(self, argd: Dict[str, Any]) -> str:
        """
        启动OCR引擎
        
        根据配置参数启动OCR引擎实例。
        
        Args:
            argd: 局部配置字典，包含：
                - language (str): 识别语言
                - angle (bool): 是否进行角度分类
                - maxSideLen (int): 最大边长限制
                
        Returns:
            空字符串 "" 表示启动成功
            错误信息字符串（以"[Error]"开头）表示失败
            
        示例:
            ```python
            def start(self, argd):
                try:
                    self.api = MyOcrEngine(argd)
                    return ""
                except Exception as e:
                    return f"[Error] 启动失败: {e}"
            ```
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        停止OCR引擎
        
        释放OCR引擎占用的资源，关闭引擎实例。
        
        示例:
            ```python
            def stop(self):
                if self.api:
                    self.api.release()
                    self.api = None
            ```
        """
        pass
    
    @abstractmethod
    def runPath(self, imgPath: str) -> OcrResult:
        """
        对图片文件路径执行OCR识别
        
        Args:
            imgPath: 图片文件的绝对路径
            
        Returns:
            OCR结果字典，格式如下：
            ```python
            {
                "code": 100,  # 状态码：100成功，101空白，其他错误
                "data": [     # 文本块列表
                    {
                        "box": [[x1,y1], [x2,y1], [x2,y2], [x1,y2]],
                        "text": "识别的文字",
                        "score": 0.95,
                        "end": "\n"  # 结尾间隔符
                    },
                    ...
                ]
            }
            ```
            错误时返回：
            ```python
            {"code": 错误码, "data": "错误信息"}
            ```
        """
        pass
    
    @abstractmethod
    def runBytes(self, imageBytes: bytes) -> OcrResult:
        """
        对图片字节流执行OCR识别
        
        Args:
            imageBytes: 图片文件的二进制数据
            
        Returns:
            OCR结果字典，格式同 runPath
        """
        pass
    
    @abstractmethod
    def runBase64(self, imageBase64: str) -> OcrResult:
        """
        对Base64编码的图片执行OCR识别
        
        Args:
            imageBase64: Base64编码的图片字符串
            
        Returns:
            OCR结果字典，格式同 runPath
        """
        pass
    
    def get_api_instance(self, argd: Dict[str, Any]) -> "OcrPlugin":
        """
        获取OCR API实例（用于与插件控制器兼容）
        
        Args:
            argd: 配置参数
            
        Returns:
            返回自身实例（已调用start）
        """
        error = self.start(argd)
        if error:
            raise RuntimeError(f"OCR引擎启动失败: {error}")
        return self
    
    def create_instance(self, argd: Dict[str, Any]) -> "OcrPlugin":
        """
        创建实例（兼容接口）
        
        与 get_api_instance 相同，用于保持接口一致性。
        """
        return self.get_api_instance(argd)
    
    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        """
        支持旧式OCR插件的鸭子类型检查
        
        检查类是否实现了必需的方法：
        - __init__(globalArgd)
        - start(argd) -> str
        - stop()
        - runPath(imgPath) -> dict
        - runBytes(imageBytes) -> dict
        - runBase64(imageBase64) -> dict
        """
        if cls is OcrPlugin:
            required_methods = [
                "__init__", "start", "stop",
                "runPath", "runBytes", "runBase64"
            ]
            if _has_required_methods(subclass, required_methods):
                return True
        return NotImplemented


# ============================================================
# 输出格式插件基类
# ============================================================

class OutputPlugin(BasePlugin):
    """
    输出格式插件基类
    
    用于实现OCR结果输出到不同格式的插件，如纯文本、Markdown、
    JSON、CSV、PDF等。
    
    必需方法:
        - create_instance(argd) -> OutputInstance: 创建输出处理器实例
    
    输出处理器实例必须实现:
        - print(res: dict): 输出单张图片的OCR结果
        - openOutputFile(): 打开输出文件
        - onEnd(): 结束输出，清理资源
    
    示例:
        ```python
        class OutputTxtPlugin(OutputPlugin):
            PluginInfo = {
                "id": "output_txt",
                "name": "纯文本输出",
                "group": "output",
                # ...
            }
            
            def create_instance(self, argd: dict):
                return TxtOutputInstance(argd)
        
        class TxtOutputInstance:
            def __init__(self, argd):
                self.file_path = argd.get("outputDir") + "/output.txt"
                
            def print(self, res: dict):
                with open(self.file_path, "a") as f:
                    f.write(res["data"][0]["text"])
                    
            def openOutputFile(self):
                os.startfile(self.file_path)
                
            def onEnd(self):
                pass
        ```
    """
    
    def __init__(self):
        """初始化输出插件"""
        super().__init__()
        self._instance: Optional[Any] = None
    
    @abstractmethod
    def create_instance(self, argd: Dict[str, Any]) -> Any:
        """
        创建输出处理器实例
        
        Args:
            argd: 输出配置参数，包含：
                - outputDir (str): 输出目录
                - outputFileName (str): 输出文件名
                - startDatetime (str): 开始时间
                - ignoreBlank (bool): 是否忽略空白结果
                - ... 其他格式特定参数
                
        Returns:
            输出处理器实例，必须实现以下方法：
            - print(res: dict): 输出单张图片结果
            - openOutputFile(): 打开输出文件
            - onEnd(): 结束输出
            
        示例:
            ```python
            def create_instance(self, argd):
                return MyOutputHandler(argd)
            ```
        """
        pass
    
    def get_api_instance(self, argd: Dict[str, Any]) -> Any:
        """
        获取输出处理器实例（兼容接口）
        
        与 create_instance 相同，用于保持与插件控制器兼容。
        """
        self._instance = self.create_instance(argd)
        return self._instance
    
    def print(self, res: Dict[str, Any]) -> None:
        """
        输出单张图片的OCR结果（代理方法）
        
        Args:
            res: OCR结果字典
        """
        if self._instance and hasattr(self._instance, "print"):
            self._instance.print(res)
    
    def openOutputFile(self) -> None:
        """打开输出文件（代理方法）"""
        if self._instance and hasattr(self._instance, "openOutputFile"):
            self._instance.openOutputFile()
    
    def onEnd(self) -> None:
        """结束输出（代理方法）"""
        if self._instance and hasattr(self._instance, "onEnd"):
            self._instance.onEnd()
    
    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        """
        支持旧式输出插件的鸭子类型检查
        
        检查类是否实现了 create_instance 方法。
        """
        if cls is OutputPlugin:
            if _has_required_methods(subclass, ["create_instance"]):
                return True
        return NotImplemented


# ============================================================
# 文本后处理插件基类
# ============================================================

class TbpuPlugin(BasePlugin):
    """
    文本后处理插件基类 (Text Block Processing Unit)
    
    用于处理OCR返回的文本块列表，进行排序、合并、格式化等后处理。
    每个文本块包含：box（包围盒）、text（文字）、score（置信度）等信息。
    
    文块处理器可以：
    - 对文本块进行排序（按阅读顺序）
    - 合并相邻的文本块
    - 添加段落结束标记
    - 过滤低置信度的文本
    
    必需方法:
        - run(textBlocks: list) -> list: 处理文本块列表
        
    或者:
        - get_api_instance(argd) -> TbpuInstance: 返回处理器实例
        - TbpuInstance.run(textBlocks) -> list: 处理方法
    
    示例:
        ```python
        class SingleParaPlugin(TbpuPlugin):
            PluginInfo = {
                "id": "single_para",
                "name": "单栏段落解析",
                "group": "tbpu",
                # ...
            }
            
            def __init__(self):
                super().__init__()
                self.tbpuName = "单栏段落"
                
            def run(self, textBlocks: list) -> list:
                # 排序
                textBlocks.sort(key=lambda tb: tb["box"][0][1])
                # 添加段落结束符
                for tb in textBlocks:
                    tb["end"] = "\n\n"
                return textBlocks
        ```
    
    向后兼容:
        兼容旧的Tbpu类（无继承关系），只要实现了run方法即可。
    """
    
    def __init__(self):
        """初始化TBPU插件"""
        super().__init__()
        self.tbpuName: str = "文块处理单元-未知"
        self._instance: Optional[Any] = None
    
    @abstractmethod
    def run(self, textBlocks: List[TextBlock]) -> List[TextBlock]:
        """
        处理文本块列表
        
        对输入的文本块进行处理，返回处理后的列表。
        可以修改文本块的顺序、内容，或添加新的字段。
        
        Args:
            textBlocks: 文本块列表，每个元素格式：
            ```python
            {
                "box": [[x1,y1], [x2,y1], [x2,y2], [x1,y2]],  # 四点坐标
                "text": "识别的文字内容",
                "score": 0.95,  # 置信度 0-1
                "end": "\n"     # 结尾间隔符（可添加）
            }
            ```
            
        Returns:
            处理后的文本块列表，每个块可能增加/修改字段：
            - end: 结尾间隔符（"\n", "\n\n", ""等）
            - normalized_bbox: 规范化后的包围盒
            
        示例:
            ```python
            def run(self, textBlocks):
                # 按垂直位置排序
                textBlocks.sort(key=lambda tb: tb["box"][0][1])
                # 设置段落结束符
                for i, tb in enumerate(textBlocks):
                    if i < len(textBlocks) - 1:
                        tb["end"] = "\n"
                    else:
                        tb["end"] = "\n\n"
                return textBlocks
            ```
        """
        pass
    
    def get_api_instance(self, argd: Dict[str, Any]) -> "TbpuPlugin":
        """
        获取TBPU实例（兼容接口）
        
        对于简单插件，可以直接返回自身。
        复杂插件可以返回专门的处理实例。
        
        Args:
            argd: 配置参数
            
        Returns:
            TBPU处理器实例
        """
        self._instance = self
        return self
    
    def create_instance(self, argd: Dict[str, Any]) -> "TbpuPlugin":
        """
        创建实例（兼容接口）
        
        与 get_api_instance 相同。
        """
        return self.get_api_instance(argd)
    
    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        """
        支持旧式TBPU插件的鸭子类型检查
        
        检查类是否实现了 run 方法。
        兼容旧的Tbpu基类。
        """
        if cls is TbpuPlugin:
            if _has_required_methods(subclass, ["run"]):
                return True
        return NotImplemented


# ============================================================
# 图像处理插件基类
# ============================================================

class ImagePlugin(BasePlugin):
    """
    图像处理插件基类
    
    用于实现图像预处理或后处理功能的插件，如图像增强、
    去噪、旋转、裁剪等操作。
    
    必需方法:
        - process(image) -> image: 处理图像
        
    图像类型可以是：
    - PIL.Image 对象
    - numpy.ndarray (OpenCV格式)
    - 其他图像表示
    
    注意：具体图像格式由插件和调用者约定，建议支持PIL和numpy。
    
    示例:
        ```python
        class DenoisePlugin(ImagePlugin):
            PluginInfo = {
                "id": "denoise",
                "name": "图像去噪",
                "group": "image",
                # ...
            }
            
            def process(self, image):
                import cv2
                return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        ```
    
    向后兼容:
        支持旧式图像处理类，只要实现了process方法即可。
    """
    
    def __init__(self):
        """初始化图像处理插件"""
        super().__init__()
        self._instance: Optional[Any] = None
    
    @abstractmethod
    def process(self, image: Any) -> Any:
        """
        处理图像
        
        对输入图像进行处理并返回处理后的图像。
        图像格式由具体插件定义，建议同时支持PIL和OpenCV格式。
        
        Args:
            image: 输入图像，通常为：
                - PIL.Image.Image: PIL图像对象
                - numpy.ndarray: OpenCV格式图像 (H, W, C) 或 (H, W)
                
        Returns:
            处理后的图像，格式与输入相同
            
        示例:
            ```python
            def process(self, image):
                # 转换为灰度图示例
                if isinstance(image, Image.Image):
                    return image.convert("L")
                elif isinstance(image, np.ndarray):
                    import cv2
                    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                return image
            ```
        """
        pass
    
    def get_api_instance(self, argd: Dict[str, Any]) -> "ImagePlugin":
        """
        获取图像处理器实例（兼容接口）
        
        Args:
            argd: 配置参数
            
        Returns:
            图像处理器实例
        """
        self._instance = self
        return self
    
    def create_instance(self, argd: Dict[str, Any]) -> "ImagePlugin":
        """
        创建实例（兼容接口）
        
        与 get_api_instance 相同。
        """
        return self.get_api_instance(argd)
    
    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        """
        支持旧式图像处理插件的鸭子类型检查
        
        检查类是否实现了 process 方法。
        """
        if cls is ImagePlugin:
            if _has_required_methods(subclass, ["process"]):
                return True
        return NotImplemented


# ============================================================
# 插件类型检查工具函数
# ============================================================

def is_plugin_class(cls: type) -> bool:
    """
    检查类是否是有效的插件类
    
    检查是否实现了PluginInfo和基本方法。
    
    Args:
        cls: 要检查的类
        
    Returns:
        是否是有效的插件类
    """
    if not hasattr(cls, "PluginInfo"):
        return False
    if not isinstance(cls.PluginInfo, dict):
        return False
    required_keys = ["id", "name", "group"]
    return all(key in cls.PluginInfo for key in required_keys)


def get_plugin_group(cls: type) -> Optional[str]:
    """
    获取插件所属组
    
    Args:
        cls: 插件类
        
    Returns:
        插件组名（ocr/output/tbpu/image）或None
    """
    if not is_plugin_class(cls):
        return None
    return cls.PluginInfo.get("group")


def check_plugin_compatibility(cls: type, group: str) -> bool:
    """
    检查插件是否与指定组兼容
    
    Args:
        cls: 插件类
        group: 期望的插件组
        
    Returns:
        是否兼容
    """
    # 检查是否继承自对应基类
    if group == "ocr":
        return issubclass(cls, OcrPlugin) or OcrPlugin.__subclasshook__(cls)
    elif group == "output":
        return issubclass(cls, OutputPlugin) or OutputPlugin.__subclasshook__(cls)
    elif group == "tbpu":
        return issubclass(cls, TbpuPlugin) or TbpuPlugin.__subclasshook__(cls)
    elif group == "image":
        return issubclass(cls, ImagePlugin) or ImagePlugin.__subclasshook__(cls)
    return False


# ============================================================
# 向后兼容：支持旧式插件的适配器
# ============================================================

class LegacyPluginAdapter:
    """
    旧式插件适配器
    
    用于包装不继承自BasePlugin的旧式插件类，
    使其兼容新的插件接口。
    
    使用方法:
        ```python
        legacy_class = OldApiClass  # 旧式类
        adapted = LegacyPluginAdapter.adapt(legacy_class, plugin_info)
        # adapted 现在继承自相应的基类
        ```
    """
    
    @staticmethod
    def adapt_ocr_plugin(legacy_class: type, plugin_info: PluginInfoDict) -> type:
        """
        将旧式OCR类适配为OcrPlugin子类
        
        Args:
            legacy_class: 旧式OCR类（实现了start/stop/runPath等方法）
            plugin_info: 插件信息字典
            
        Returns:
            适配后的类，继承自OcrPlugin
        """
        class AdaptedOcrPlugin(OcrPlugin):
            PluginInfo = plugin_info
            
            def __init__(self, globalArgd):
                super().__init__(globalArgd)
                self._legacy = legacy_class(globalArgd)
            
            def start(self, argd):
                return self._legacy.start(argd)
            
            def stop(self):
                return self._legacy.stop()
            
            def runPath(self, imgPath):
                return self._legacy.runPath(imgPath)
            
            def runBytes(self, imageBytes):
                return self._legacy.runBytes(imageBytes)
            
            def runBase64(self, imageBase64):
                return self._legacy.runBase64(imageBase64)
        
        AdaptedOcrPlugin.__name__ = legacy_class.__name__
        AdaptedOcrPlugin.__module__ = legacy_class.__module__
        return AdaptedOcrPlugin
    
    @staticmethod
    def adapt_tbpu_plugin(legacy_class: type, plugin_info: PluginInfoDict) -> type:
        """
        将旧式TBPU类适配为TbpuPlugin子类
        
        Args:
            legacy_class: 旧式TBPU类（实现了run方法）
            plugin_info: 插件信息字典
            
        Returns:
            适配后的类，继承自TbpuPlugin
        """
        class AdaptedTbpuPlugin(TbpuPlugin):
            PluginInfo = plugin_info
            
            def __init__(self):
                super().__init__()
                self._legacy = legacy_class()
                if hasattr(self._legacy, "tbpuName"):
                    self.tbpuName = self._legacy.tbpuName
            
            def run(self, textBlocks):
                return self._legacy.run(textBlocks)
        
        AdaptedTbpuPlugin.__name__ = legacy_class.__name__
        AdaptedTbpuPlugin.__module__ = legacy_class.__module__
        return AdaptedTbpuPlugin


# ============================================================
# 模块导出
# ============================================================

__all__ = [
    # 基类
    "BasePlugin",
    "OcrPlugin",
    "OutputPlugin",
    "TbpuPlugin",
    "ImagePlugin",
    # 类型
    "PluginGroup",
    "PluginInfoDict",
    "OcrResult",
    "TextBlock",
    # 工具函数
    "is_plugin_class",
    "get_plugin_group",
    "check_plugin_compatibility",
    # 适配器
    "LegacyPluginAdapter",
]
