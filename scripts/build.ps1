# build.ps1
# 简化版 Umi-OCR 构建脚本

param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath,
    [string]$OutputPath = ".\dist",
    [string]$AppName = "Umi-OCR",
    [string]$Version = "2.1.5"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Umi-OCR 简化构建脚本" -ForegroundColor Cyan
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

# 检查 PyStand 目录
Write-Host "`n检查 PyStand..." -ForegroundColor Cyan
$PyStandDir = ".\pystand"
if (-not (Test-Path $PyStandDir)) {
    Write-Host "错误: PyStand 目录不存在: $PyStandDir" -ForegroundColor Red
    exit 1
}
Write-Host "PyStand 目录: $PyStandDir" -ForegroundColor Green

# 创建输出目录
if (Test-Path $OutputPath) {
    Write-Host "清理输出目录: $OutputPath" -ForegroundColor Yellow
    Remove-Item -Path $OutputPath -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

# 复制源代码
Write-Host "`n步骤 1: 复制源代码..." -ForegroundColor Cyan
$UmiDataPath = Join-Path $OutputPath "UmiOCR-data"
New-Item -ItemType Directory -Path $UmiDataPath -Force | Out-Null
Copy-Item -Path "$SourcePath\*" -Destination $UmiDataPath -Recurse -Force
Write-Host "源代码已复制到: $UmiDataPath" -ForegroundColor Green

# 复制 PyStand
Write-Host "`n步骤 2: 复制 PyStand 运行时..." -ForegroundColor Cyan
Copy-Item -Path "$PyStandDir\*" -Destination $OutputPath -Recurse -Force
Write-Host "PyStand 已复制" -ForegroundColor Green

# 创建启动脚本
Write-Host "`n步骤 3: 创建启动脚本..." -ForegroundColor Cyan
$BatContent = @"
@echo off
cd /d "%~dp0"
python main.py
pause
"@
$BatFile = Join-Path $OutputPath "启动.bat"
$BatContent | Out-File -FilePath $BatFile -Encoding ASCII
Write-Host "启动脚本已创建: $BatFile" -ForegroundColor Green

# 创建 README
Write-Host "`n步骤 4: 创建 README..." -ForegroundColor Cyan
$ReadmeContent = @"
# $AppName v$Version (Windows)

## 使用说明

1. 双击运行 `启动.bat`
2. 首次运行可能需要一些时间加载模型

## 系统要求

- Windows 10/11 (64位)
- Python 3.12

## 版本信息

- 版本: $Version
- 构建日期: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- 构建方式: PyStand
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
Write-Host "  - PyStand.exe (主程序)" -ForegroundColor Gray
Write-Host "  - 启动.bat (启动脚本)" -ForegroundColor Gray
Write-Host "  - UmiOCR-data/ (应用数据)" -ForegroundColor Gray
Write-Host "  - README.txt (使用说明)" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

# 显示目录大小
$Size = (Get-ChildItem -Path $OutputPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "总大小: $([math]::Round($Size, 2)) MB" -ForegroundColor Cyan