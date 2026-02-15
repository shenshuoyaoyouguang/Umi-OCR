# TBPU 配置常量
# 集中管理排版解析算法中的阈值和参数

from __future__ import annotations


class TbpuConfig:
    """
    TBPU 配置常量类
    
    集中管理所有排版解析算法中使用的阈值和参数，
    便于调整和维护。
    """
    
    # =============== 行识别参数 ===============
    
    # 行高容差因子（用于判断两个文本块是否属于同一行）
    LINE_HEIGHT_TOLERANCE: float = 0.5
    
    # 水平间隙因子（间隙超过行高的此倍数时，强制添加空格）
    HORIZONTAL_GAP_FACTOR: float = 1.5
    
    # =============== 段落分析参数 ===============
    
    # 段落分析阈值（行高用作对比的阈值）
    PARAGRAPH_THRESHOLD: float = 1.2
    
    # 行间距容差因子
    LINE_SPACING_TOLERANCE: float = 0.5
    
    # =============== 角度阈值 ===============
    
    # 进行旋转操作的最小角度阈值（度）
    ANGLE_THRESHOLD_DEGREES: float = 3.0
