# =============================================
# 插件依赖解析器
# =============================================

"""
插件依赖解析模块

提供完整的插件依赖管理系统，包括：
- 依赖定义与版本匹配
- 有向无环图（DAG）构建
- Kahn算法拓扑排序
- 循环依赖检测
- 错误报告
"""

import re
from typing import List, Dict, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque


# =============================================
# 版本号处理
# =============================================

class VersionError(Exception):
    """版本号相关错误"""
    pass


class Version:
    """
    版本号类，支持语义化版本（SemVer）
    
    格式: MAJOR.MINOR.PATCH[-prerelease][+build]
    示例: 1.0.0, 2.1.3-alpha, 3.0.0-beta+exp.sha.5114f85
    """
    
    def __init__(self, version_str: str):
        """
        初始化版本号
        
        Args:
            version_str: 版本字符串
            
        Raises:
            VersionError: 版本号格式无效
        """
        self._original = version_str.strip()
        self._major = 0
        self._minor = 0
        self._patch = 0
        self._prerelease = ""
        self._build = ""
        self._parse()
    
    def _parse(self):
        """解析版本字符串"""
        if not self._original:
            raise VersionError("版本号不能为空")
        
        # 正则匹配语义化版本
        pattern = r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:-([a-zA-Z0-9.]+))?(?:\+([a-zA-Z0-9.]+))?$'
        match = re.match(pattern, self._original)
        
        if not match:
            raise VersionError(f"无效的版本号格式: {self._original}")
        
        self._major = int(match.group(1))
        self._minor = int(match.group(2)) if match.group(2) else 0
        self._patch = int(match.group(3)) if match.group(3) else 0
        self._prerelease = match.group(4) or ""
        self._build = match.group(5) or ""
    
    @property
    def major(self) -> int:
        """主版本号"""
        return self._major
    
    @property
    def minor(self) -> int:
        """次版本号"""
        return self._minor
    
    @property
    def patch(self) -> int:
        """修订号"""
        return self._patch
    
    @property
    def prerelease(self) -> str:
        """预发布版本标识"""
        return self._prerelease
    
    @property
    def is_prerelease(self) -> bool:
        """是否为预发布版本"""
        return bool(self._prerelease)
    
    @property
    def tuple(self) -> Tuple[int, int, int]:
        """返回版本号元组 (major, minor, patch)"""
        return (self._major, self._minor, self._patch)
    
    def __str__(self) -> str:
        """字符串表示"""
        version = f"{self._major}.{self._minor}.{self._patch}"
        if self._prerelease:
            version += f"-{self._prerelease}"
        if self._build:
            version += f"+{self._build}"
        return version
    
    def __repr__(self) -> str:
        """开发者表示"""
        return f"Version('{str(self)}')"
    
    def __eq__(self, other) -> bool:
        """等于比较"""
        if not isinstance(other, Version):
            try:
                other = Version(str(other))
            except VersionError:
                return False
        return self.tuple == other.tuple and self._prerelease == other._prerelease
    
    def __ne__(self, other) -> bool:
        """不等于比较"""
        return not self.__eq__(other)
    
    def __lt__(self, other) -> bool:
        """小于比较"""
        if not isinstance(other, Version):
            other = Version(str(other))
        
        # 先比较版本号
        if self.tuple != other.tuple:
            return self.tuple < other.tuple
        
        # 再比较预发布版本
        if self._prerelease and other._prerelease:
            return self._compare_prerelease(self._prerelease, other._prerelease) < 0
        if self._prerelease:
            return True  # 有预发布标记的版本更小
        if other._prerelease:
            return False
        
        return False
    
    def __le__(self, other) -> bool:
        """小于等于比较"""
        return self.__lt__(other) or self.__eq__(other)
    
    def __gt__(self, other) -> bool:
        """大于比较"""
        return not self.__le__(other)
    
    def __ge__(self, other) -> bool:
        """大于等于比较"""
        return not self.__lt__(other)
    
    def _compare_prerelease(self, pre1: str, pre2: str) -> int:
        """
        比较预发布版本标识
        
        规则: 按点分割，数字部分按数值比较，字符串按字典序比较
        """
        parts1 = pre1.split('.')
        parts2 = pre2.split('.')
        
        for p1, p2 in zip(parts1, parts2):
            # 尝试作为数字比较
            try:
                n1, n2 = int(p1), int(p2)
                if n1 != n2:
                    return -1 if n1 < n2 else 1
            except ValueError:
                # 按字符串比较
                if p1 != p2:
                    return -1 if p1 < p2 else 1
        
        # 长度不同，长的更大
        return len(parts1) - len(parts2)


# =============================================
# 版本匹配器
# =============================================

class VersionMatcher:
    """
    版本匹配器
    
    支持的操作符:
    - >= : 大于等于 (compatible with higher versions)
    - <= : 小于等于
    - >  : 大于
    - <  : 小于
    - == : 精确匹配
    - ^  : 兼容版本（允许更新的次版本和修订号，但不允许主版本变更）
           例如: ^1.2.3 匹配 >=1.2.3 <2.0.0
    - ~  : 近似版本（允许更新的修订号，但不允许次版本变更）
           例如: ~1.2.3 匹配 >=1.2.3 <1.3.0
    """
    
    # 操作符正则
    OPERATOR_PATTERN = re.compile(r'^(>=|<=|>| <|==|\^|~)?(.+)$')
    
    @classmethod
    def parse(cls, version_str: str) -> Version:
        """
        解析版本号
        
        Args:
            version_str: 版本字符串
            
        Returns:
            Version: 版本对象
            
        Raises:
            VersionError: 版本号格式无效
        """
        return Version(version_str)
    
    @classmethod
    def match(cls, required: str, actual: str) -> bool:
        """
        检查实际版本是否满足需求版本
        
        Args:
            required: 需求版本表达式（如 ">=1.0.0"）
            actual: 实际版本号（如 "1.2.0"）
            
        Returns:
            bool: 是否匹配
            
        Raises:
            VersionError: 版本号格式无效
        """
        operator, version_req = cls._parse_requirement(required)
        version_actual = cls.parse(actual)
        version_req = cls.parse(version_req)
        
        return cls._check_operator(operator, version_req, version_actual)
    
    @classmethod
    def _parse_requirement(cls, requirement: str) -> Tuple[str, str]:
        """
        解析需求表达式
        
        Returns:
            Tuple[操作符, 版本号]
        """
        match = cls.OPERATOR_PATTERN.match(requirement.strip())
        if not match:
            raise VersionError(f"无效的需求表达式: {requirement}")
        
        operator = match.group(1) or ">="  # 默认为 >=
        version = match.group(2).strip()
        
        return operator, version
    
    @classmethod
    def _check_operator(cls, operator: str, required: Version, actual: Version) -> bool:
        """检查操作符"""
        if operator == ">=":
            return actual >= required
        elif operator == "<=":
            return actual <= required
        elif operator == ">":
            return actual > required
        elif operator == "<":
            return actual < required
        elif operator == "==":
            return actual == required
        elif operator == "^":
            # 兼容版本: 主版本必须相同，且必须 >= required
            if actual.major != required.major:
                return False
            return actual >= required
        elif operator == "~":
            # 近似版本: 主、次版本必须相同，且必须 >= required
            if actual.major != required.major or actual.minor != required.minor:
                return False
            return actual >= required
        else:
            raise VersionError(f"未知的操作符: {operator}")


# =============================================
# 依赖定义
# =============================================

@dataclass
class Dependency:
    """
    依赖定义类
    
    Attributes:
        id: 依赖的插件ID
        version: 版本要求（如 ">=1.0.0"）
        optional: 是否为可选依赖，默认为False
    """
    id: str
    version: str = ">=0.0.0"  # 默认接受任何版本
    optional: bool = False
    
    def __post_init__(self):
        """验证数据"""
        if not self.id:
            raise ValueError("依赖ID不能为空")
        self.id = self.id.strip()
    
    def __str__(self) -> str:
        """字符串表示"""
        prefix = "optional:" if self.optional else ""
        return f"{prefix}{self.id}({self.version})"
    
    def __repr__(self) -> str:
        """开发者表示"""
        return f"Dependency(id='{self.id}', version='{self.version}', optional={self.optional})"
    
    def check_version(self, actual_version: str) -> bool:
        """
        检查实际版本是否满足要求
        
        Args:
            actual_version: 实际版本号
            
        Returns:
            bool: 是否满足
        """
        try:
            return VersionMatcher.match(self.version, actual_version)
        except VersionError:
            return False


# =============================================
# 解析错误类型
# =============================================

class DependencyErrorType(Enum):
    """依赖错误类型"""
    MISSING = "missing"               # 依赖缺失
    VERSION_MISMATCH = "version"      # 版本不匹配
    CIRCULAR = "circular"             # 循环依赖
    UNKNOWN = "unknown"               # 未知错误


@dataclass
class DependencyError:
    """依赖错误信息"""
    plugin_id: str                      # 发生错误的插件ID
    dependency: Optional[Dependency]    # 相关的依赖
    error_type: DependencyErrorType     # 错误类型
    message: str                        # 错误信息
    
    def __str__(self) -> str:
        return f"[{self.error_type.value}] {self.plugin_id}: {self.message}"


# =============================================
# 依赖解析器
# =============================================

class DependencyResolver:
    """
    依赖解析器
    
    使用有向无环图（DAG）管理插件依赖关系，使用 Kahn 算法进行拓扑排序。
    
    特性：
    - 自动检测循环依赖
    - 支持可选依赖
    - 详细的错误报告
    - 基于版本约束的依赖解析
    
    Example:
        >>> resolver = DependencyResolver()
        >>> resolver.add_plugin("A", [Dependency("B", ">=1.0")])
        >>> resolver.add_plugin("B", [])
        >>> order = resolver.resolve()
        >>> print(order)  # ['B', 'A']
    """
    
    def __init__(self):
        """初始化解析器"""
        # 插件依赖图: {plugin_id: [Dependency, ...]}
        self._dependencies: Dict[str, List[Dependency]] = {}
        
        # 已注册插件的版本信息: {plugin_id: version}
        self._versions: Dict[str, str] = {}
        
        # 错误列表
        self._errors: List[DependencyError] = []
        
        # 缺失的依赖: {(plugin_id, dependency_id)}
        self._missing: Set[Tuple[str, str]] = set()
    
    def add_plugin(self, plugin_id: str, dependencies: List[Dependency], version: str = "0.0.0"):
        """
        添加插件及其依赖
        
        Args:
            plugin_id: 插件ID
            dependencies: 依赖列表
            version: 插件版本号，默认为 "0.0.0"
            
        Raises:
            ValueError: 插件ID重复
        """
        if plugin_id in self._dependencies:
            raise ValueError(f"插件 '{plugin_id}' 已存在")
        
        self._dependencies[plugin_id] = list(dependencies)
        self._versions[plugin_id] = version
    
    def remove_plugin(self, plugin_id: str):
        """
        移除插件及其依赖信息
        
        Args:
            plugin_id: 插件ID
        """
        if plugin_id in self._dependencies:
            del self._dependencies[plugin_id]
        if plugin_id in self._versions:
            del self._versions[plugin_id]
        
        # 清除相关的错误和缺失记录
        self._errors = [e for e in self._errors if e.plugin_id != plugin_id]
        self._missing = {(p, d) for p, d in self._missing if p != plugin_id}
    
    def clear(self):
        """清空所有数据"""
        self._dependencies.clear()
        self._versions.clear()
        self._errors.clear()
        self._missing.clear()
    
    def resolve(self) -> List[str]:
        """
        解析加载顺序，返回插件ID列表
        
        使用 Kahn 算法进行拓扑排序，确保依赖的插件先于被依赖的插件加载。
        
        Returns:
            List[str]: 排序后的插件ID列表
            
        Raises:
            CircularDependencyError: 存在循环依赖
        """
        # 检查循环依赖
        if self.check_circular():
            cycles = self._find_cycles()
            cycle_str = " -> ".join(cycles[0]) + " -> " + cycles[0][0]
            raise CircularDependencyError(f"检测到循环依赖: {cycle_str}")
        
        # 构建入度表和邻接表
        in_degree: Dict[str, int] = {plugin: 0 for plugin in self._dependencies}
        adjacency: Dict[str, List[str]] = {plugin: [] for plugin in self._dependencies}
        
        for plugin_id, deps in self._dependencies.items():
            for dep in deps:
                # 跳过缺失的可选依赖
                if dep.id not in self._dependencies:
                    if not dep.optional:
                        self._missing.add((plugin_id, dep.id))
                    continue
                
                # 检查版本匹配
                if not dep.check_version(self._versions.get(dep.id, "0.0.0")):
                    self._errors.append(DependencyError(
                        plugin_id=plugin_id,
                        dependency=dep,
                        error_type=DependencyErrorType.VERSION_MISMATCH,
                        message=f"版本不匹配: 需要 {dep.version}, 实际 {self._versions.get(dep.id, 'unknown')}"
                    ))
                    if not dep.optional:
                        continue
                
                # 添加边: dep.id -> plugin_id (依赖dep的插件要在dep之后加载)
                if dep.id in self._dependencies:
                    adjacency[dep.id].append(plugin_id)
                    in_degree[plugin_id] += 1
        
        # Kahn算法
        queue = deque([p for p, d in in_degree.items() if d == 0])
        result = []
        
        while queue:
            plugin = queue.popleft()
            result.append(plugin)
            
            for dependent in adjacency[plugin]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        # 检查是否所有插件都被处理
        if len(result) != len(self._dependencies):
            unprocessed = set(self._dependencies.keys()) - set(result)
            raise CircularDependencyError(
                f"无法解析部分插件的加载顺序: {unprocessed}"
            )
        
        return result
    
    def check_circular(self) -> bool:
        """
        检查是否存在循环依赖
        
        Returns:
            bool: 是否存在循环依赖
        """
        # 使用DFS检测循环
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {plugin: WHITE for plugin in self._dependencies}
        
        def dfs(node: str, path: List[str]) -> bool:
            color[node] = GRAY
            path.append(node)
            
            for dep in self._dependencies.get(node, []):
                # 跳过缺失的依赖
                if dep.id not in self._dependencies:
                    continue
                    
                if color[dep.id] == GRAY:
                    # 发现循环
                    cycle_start = path.index(dep.id)
                    cycle = path[cycle_start:] + [dep.id]
                    self._errors.append(DependencyError(
                        plugin_id=node,
                        dependency=dep,
                        error_type=DependencyErrorType.CIRCULAR,
                        message=f"循环依赖: {' -> '.join(cycle)}"
                    ))
                    return True
                
                if color[dep.id] == WHITE:
                    if dfs(dep.id, path):
                        return True
            
            path.pop()
            color[node] = BLACK
            return False
        
        for plugin in self._dependencies:
            if color[plugin] == WHITE:
                if dfs(plugin, []):
                    return True
        
        return False
    
    def _find_cycles(self) -> List[List[str]]:
        """
        查找所有循环依赖路径
        
        Returns:
            List[List[str]]: 循环路径列表
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for dep in self._dependencies.get(node, []):
                if dep.id not in self._dependencies:
                    continue
                    
                if dep.id not in visited:
                    dfs(dep.id)
                elif dep.id in rec_stack:
                    # 发现循环
                    cycle_start = path.index(dep.id)
                    cycle = path[cycle_start:]
                    cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node)
        
        for plugin in self._dependencies:
            if plugin not in visited:
                dfs(plugin)
        
        return cycles
    
    def get_missing(self) -> List[Tuple[str, str]]:
        """
        获取缺失的依赖
        
        Returns:
            List[Tuple[str, str]]: (插件ID, 缺失的依赖ID) 列表
        """
        return sorted(list(self._missing))
    
    def get_errors(self) -> List[DependencyError]:
        """
        获取所有错误信息
        
        Returns:
            List[DependencyError]: 错误信息列表
        """
        return self._errors.copy()
    
    def has_errors(self) -> bool:
        """
        检查是否存在错误
        
        Returns:
            bool: 是否存在错误
        """
        return bool(self._errors) or bool(self._missing)
    
    def get_plugin_dependencies(self, plugin_id: str) -> List[Dependency]:
        """
        获取指定插件的依赖列表
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            List[Dependency]: 依赖列表
        """
        return self._dependencies.get(plugin_id, []).copy()
    
    def get_dependent_plugins(self, plugin_id: str) -> List[str]:
        """
        获取依赖于指定插件的所有插件
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            List[str]: 依赖于此插件的插件ID列表
        """
        dependents = []
        for pid, deps in self._dependencies.items():
            for dep in deps:
                if dep.id == plugin_id:
                    dependents.append(pid)
                    break
        return dependents
    
    def __len__(self) -> int:
        """返回已注册的插件数量"""
        return len(self._dependencies)
    
    def __contains__(self, plugin_id: str) -> bool:
        """检查插件是否已注册"""
        return plugin_id in self._dependencies


class CircularDependencyError(Exception):
    """循环依赖错误"""
    pass


# =============================================
# 单元测试
# =============================================

if __name__ == "__main__":
    import unittest
    
    class TestVersion(unittest.TestCase):
        """版本号测试"""
        
        def test_basic_parsing(self):
            v = Version("1.2.3")
            self.assertEqual(v.major, 1)
            self.assertEqual(v.minor, 2)
            self.assertEqual(v.patch, 3)
        
        def test_prerelease(self):
            v = Version("1.0.0-alpha")
            self.assertEqual(v.prerelease, "alpha")
            self.assertTrue(v.is_prerelease)
        
        def test_comparison(self):
            self.assertTrue(Version("1.0.0") < Version("2.0.0"))
            self.assertTrue(Version("1.0.0") < Version("1.1.0"))
            self.assertTrue(Version("1.0.0") < Version("1.0.1"))
            self.assertTrue(Version("1.0.0-alpha") < Version("1.0.0"))
            self.assertEqual(Version("1.0.0"), Version("1.0.0"))
        
        def test_invalid_version(self):
            with self.assertRaises(VersionError):
                Version("")
            with self.assertRaises(VersionError):
                Version("abc")
    
    
    class TestVersionMatcher(unittest.TestCase):
        """版本匹配器测试"""
        
        def test_exact_match(self):
            self.assertTrue(VersionMatcher.match("==1.0.0", "1.0.0"))
            self.assertFalse(VersionMatcher.match("==1.0.0", "1.0.1"))
        
        def test_greater_than(self):
            self.assertTrue(VersionMatcher.match(">=1.0.0", "1.0.0"))
            self.assertTrue(VersionMatcher.match(">=1.0.0", "2.0.0"))
            self.assertFalse(VersionMatcher.match(">=1.0.0", "0.9.0"))
        
        def test_less_than(self):
            self.assertTrue(VersionMatcher.match("<=1.0.0", "1.0.0"))
            self.assertTrue(VersionMatcher.match("<=1.0.0", "0.9.0"))
            self.assertFalse(VersionMatcher.match("<=1.0.0", "1.1.0"))
        
        def test_caret(self):
            # ^1.2.3 应该匹配 >=1.2.3 <2.0.0
            self.assertTrue(VersionMatcher.match("^1.2.3", "1.2.3"))
            self.assertTrue(VersionMatcher.match("^1.2.3", "1.3.0"))
            self.assertFalse(VersionMatcher.match("^1.2.3", "2.0.0"))
            self.assertFalse(VersionMatcher.match("^1.2.3", "1.2.2"))
        
        def test_tilde(self):
            # ~1.2.3 应该匹配 >=1.2.3 <1.3.0
            self.assertTrue(VersionMatcher.match("~1.2.3", "1.2.3"))
            self.assertTrue(VersionMatcher.match("~1.2.3", "1.2.9"))
            self.assertFalse(VersionMatcher.match("~1.2.3", "1.3.0"))
            self.assertFalse(VersionMatcher.match("~1.2.3", "1.2.2"))
    
    
    class TestDependency(unittest.TestCase):
        """依赖定义测试"""
        
        def test_creation(self):
            d = Dependency("test_plugin", ">=1.0.0", optional=True)
            self.assertEqual(d.id, "test_plugin")
            self.assertEqual(d.version, ">=1.0.0")
            self.assertTrue(d.optional)
        
        def test_check_version(self):
            d = Dependency("test", ">=1.0.0")
            self.assertTrue(d.check_version("1.0.0"))
            self.assertTrue(d.check_version("2.0.0"))
            self.assertFalse(d.check_version("0.9.0"))
        
        def test_invalid_id(self):
            with self.assertRaises(ValueError):
                Dependency("")
    
    
    class TestDependencyResolver(unittest.TestCase):
        """依赖解析器测试"""
        
        def test_simple_resolution(self):
            resolver = DependencyResolver()
            resolver.add_plugin("A", [Dependency("B")])
            resolver.add_plugin("B", [])
            
            order = resolver.resolve()
            self.assertEqual(order.index("B"), 0)
            self.assertEqual(order.index("A"), 1)
        
        def test_complex_resolution(self):
            """
            依赖关系:
            A -> B, C
            B -> D
            C -> D
            D -> (无)
            
            预期加载顺序: D, B, C, A 或 D, C, B, A
            """
            resolver = DependencyResolver()
            resolver.add_plugin("A", [Dependency("B"), Dependency("C")])
            resolver.add_plugin("B", [Dependency("D")])
            resolver.add_plugin("C", [Dependency("D")])
            resolver.add_plugin("D", [])
            
            order = resolver.resolve()
            self.assertEqual(order.index("D"), 0)  # D 必须第一个
            self.assertTrue(order.index("B") < order.index("A"))
            self.assertTrue(order.index("C") < order.index("A"))
        
        def test_circular_detection(self):
            resolver = DependencyResolver()
            resolver.add_plugin("A", [Dependency("B")])
            resolver.add_plugin("B", [Dependency("A")])
            
            self.assertTrue(resolver.check_circular())
            with self.assertRaises(CircularDependencyError):
                resolver.resolve()
        
        def test_optional_dependency(self):
            """测试可选依赖：当依赖缺失时，可选依赖不会导致错误"""
            resolver = DependencyResolver()
            resolver.add_plugin("A", [Dependency("B", ">=1.0.0", optional=True)])
            
            order = resolver.resolve()
            self.assertEqual(order, ["A"])
            # 可选依赖缺失不应记录在 missing 中
            self.assertEqual(len(resolver.get_missing()), 0)
        
        def test_version_mismatch(self):
            resolver = DependencyResolver()
            resolver.add_plugin("A", [Dependency("B", ">=2.0.0")], version="1.0.0")
            resolver.add_plugin("B", [], version="1.0.0")
            
            order = resolver.resolve()
            errors = resolver.get_errors()
            self.assertTrue(len(errors) > 0)
            self.assertEqual(errors[0].error_type, DependencyErrorType.VERSION_MISMATCH)
        
        def test_get_dependents(self):
            resolver = DependencyResolver()
            resolver.add_plugin("A", [Dependency("B")])
            resolver.add_plugin("C", [Dependency("B")])
            resolver.add_plugin("B", [])
            
            dependents = resolver.get_dependent_plugins("B")
            self.assertIn("A", dependents)
            self.assertIn("C", dependents)
        
        def test_remove_plugin(self):
            resolver = DependencyResolver()
            resolver.add_plugin("A", [Dependency("B")])
            resolver.add_plugin("B", [])
            
            resolver.remove_plugin("B")
            self.assertNotIn("B", resolver)
            
            # 调用 resolve 后才会检测缺失依赖
            order = resolver.resolve()
            self.assertEqual(len(resolver.get_missing()), 1)
            self.assertEqual(resolver.get_missing()[0], ("A", "B"))
    
    
    # 运行测试
    print("=" * 50)
    print("运行依赖解析器单元测试")
    print("=" * 50)
    
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVersion))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVersionMatcher))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDependency))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDependencyResolver))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印摘要
    print("\n" + "=" * 50)
    print("测试摘要")
    print("=" * 50)
    print(f"运行测试: {result.testsRun}")
    print(f"通过: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n所有测试通过!")
    else:
        print("\n存在失败的测试!")
        exit(1)
