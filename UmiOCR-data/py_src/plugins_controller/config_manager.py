# ===========================================
# =============== 插件配置管理器 ===============
# ===========================================
"""
插件配置管理系统

提供统一的配置模式定义、验证和管理功能。
支持 Umi-OCR 的 global_options 和 local_options 配置格式。

主要组件:
    - ConfigSchema: 配置字段模式定义
    - PluginConfig: 插件配置封装
    - PluginConfigManager: 配置管理器单例
    - ValidationResult: 验证结果封装

使用示例:
    # 注册插件配置
    manager = PluginConfigManager()
    manager.register("rapidocr", global_schema, local_schema)
    
    # 验证配置
    result = manager.validate_global("rapidocr", user_config)
    if not result.is_valid:
        print(result.errors)
    
    # 获取默认配置
    defaults = manager.get_default_global("rapidocr")
"""

from typing import Dict, List, Any, Optional, Union, Callable, Type
from enum import Enum
from dataclasses import dataclass, field
import copy


# ============================================================
# 配置字段类型枚举
# ============================================================

class ConfigFieldType(str, Enum):
    """配置字段类型枚举"""
    GROUP = "group"       # 配置组（容器）
    INT = "int"           # 整数
    FLOAT = "float"       # 浮点数
    BOOL = "bool"         # 布尔值
    STR = "str"           # 字符串
    ENUM = "enum"         # 枚举选项
    ARRAY = "array"       # 数组
    DICT = "dict"         # 字典


# ============================================================
# 验证结果类
# ============================================================

@dataclass
class ValidationResult:
    """
    配置验证结果
    
    属性:
        is_valid: 验证是否通过
        errors: 错误信息列表
        warnings: 警告信息列表
        field_errors: 按字段组织的错误信息
        
    示例:
        result = ValidationResult()
        result.add_error("字段 'numThread' 必须是整数")
        result.add_warning("字段 'timeout' 使用默认值")
    """
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field_errors: Dict[str, List[str]] = field(default_factory=dict)
    
    def add_error(self, message: str, field: Optional[str] = None) -> None:
        """
        添加错误信息
        
        Args:
            message: 错误描述
            field: 相关字段名（可选）
        """
        self.is_valid = False
        self.errors.append(message)
        if field:
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].append(message)
    
    def add_warning(self, message: str, field: Optional[str] = None) -> None:
        """
        添加警告信息
        
        Args:
            message: 警告描述
            field: 相关字段名（可选）
        """
        self.warnings.append(message)
    
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """
        合并另一个验证结果
        
        Args:
            other: 另一个 ValidationResult 实例
            
        Returns:
            合并后的新 ValidationResult 实例
        """
        result = ValidationResult()
        result.is_valid = self.is_valid and other.is_valid
        result.errors = self.errors + other.errors
        result.warnings = self.warnings + other.warnings
        result.field_errors = copy.deepcopy(self.field_errors)
        for field, errors in other.field_errors.items():
            if field not in result.field_errors:
                result.field_errors[field] = []
            result.field_errors[field].extend(errors)
        return result
    
    def __bool__(self) -> bool:
        """布尔值表示验证是否通过"""
        return self.is_valid
    
    def __repr__(self) -> str:
        status = "通过" if self.is_valid else "失败"
        return f"ValidationResult({status}, errors={len(self.errors)}, warnings={len(self.warnings)})"


# ============================================================
# 配置模式类
# ============================================================

class ConfigSchema:
    """
    配置字段模式定义
    
    定义单个配置字段的元数据、约束和验证规则。
    兼容 Umi-OCR 的 global_options/local_options 格式。
    
    属性:
        field_type: 字段类型（group, int, float, bool, str, enum）
        title: 显示标题（用于UI展示）
        default: 默认值
        description: 字段描述/提示信息
        options: 选项列表（用于enum类型）
        min: 最小值（用于数值类型）
        max: 最大值（用于数值类型）
        tool_tip: 工具提示信息
        is_int: 是否强制转换为整数（用于数值类型）
        
    示例:
        # 整数配置
        schema = ConfigSchema(
            field_type=ConfigFieldType.INT,
            title="线程数",
            default=4,
            min=1,
            max=16,
            description="OCR识别线程数"
        )
        
        # 枚举配置
        schema = ConfigSchema(
            field_type=ConfigFieldType.ENUM,
            title="语言",
            default="简体中文",
            options=[["简体中文", "简体中文"], ["English", "English"]]
        )
        
        # 配置组
        schema = ConfigSchema(
            field_type=ConfigFieldType.GROUP,
            title="RapidOCR设置",
            description="全局配置组"
        )
    """
    
    def __init__(
        self,
        field_type: Union[str, ConfigFieldType] = ConfigFieldType.STR,
        title: str = "",
        default: Any = None,
        description: str = "",
        options: Optional[List[List[Any]]] = None,
        min: Optional[Union[int, float]] = None,
        max: Optional[Union[int, float]] = None,
        tool_tip: str = "",
        is_int: bool = False,
        **kwargs
    ):
        """
        初始化配置模式
        
        Args:
            field_type: 字段类型
            title: 显示标题
            default: 默认值
            description: 字段描述
            options: 选项列表 [[值, 显示名], ...]
            min: 最小值
            max: 最大值
            tool_tip: 工具提示
            is_int: 是否强制整数
            **kwargs: 扩展属性
        """
        # 处理字符串类型的 field_type
        if isinstance(field_type, str):
            try:
                self.field_type = ConfigFieldType(field_type)
            except ValueError:
                self.field_type = ConfigFieldType.STR
        else:
            self.field_type = field_type
            
        self.title = title
        self.default = default
        self.description = description or tool_tip  # 兼容两种描述字段
        self.tool_tip = tool_tip or description
        self.options = options or []
        self.min = min
        self.max = max
        self.is_int = is_int
        self.extra = kwargs  # 保存额外的属性
        
        # 子字段（用于GROUP类型）
        self.sub_schemas: Dict[str, 'ConfigSchema'] = {}
    
    def add_sub_schema(self, name: str, schema: 'ConfigSchema') -> None:
        """
        添加子字段模式（用于配置组）
        
        Args:
            name: 子字段名
            schema: 子字段模式
        """
        self.sub_schemas[name] = schema
    
    def get_sub_schema(self, name: str) -> Optional['ConfigSchema']:
        """
        获取子字段模式
        
        Args:
            name: 子字段名
            
        Returns:
            ConfigSchema 实例或 None
        """
        return self.sub_schemas.get(name)
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """
        验证值是否符合模式定义
        
        Args:
            value: 要验证的值
            field_name: 字段名（用于错误报告）
            
        Returns:
            ValidationResult 验证结果
        """
        result = ValidationResult()
        
        # 如果是None且有默认值，使用默认值进行验证
        if value is None and self.default is not None:
            value = self.default
        
        # 根据类型进行验证
        if self.field_type == ConfigFieldType.GROUP:
            # 配置组类型 - 验证字典
            if not isinstance(value, dict):
                result.add_error(f"字段 '{field_name}' 必须是字典类型", field_name)
                return result
            # 验证子字段（仅验证提供的字段，可选字段未提供时跳过）
            for sub_name, sub_schema in self.sub_schemas.items():
                sub_value = value.get(sub_name)
                # 如果字段未提供且没有默认值，跳过验证（视为可选）
                if sub_value is None and sub_schema.default is None:
                    continue
                sub_result = sub_schema.validate(sub_value, f"{field_name}.{sub_name}" if field_name else sub_name)
                result = result.merge(sub_result)
                
        elif self.field_type == ConfigFieldType.INT:
            # 整数类型验证
            if not isinstance(value, (int, float)):
                result.add_error(f"字段 '{field_name}' 必须是数字类型", field_name)
            else:
                # 转换为整数
                try:
                    int_value = int(value)
                    # 范围验证
                    if self.min is not None and int_value < self.min:
                        result.add_error(
                            f"字段 '{field_name}' 的值 {int_value} 小于最小值 {self.min}", 
                            field_name
                        )
                    if self.max is not None and int_value > self.max:
                        result.add_error(
                            f"字段 '{field_name}' 的值 {int_value} 大于最大值 {self.max}", 
                            field_name
                        )
                except (ValueError, TypeError):
                    result.add_error(f"字段 '{field_name}' 无法转换为整数", field_name)
                    
        elif self.field_type == ConfigFieldType.FLOAT:
            # 浮点数类型验证
            if not isinstance(value, (int, float)):
                result.add_error(f"字段 '{field_name}' 必须是数字类型", field_name)
            else:
                float_value = float(value)
                # 范围验证
                if self.min is not None and float_value < self.min:
                    result.add_error(
                        f"字段 '{field_name}' 的值 {float_value} 小于最小值 {self.min}", 
                        field_name
                    )
                if self.max is not None and float_value > self.max:
                    result.add_error(
                        f"字段 '{field_name}' 的值 {float_value} 大于最大值 {self.max}", 
                        field_name
                    )
                    
        elif self.field_type == ConfigFieldType.BOOL:
            # 布尔类型验证
            if not isinstance(value, bool):
                # 尝试转换
                if isinstance(value, str):
                    if value.lower() in ('true', '1', 'yes', 'on'):
                        pass  # 可以转换
                    elif value.lower() in ('false', '0', 'no', 'off'):
                        pass  # 可以转换
                    else:
                        result.add_warning(f"字段 '{field_name}' 的布尔值格式不规范", field_name)
                else:
                    result.add_warning(f"字段 '{field_name}' 的类型应为布尔值", field_name)
                    
        elif self.field_type == ConfigFieldType.STR:
            # 字符串类型验证
            if value is not None and not isinstance(value, str):
                result.add_warning(f"字段 '{field_name}' 的类型应为字符串", field_name)
                
        elif self.field_type == ConfigFieldType.ENUM:
            # 枚举类型验证
            if self.options:
                valid_values = [opt[0] for opt in self.options]
                if value not in valid_values:
                    result.add_error(
                        f"字段 '{field_name}' 的值 '{value}' 不在有效选项中: {valid_values}", 
                        field_name
                    )
                    
        elif self.field_type == ConfigFieldType.ARRAY:
            # 数组类型验证
            if not isinstance(value, list):
                result.add_error(f"字段 '{field_name}' 必须是数组类型", field_name)
                
        elif self.field_type == ConfigFieldType.DICT:
            # 字典类型验证
            if not isinstance(value, dict):
                result.add_error(f"字段 '{field_name}' 必须是字典类型", field_name)
        
        return result
    
    def cast_value(self, value: Any) -> Any:
        """
        将值转换为正确的类型
        
        Args:
            value: 原始值
            
        Returns:
            转换后的值
        """
        if value is None:
            return self.default
            
        try:
            if self.field_type == ConfigFieldType.INT or self.is_int:
                return int(float(value))
            elif self.field_type == ConfigFieldType.FLOAT:
                return float(value)
            elif self.field_type == ConfigFieldType.BOOL:
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif self.field_type == ConfigFieldType.STR:
                return str(value)
            elif self.field_type == ConfigFieldType.GROUP and isinstance(value, dict):
                # 递归转换子字段
                result = {}
                for key, val in value.items():
                    if key in self.sub_schemas:
                        result[key] = self.sub_schemas[key].cast_value(val)
                    else:
                        result[key] = val
                return result
        except (ValueError, TypeError):
            pass
            
        return value
    
    def get_default_value(self) -> Any:
        """
        获取默认值
        
        Returns:
            默认值（会进行深拷贝）
        """
        if self.field_type == ConfigFieldType.GROUP:
            # 为配置组构建默认字典
            defaults = {}
            for name, schema in self.sub_schemas.items():
                defaults[name] = schema.get_default_value()
            return defaults
        return copy.deepcopy(self.default)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigSchema':
        """
        从字典创建配置模式
        
        兼容 Umi-OCR 的 global_options/local_options 格式。
        
        Args:
            data: 配置字典
            
        Returns:
            ConfigSchema 实例
            
        示例:
            data = {
                "title": "线程数",
                "type": "group",
                "numThread": {
                    "title": "线程数",
                    "default": 8,
                    "min": 1,
                    "isInt": True,
                },
            }
            schema = ConfigSchema.from_dict(data)
        """
        # 提取基本属性
        field_type = data.get("type", "str")
        title = data.get("title", "")
        default = data.get("default")
        description = data.get("description", data.get("toolTip", ""))
        tool_tip = data.get("toolTip", data.get("description", ""))
        options = data.get("optionsList", data.get("options", None))
        min_val = data.get("min")
        max_val = data.get("max")
        is_int = data.get("isInt", False)
        
        # 智能推断类型
        # 如果 isInt=True 或设置了 min/max，推断为 int 类型
        if field_type == "str" and (is_int or min_val is not None or max_val is not None):
            field_type = "int"
        # 如果 default 是布尔值且未指定类型，推断为 bool 类型
        elif field_type == "str" and isinstance(default, bool):
            field_type = "bool"
        # 如果有 optionsList 且未指定类型，推断为 enum 类型
        elif field_type == "str" and options is not None:
            field_type = "enum"
        
        schema = cls(
            field_type=field_type,
            title=title,
            default=default,
            description=description,
            tool_tip=tool_tip,
            options=options,
            min=min_val,
            max=max_val,
            is_int=is_int
        )
        
        # 如果是配置组，递归解析子字段
        if field_type == "group":
            for key, value in data.items():
                if key not in ("title", "type", "default", "description", "toolTip", 
                              "optionsList", "options", "min", "max", "isInt"):
                    if isinstance(value, dict):
                        sub_schema = cls.from_dict(value)
                        schema.add_sub_schema(key, sub_schema)
        
        return schema
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            兼容 Umi-OCR 的字典格式
        """
        result = {
            "type": self.field_type.value,
            "title": self.title,
        }
        
        if self.default is not None:
            result["default"] = self.default
        if self.description:
            result["toolTip"] = self.description
        if self.options:
            result["optionsList"] = self.options
        if self.min is not None:
            result["min"] = self.min
        if self.max is not None:
            result["max"] = self.max
        if self.is_int:
            result["isInt"] = True
            
        # 添加子字段
        for name, sub_schema in self.sub_schemas.items():
            result[name] = sub_schema.to_dict()
            
        return result


# ============================================================
# 插件配置类
# ============================================================

class PluginConfig:
    """
    插件配置封装
    
    封装单个插件的配置模式，包括全局配置和局部配置。
    
    属性:
        plugin_id: 插件唯一标识符
        global_schema: 全局配置模式字典
        local_schema: 局部配置模式字典
        
    示例:
        config = PluginConfig(
            plugin_id="rapidocr",
            global_schema={"numThread": {...}},
            local_schema={"language": {...}}
        )
        defaults = config.get_global_default()
    """
    
    def __init__(
        self,
        plugin_id: str,
        global_schema: Optional[Dict[str, Any]] = None,
        local_schema: Optional[Dict[str, Any]] = None
    ):
        """
        初始化插件配置
        
        Args:
            plugin_id: 插件ID
            global_schema: 全局配置模式字典或ConfigSchema
            local_schema: 局部配置模式字典或ConfigSchema
        """
        self.plugin_id = plugin_id
        
        # 转换全局配置模式
        if global_schema is None:
            self.global_schema: Optional[ConfigSchema] = None
        elif isinstance(global_schema, ConfigSchema):
            self.global_schema = global_schema
        else:
            self.global_schema = ConfigSchema.from_dict(global_schema)
            
        # 转换局部配置模式
        if local_schema is None:
            self.local_schema: Optional[ConfigSchema] = None
        elif isinstance(local_schema, ConfigSchema):
            self.local_schema = local_schema
        else:
            self.local_schema = ConfigSchema.from_dict(local_schema)
    
    def get_global_default(self) -> Dict[str, Any]:
        """
        获取全局默认配置
        
        Returns:
            默认配置字典
        """
        if self.global_schema:
            return self.global_schema.get_default_value() or {}
        return {}
    
    def get_local_default(self) -> Dict[str, Any]:
        """
        获取局部默认配置
        
        Returns:
            默认配置字典
        """
        if self.local_schema:
            return self.local_schema.get_default_value() or {}
        return {}
    
    def validate_global(self, config: Dict[str, Any]) -> ValidationResult:
        """
        验证全局配置
        
        Args:
            config: 要验证的配置字典
            
        Returns:
            ValidationResult 验证结果
        """
        if self.global_schema:
            return self.global_schema.validate(config)
        return ValidationResult()
    
    def validate_local(self, config: Dict[str, Any]) -> ValidationResult:
        """
        验证局部配置
        
        Args:
            config: 要验证的配置字典
            
        Returns:
            ValidationResult 验证结果
        """
        if self.local_schema:
            return self.local_schema.validate(config)
        return ValidationResult()
    
    def cast_global(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换全局配置值为正确类型
        
        Args:
            config: 原始配置字典
            
        Returns:
            类型转换后的配置字典
        """
        if self.global_schema:
            return self.global_schema.cast_value(config) or config
        return config
    
    def cast_local(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换局部配置值为正确类型
        
        Args:
            config: 原始配置字典
            
        Returns:
            类型转换后的配置字典
        """
        if self.local_schema:
            return self.local_schema.cast_value(config) or config
        return config


# ============================================================
# 配置管理器（单例）
# ============================================================

class PluginConfigManager:
    """
    插件配置管理器（单例模式）
    
    管理所有插件的配置模式，提供统一的配置注册、验证和查询接口。
    
    使用示例:
        # 获取管理器实例
        manager = PluginConfigManager()
        
        # 注册插件配置
        manager.register("rapidocr", global_schema, local_schema)
        
        # 验证配置
        result = manager.validate_global("rapidocr", user_config)
        if not result.is_valid:
            print("配置错误:", result.errors)
        
        # 应用配置
        manager.apply_global("rapidocr", validated_config)
        
        # 获取当前配置
        current = manager.get_global("rapidocr")
    """
    
    _instance: Optional['PluginConfigManager'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'PluginConfigManager':
        """实现单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器"""
        if PluginConfigManager._initialized:
            return
            
        self._configs: Dict[str, PluginConfig] = {}
        self._global_configs: Dict[str, Dict[str, Any]] = {}
        self._validators: Dict[str, Callable] = {}
        PluginConfigManager._initialized = True
    
    def register(
        self,
        plugin_id: str,
        global_schema: Optional[Dict[str, Any]] = None,
        local_schema: Optional[Dict[str, Any]] = None
    ) -> PluginConfig:
        """
        注册插件配置
        
        Args:
            plugin_id: 插件唯一标识符
            global_schema: 全局配置模式字典
            local_schema: 局部配置模式字典
            
        Returns:
            创建的 PluginConfig 实例
            
        示例:
            manager.register(
                "rapidocr",
                global_schema={
                    "title": "RapidOCR",
                    "type": "group",
                    "numThread": {"title": "线程数", "default": 8, "min": 1, "isInt": True}
                },
                local_schema={
                    "title": "识别设置",
                    "type": "group",
                    "language": {"title": "语言", "optionsList": [["zh", "中文"], ["en", "英文"]]}
                }
            )
        """
        config = PluginConfig(plugin_id, global_schema, local_schema)
        self._configs[plugin_id] = config
        # 初始化全局配置存储
        if plugin_id not in self._global_configs:
            self._global_configs[plugin_id] = config.get_global_default()
        return config
    
    def unregister(self, plugin_id: str) -> bool:
        """
        注销插件配置
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            是否成功注销
        """
        if plugin_id in self._configs:
            del self._configs[plugin_id]
            if plugin_id in self._global_configs:
                del self._global_configs[plugin_id]
            return True
        return False
    
    def get_config(self, plugin_id: str) -> Optional[PluginConfig]:
        """
        获取插件配置对象
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            PluginConfig 实例或 None
        """
        return self._configs.get(plugin_id)
    
    def validate_global(self, plugin_id: str, config: Dict[str, Any]) -> ValidationResult:
        """
        验证全局配置
        
        Args:
            plugin_id: 插件ID
            config: 要验证的配置字典
            
        Returns:
            ValidationResult 验证结果
        """
        plugin_config = self._configs.get(plugin_id)
        if plugin_config:
            return plugin_config.validate_global(config)
        return ValidationResult(
            is_valid=False,
            errors=[f"插件 '{plugin_id}' 未注册配置模式"]
        )
    
    def validate_local(self, plugin_id: str, config: Dict[str, Any]) -> ValidationResult:
        """
        验证局部配置
        
        Args:
            plugin_id: 插件ID
            config: 要验证的配置字典
            
        Returns:
            ValidationResult 验证结果
        """
        plugin_config = self._configs.get(plugin_id)
        if plugin_config:
            return plugin_config.validate_local(config)
        return ValidationResult(
            is_valid=False,
            errors=[f"插件 '{plugin_id}' 未注册配置模式"]
        )
    
    def get_default_global(self, plugin_id: str) -> Dict[str, Any]:
        """
        获取默认全局配置
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            默认配置字典
        """
        plugin_config = self._configs.get(plugin_id)
        if plugin_config:
            return plugin_config.get_global_default()
        return {}
    
    def get_default_local(self, plugin_id: str) -> Dict[str, Any]:
        """
        获取默认局部配置
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            默认配置字典
        """
        plugin_config = self._configs.get(plugin_id)
        if plugin_config:
            return plugin_config.get_local_default()
        return {}
    
    def apply_global(self, plugin_id: str, config: Dict[str, Any]) -> ValidationResult:
        """
        应用全局配置
        
        先验证配置，如果通过则保存到当前配置存储。
        
        Args:
            plugin_id: 插件ID
            config: 要应用的配置字典
            
        Returns:
            ValidationResult 验证结果
        """
        # 验证配置
        result = self.validate_global(plugin_id, config)
        if not result.is_valid:
            return result
            
        # 类型转换
        plugin_config = self._configs.get(plugin_id)
        if plugin_config:
            config = plugin_config.cast_global(config)
            
        # 保存配置
        self._global_configs[plugin_id] = config
        return result
    
    def get_global(self, plugin_id: str) -> Dict[str, Any]:
        """
        获取当前全局配置
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            当前配置字典，如果未设置则返回默认值
        """
        if plugin_id in self._global_configs:
            return self._global_configs[plugin_id]
        return self.get_default_global(plugin_id)
    
    def set_global(self, plugin_id: str, config: Dict[str, Any]) -> ValidationResult:
        """
        设置全局配置（apply_global 的别名）
        
        Args:
            plugin_id: 插件ID
            config: 配置字典
            
        Returns:
            ValidationResult 验证结果
        """
        return self.apply_global(plugin_id, config)
    
    def get_all_plugin_ids(self) -> List[str]:
        """
        获取所有已注册的插件ID
        
        Returns:
            插件ID列表
        """
        return list(self._configs.keys())
    
    def has_config(self, plugin_id: str) -> bool:
        """
        检查插件是否已注册配置
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            是否已注册
        """
        return plugin_id in self._configs
    
    def clear(self) -> None:
        """清空所有配置（主要用于测试）"""
        self._configs.clear()
        self._global_configs.clear()
    
    @classmethod
    def reset_instance(cls) -> None:
        """重置单例实例（主要用于测试）"""
        cls._instance = None
        cls._initialized = False


# ============================================================
# 便捷函数
# ============================================================

def register_plugin_config(
    plugin_id: str,
    global_schema: Optional[Dict[str, Any]] = None,
    local_schema: Optional[Dict[str, Any]] = None
) -> PluginConfig:
    """
    便捷函数：注册插件配置
    
    Args:
        plugin_id: 插件ID
        global_schema: 全局配置模式
        local_schema: 局部配置模式
        
    Returns:
        PluginConfig 实例
    """
    manager = PluginConfigManager()
    return manager.register(plugin_id, global_schema, local_schema)


def validate_plugin_config(
    plugin_id: str,
    config: Dict[str, Any],
    config_type: str = "global"
) -> ValidationResult:
    """
    便捷函数：验证插件配置
    
    Args:
        plugin_id: 插件ID
        config: 配置字典
        config_type: "global" 或 "local"
        
    Returns:
        ValidationResult 验证结果
    """
    manager = PluginConfigManager()
    if config_type == "global":
        return manager.validate_global(plugin_id, config)
    else:
        return manager.validate_local(plugin_id, config)


# ============================================================
# 单元测试
# ============================================================

def _run_tests():
    """运行单元测试"""
    print("=" * 60)
    print("运行 config_manager.py 单元测试")
    print("=" * 60)
    
    # 重置单例
    PluginConfigManager.reset_instance()
    
    # 测试数据：模拟 RapidOCR 配置
    rapidocr_global = {
        "title": "RapidOCR（本地）",
        "type": "group",
        "numThread": {
            "title": "线程数",
            "default": 8,
            "min": 1,
            "isInt": True,
        },
    }
    
    rapidocr_local = {
        "title": "文字识别（RapidOCR）",
        "type": "group",
        "language": {
            "title": "语言/模型库",
            "optionsList": [
                ["简体中文(V4)", "简体中文(V4)"],
                ["English(V4)", "English(V4)"],
            ],
        },
        "angle": {
            "title": "纠正文本方向",
            "default": False,
            "toolTip": "启用方向分类，识别倾斜或倒置的文本。",
        },
        "maxSideLen": {
            "title": "限制图像边长",
            "optionsList": [
                [1024, "1024（默认）"],
                [2048, "2048"],
                [4096, "4096"],
                [999999, "无限制"],
            ],
        },
    }
    
    # 测试 1: 注册配置
    print("\n[测试 1] 注册插件配置")
    manager = PluginConfigManager()
    config = manager.register("rapidocr", rapidocr_global, rapidocr_local)
    assert config.plugin_id == "rapidocr"
    print("  ✓ 注册成功")
    
    # 测试 2: 获取默认配置
    print("\n[测试 2] 获取默认配置")
    global_default = manager.get_default_global("rapidocr")
    assert global_default.get("numThread") == 8
    local_default = manager.get_default_local("rapidocr")
    assert local_default.get("angle") == False
    print(f"  ✓ 全局默认: {global_default}")
    print(f"  ✓ 局部默认: {local_default}")
    
    # 测试 3: 验证有效配置
    print("\n[测试 3] 验证有效配置")
    valid_global = {"numThread": 4}
    result = manager.validate_global("rapidocr", valid_global)
    assert result.is_valid
    print(f"  ✓ 验证通过: {valid_global}")
    
    # 测试 4: 验证无效配置（超出范围）
    print("\n[测试 4] 验证无效配置（超出范围）")
    invalid_global = {"numThread": 0}
    result = manager.validate_global("rapidocr", invalid_global)
    assert not result.is_valid
    assert len(result.errors) > 0
    print(f"  ✓ 正确检测到错误: {result.errors}")
    
    # 测试 5: 验证局部配置（枚举）
    print("\n[测试 5] 验证局部配置（枚举）")
    valid_local = {"language": "简体中文(V4)", "angle": True}
    print(f"  Debug: calling validate_local with {valid_local}")
    result = manager.validate_local("rapidocr", valid_local)
    print(f"  Debug: result={result}, is_valid={result.is_valid}, errors={result.errors}")
    assert result.is_valid, f"Expected valid, got errors: {result.errors}"
    print(f"  ✓ 验证通过: {valid_local}")
    
    # 测试 6: 验证无效枚举值
    print("\n[测试 6] 验证无效枚举值")
    invalid_local = {"language": "无效语言"}
    result = manager.validate_local("rapidocr", invalid_local)
    assert not result.is_valid
    print(f"  ✓ 正确检测到错误: {result.errors}")
    
    # 测试 7: 应用配置
    print("\n[测试 7] 应用配置")
    result = manager.apply_global("rapidocr", {"numThread": 16})
    assert result.is_valid
    current = manager.get_global("rapidocr")
    assert current.get("numThread") == 16
    print(f"  ✓ 应用成功，当前配置: {current}")
    
    # 测试 8: 类型转换
    print("\n[测试 8] 类型转换")
    # float -> int
    result = manager.apply_global("rapidocr", {"numThread": 8.5})
    current = manager.get_global("rapidocr")
    assert current.get("numThread") == 8
    print(f"  ✓ float->int 转换成功: 8.5 -> {current.get('numThread')}")
    
    # 测试 9: ConfigSchema.from_dict
    print("\n[测试 9] 从字典创建模式")
    schema_dict = {
        "title": "测试配置",
        "type": "group",
        "enabled": {
            "title": "启用功能",
            "default": True,
            "type": "bool",
        },
        "threshold": {
            "title": "阈值",
            "default": 0.5,
            "min": 0.0,
            "max": 1.0,
        },
    }
    schema = ConfigSchema.from_dict(schema_dict)
    assert schema.field_type == ConfigFieldType.GROUP
    assert "enabled" in schema.sub_schemas
    print(f"  ✓ 模式创建成功，子字段: {list(schema.sub_schemas.keys())}")
    
    # 测试 10: 便捷函数
    print("\n[测试 10] 便捷函数")
    PluginConfigManager.reset_instance()
    register_plugin_config("test_plugin", rapidocr_global, rapidocr_local)
    result = validate_plugin_config("test_plugin", {"numThread": 4})
    assert result.is_valid
    print(f"  ✓ 便捷函数工作正常")
    
    # 测试 11: ValidationResult 合并
    print("\n[测试 11] ValidationResult 合并")
    r1 = ValidationResult(is_valid=True)
    r1.add_warning("警告1")
    r2 = ValidationResult(is_valid=False)
    r2.add_error("错误1")
    merged = r1.merge(r2)
    assert not merged.is_valid
    assert len(merged.errors) == 1
    assert len(merged.warnings) == 1
    print(f"  ✓ 合并结果: errors={merged.errors}, warnings={merged.warnings}")
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    _run_tests()
