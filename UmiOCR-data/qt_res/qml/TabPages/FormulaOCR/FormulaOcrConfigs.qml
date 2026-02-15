// ==============================================
// =============== 公式OCR的配置项 ===============
// ==============================================

import QtQuick 2.15
import "../../Configs"

Configs {
    category_: "FormulaOCR"

    configDict: {
        // OCR参数
        "ocr": qmlapp.globalConfigs.ocrManager.deploy(this, "ocr"),

        // 输出设置
        "output": {
            "title": qsTr("输出设置"),
            "type": "group",

            "delimiter": {
                "title": qsTr("输出定界符"),
                "toolTip": qsTr("复制时自动添加LaTeX定界符"),
                "optionsList": [
                    ["none", qsTr("无定界符")],
                    ["inline", qsTr("行内公式 ($...$)")],
                    ["display", qsTr("行间公式 ($$...$$)")],
                ],
                "default": "none",
            },
            "showConfidence": {
                "title": qsTr("显示置信度"),
                "toolTip": qsTr("在预览中显示识别置信度"),
                "default": true,
            },
            "autoFixErrors": {
                "title": qsTr("自动修复错误"),
                "toolTip": qsTr("自动修复常见的LaTeX语法错误"),
                "default": true,
            },
        },

        // 快捷键
        "hotkey": {
            "title": qsTr("快捷键"),
            "type": "group",

            "screenshot": {
                "title": qsTr("屏幕截图"),
                "type": "hotkey",
                // 默认热键
                "default": UmiAbout.app.system==="win32" ?
                            "win+alt+f" : "alt+f",
                "eventTitle": "<<formulaScreenshot>>", // 触发事件标题
            },
            "paste": {
                "title": qsTr("粘贴图片"),
                "type": "hotkey",
                "default": "",
                "eventTitle": "<<formulaPaste>>",
            },
            "reScreenshot": {
                "title": qsTr("重复截图"),
                "toolTip": qsTr("重新截取上一次截图的范围"),
                "type": "hotkey",
                "default": "",
                "eventTitle": "<<formulaReScreenshot>>",
            },
        },

        // 识图后的操作
        "action": {
            "title": qsTr("识图后的操作"),
            "type": "group",

            "copy": {
                "title": qsTr("复制结果"),
                "default": false,
            },
            "popMainWindow": {
                "title": qsTr("弹出主窗口"),
                "toolTip": qsTr("识图后，如果主窗口最小化或处于后台，则弹到前台"),
                "default": true,
            },
        },

        // 其它
        "other": {
            "title": qsTr("其它"),
            "type": "group",

            "simpleNotificationType": qmlapp.globalConfigs.utilsDicts.getSimpleNotificationType()
        },
    }
}
