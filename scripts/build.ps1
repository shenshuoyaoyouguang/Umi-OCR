# build.ps1
# 使用 PyStand 打包 Umi-OCR

param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath,
    [string]$OutputPath = ".\dist",
    [string]$AppName = "Umi-OCR",
    [string]$Version = "2.1.5"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Umi-OCR 构建脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "源代码路径: $SourcePath" -ForegroundColor Yellow
Write-Host "输出路径: $OutputPath" -ForegroundColor Yellow
Write-Host "应用名称: $AppName" -ForegroundColor Yellow
Write-Host "版本: $Version" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# 验证源代码路径
if (-not (Test-Path $SourcePath)) {
    Write-Host "错误: 源代码路径不存在: $SourcePath" -ForegroundColor Red
    exit 1
}

# 查找 PyStand（从 pip 安装的位置）
Write-Host "`n查找 PyStand..." -ForegroundColor Cyan
try {
    # 使用 pystand 命令
    $PyStandLocation = python -c "import pystand; import os; print(os.path.dirname(pystand.__file__))" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PyStand 已安装: $PyStandLocation" -ForegroundColor Green
    } else {
        Write-Host "错误: PyStand 未正确安装" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "错误: 无法找到 PyStand" -ForegroundColor Red
    exit 1
}

# 创建输出目录
if (Test-Path $OutputPath) {
    Write-Host "清理输出目录: $OutputPath" -ForegroundColor Yellow
    Remove-Item -Path $OutputPath -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

# 复制源代码
Write-Host "`n步骤 1: 复制源代码..." -ForegroundColor Cyan
$UmiDataPath = Join-Path $OutputPath "UmiOCR-data"
Copy-Item -Path "$SourcePath\*" -Destination $UmiDataPath -Recurse -Force
Write-Host "源代码已复制到: $UmiDataPath" -ForegroundColor Green

# 复制 PyStand 运行时
Write-Host "`n步骤 2: 复制 PyStand 运行时..." -ForegroundColor Cyan
Copy-Item -Path "$PyStandLocation\*" -Destination $OutputPath -Recurse -Force

# 重命名 PyStand 可执行文件
$PyStandExe = Get-ChildItem -Path $OutputPath -Filter "pystand*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($PyStandExe) {
    $NewExe = Join-Path $OutputPath "$AppName.exe"
    if (Test-Path $NewExe) {
        Remove-Item -Path $NewExe -Force
    }
    Move-Item -Path $PyStandExe.FullName -Destination $NewExe -Force
    Write-Host "可执行文件已重命名: $NewExe" -ForegroundColor Green
}

# 创建配置文件
Write-Host "`n步骤 3: 创建配置文件..." -ForegroundColor Cyan
$ConfigContent = @"
{
    "version": "$Version",
    "app_name": "$AppName",
    "entry_point": "main.py",
    "python_version": "3.12",
    "platform": "windows",
    "build_date": "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
}
"@
$ConfigFile = Join-Path $OutputPath "build_info.json"
$ConfigContent | Out-File -FilePath $ConfigFile -Encoding UTF8
Write-Host "配置文件已创建: $ConfigFile" -ForegroundColor Green

# 复制插件目录
Write-Host "`n步骤 4: 复制插件..." -ForegroundColor Cyan
$PluginsDir = Join-Path $UmiDataPath "plugins"
if (Test-Path $PluginsDir) {
    $PluginCount = (Get-ChildItem -Path $PluginsDir -Directory).Count
    Write-Host "发现 $PluginCount 个插件" -ForegroundColor Green
    foreach ($plugin in Get-ChildItem -Path $PluginsDir -Directory) {
        Write-Host "  - $($plugin.Name)" -ForegroundColor Gray
    }
}

# 创建启动脚本
Write-Host "`n步骤 5: 创建启动脚本..." -ForegroundColor Cyan
$BatContent = @"
@echo off
cd /d "%~dp0"
$AppName.exe
pause
"@
$BatFile = Join-Path $OutputPath "启动.bat"
$BatContent | Out-File -FilePath $BatFile -Encoding ASCII
Write-Host "启动脚本已创建: $BatFile" -ForegroundColor Green

# 创建 README
Write-Host "`n步骤 6: 创建 README..." -ForegroundColor Cyan
$ReadmeContent = @"
# $AppName v$Version (Windows)

## 使用说明

1. 双击运行 `$AppName.exe` 或 `启动.bat`
2. 首次运行可能需要一些时间加载模型
3. 支持的插件：

"@

$PluginsDir = Join-Path $UmiDataPath "plugins"
if (Test-Path $PluginsDir) {
    foreach ($plugin in Get-ChildItem -Path $PluginsDir -Directory) {
        $ReadmeContent += "- $($plugin.Name)`n"
    }
}

$ReadmeContent += @"

## 系统要求

- Windows 10/11 (64位)
- Windows 7 (使用 win7_x64_PaddleOCR 插件)

## 版本信息

- 版本: $Version
- 构建日期: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- 构建方式: PyStand

## 问题反馈

如有问题，请访问: https://github.com/shenshuoyaoyouguang/Umi-OCR/issues
"@

$ReadmeFile = Join-Path $OutputPath "README.txt"
$ReadmeContent | Out-File -FilePath $ReadmeFile -Encoding UTF8
Write-Host "README 已创建: $ReadmeFile" -ForegroundColor Green

# 显示构建结果
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "构建完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "输出目录: $OutputPath" -ForegroundColor Yellow
Write-Host "主要文件:" -ForegroundColor Yellow
Write-Host "  - $AppName.exe (主程序)" -ForegroundColor Gray
Write-Host "  - 启动.bat (启动脚本)" -ForegroundColor Gray
Write-Host "  - UmiOCR-data/ (应用数据)" -ForegroundColor Gray
Write-Host "  - README.txt (使用说明)" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

# 显示目录大小
$Size = (Get-ChildItem -Path $OutputPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "总大小: $([math]::Round($Size, 2)) MB" -ForegroundColor Cyan