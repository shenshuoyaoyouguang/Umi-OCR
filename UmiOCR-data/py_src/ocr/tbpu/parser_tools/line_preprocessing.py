# =========================================
# =============== 按行预处理 ===============
# =========================================

from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple
from statistics import median  # 中位数
from math import atan2, cos, sin, sqrt, pi, radians, degrees

if TYPE_CHECKING:
    from ..tbpu_types import TextBlocks, TextBlock, NormalizedBox, Box

from umi_log import logger

# 进行一些操作的最小角度阈值
angle_threshold: float = 3
angle_threshold_rad: float = radians(angle_threshold)


def _distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    计算两点之间的距离

    Args:
        point1: 第一个点坐标 (x, y)
        point2: 第二个点坐标 (x, y)

    Returns:
        两点之间的距离
    """
    return sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)


def _calculate_angle(box: Box) -> float:
    """
    计算一个box的旋转角度

    Args:
        box: 四边形包围盒，四个顶点的坐标

    Returns:
        旋转角度（弧度）
    """
    # 获取宽高
    width = _distance(box[0], box[1])
    height = _distance(box[1], box[2])
    # 选择距离较大的两个顶点对，计算角度弧度值
    if width < height:
        angle_rad = atan2(box[2][1] - box[1][1], box[2][0] - box[1][0])
    else:
        angle_rad = atan2(box[1][1] - box[0][1], box[1][0] - box[0][0])
    # 标准化角度到[-pi/2, pi/2)范围（加上阈值）
    if angle_rad < -pi / 2 + angle_threshold_rad:
        angle_rad += pi
    elif angle_rad >= pi / 2 + angle_threshold_rad:
        angle_rad -= pi
    return angle_rad


def _estimate_rotation(text_blocks: TextBlocks) -> float:
    """
    估计一组文本块的旋转角度

    Args:
        text_blocks: 文本块列表

    Returns:
        估计的旋转角度（弧度）
    """
    # blocks["box"] = [左上角,右上角,右下角,左下角]
    angle_rads = (_calculate_angle(block["box"]) for block in text_blocks)
    median_angle = median(angle_rads)  # 中位数
    return median_angle


def _get_bboxes(text_blocks: TextBlocks, rotation_rad: float) -> List[NormalizedBox]:
    """
    获取旋转后的标准bbox

    Args:
        text_blocks: 文本块列表
        rotation_rad: 旋转角度（弧度）

    Returns:
        标准化包围盒列表
    """
    bboxes: List[NormalizedBox] = []

    # 角度低于阈值（接近0°），则不进行旋转，以提高性能。
    if abs(rotation_rad) <= angle_threshold_rad:
        bboxes = [
            (  # 直接构造bbox
                min(x for x, y in tb["box"]),
                min(y for x, y in tb["box"]),
                max(x for x, y in tb["box"]),
                max(y for x, y in tb["box"]),
            )
            for tb in text_blocks
        ]
    # 否则，进行旋转操作。
    else:
        logger.debug(f"文本块预处理旋转 {degrees(rotation_rad):.2f} °")
        min_x, min_y = float("inf"), float("inf")  # 初始化最小的x和y坐标
        cos_angle = cos(-rotation_rad)  # 计算角度余弦值
        sin_angle = sin(-rotation_rad)

        for tb in text_blocks:
            box: Box = tb["box"]
            rotated_box = [  # 旋转box的每个顶点
                (cos_angle * x - sin_angle * y, sin_angle * x + cos_angle * y)
                for x, y in box
            ]
            # 解包旋转后的顶点坐标，分别得到所有x和y的值
            xs, ys = zip(*rotated_box)
            # 构建标准bbox (左上角x, 左上角y, 右下角x, 右下角y)
            bbox: NormalizedBox = (min(xs), min(ys), max(xs), max(ys))
            bboxes.append(bbox)
            min_x, min_y = min(min_x, bbox[0]), min(min_y, bbox[1])

        # 如果旋转后存在负坐标，将所有包围盒平移，使得最小的x和y坐标为0，确保所有坐标非负
        if min_x < 0 or min_y < 0:
            bboxes = [
                (x - min_x, y - min_y, x2 - min_x, y2 - min_y)
                for (x, y, x2, y2) in bboxes
            ]

    return bboxes


def line_preprocessing(text_blocks: TextBlocks) -> TextBlocks:
    """
    预处理 text_blocks ，将包围盒 ["box"] 转为标准化 bbox ，同时去除 ["text"] 不完整的项

    Args:
        text_blocks: 输入的文本块列表

    Returns:
        预处理后的文本块列表
    """
    # 过滤掉没有文本的块
    text_blocks = [i for i in text_blocks if i.get("text", False)]

    if not text_blocks:
        return []

    # 判断角度
    rotation_rad = _estimate_rotation(text_blocks)

    # 获取标准化bbox
    bboxes = _get_bboxes(text_blocks, rotation_rad)

    # 写入tb
    for i, tb in enumerate(text_blocks):
        tb["normalized_bbox"] = bboxes[i]

    # 按y排序
    text_blocks.sort(key=lambda tb: tb["normalized_bbox"][1])

    return text_blocks