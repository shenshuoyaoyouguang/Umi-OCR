# prepare_deps.ps1
# 准备 Umi-OCR 构建所需的依赖

param(
    [string]$RequirementsFile = "requirements.txt",
    [string]$PythonVersion = "3.12"
)

Write-Host "开始准备构建依赖..." -ForegroundColor Cyan
Write-Host "Python 版本: $PythonVersion" -ForegroundColor Yellow

# 检查 Python 版本
$pythonVersionOutput = python --version 2>&1
Write-Host "当前 Python: $pythonVersionOutput" -ForegroundColor Gray

# 创建虚拟环境（可选）
$VenvDir = ".\venv"
if (-not (Test-Path $VenvDir)) {
    Write-Host "创建虚拟环境: $VenvDir" -ForegroundColor Yellow
    python -m venv $VenvDir
}

# 激活虚拟环境
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    Write-Host "激活虚拟环境..." -ForegroundColor Yellow
    & $ActivateScript
}

# 升级 pip
Write-Host "升级 pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 安装基础依赖
Write-Host "安装基础依赖..." -ForegroundColor Yellow
$baseDeps = @(
    "setuptools",
    "wheel",
    "PyInstaller"
)

foreach ($dep in $baseDeps) {
    Write-Host "  安装 $dep..." -ForegroundColor Gray
    pip install $dep
}

# 安装项目依赖
if (Test-Path $RequirementsFile) {
    Write-Host "从 $RequirementsFile 安装依赖..." -ForegroundColor Yellow
    pip install -r $RequirementsFile
} else {
    Write-Host "未找到 $RequirementsFile，安装默认依赖..." -ForegroundColor Yellow

    # Umi-OCR 常用依赖
    $umiOcrDeps = @(
        "PyQt6>=6.5.0",
        "PySide6>=6.5.0",
        "numpy>=1.24.0",
        "opencv-python-headless>=4.8.0",
        "Pillow>=10.0.0",
        "pyclipper>=1.3.0",
        "shapely>=2.0.0",
        "onnxruntime>=1.15.0",
        "rapidocr_onnxruntime>=1.2.0",
        "rapidocr>=1.2.0"
    )

    foreach ($dep in $umiOcrDeps) {
        Write-Host "  安装 $dep..." -ForegroundColor Gray
        pip install $dep
    }
}

# 安装 OCR 引擎
Write-Host "安装 OCR 引擎..." -ForegroundColor Yellow

# PaddleOCR（可选）
Write-Host "检查 PaddleOCR..." -ForegroundColor Gray
try {
    $paddleOcr = pip show paddleocr 2>$null
    if (-not $paddleOcr) {
        Write-Host "安装 PaddleOCR..." -ForegroundColor Yellow
        pip install paddlepaddle paddleocr
    } else {
        Write-Host "PaddleOCR 已安装: $($paddleOcr.Version)" -ForegroundColor Green
    }
} catch {
    Write-Host "警告: 无法安装 PaddleOCR: $_" -ForegroundColor Yellow
}

# 下载 OCR 模型（可选）
Write-Host "准备 OCR 模型..." -ForegroundColor Yellow
$ModelsDir = ".\models"
if (-not (Test-Path $ModelsDir)) {
    New-Item -ItemType Directory -Path $ModelsDir -Force | Out-Null
    Write-Host "创建模型目录: $ModelsDir" -ForegroundColor Green
}

# 下载 RapidOCR 模型
Write-Host "检查 RapidOCR 模型..." -ForegroundColor Gray
try {
    $modelFile = Join-Path $ModelsDir "ch_PP-OCRv3_det_infer.onnx"
    if (-not (Test-Path $modelFile)) {
        Write-Host "下载 RapidOCR 检测模型..." -ForegroundColor Yellow
        # 使用 huggingface 或其他源下载模型
        # 这里只是示例，实际需要根据项目需求调整
        Write-Host "模型下载示例（需根据实际情况调整）" -ForegroundColor Yellow
    } else {
        Write-Host "模型文件已存在" -ForegroundColor Green
    }
} catch {
    Write-Host "警告: 无法下载模型: $_" -ForegroundColor Yellow
}

# 依赖检查
Write-Host "`n依赖检查..." -ForegroundColor Cyan
$requiredPackages = @(
    "PyQt6",
    "opencv-python-headless",
    "numpy"
)

foreach ($package in $requiredPackages) {
    $installed = pip show $package 2>$null
    if ($installed) {
        Write-Host "  ✓ $package ($($installed.Version))" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $package 未安装" -ForegroundColor Red
    }
}

Write-Host "`n依赖准备完成！" -ForegroundColor Green