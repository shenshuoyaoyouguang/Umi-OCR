# download_pystand.ps1
# 下载 PyStand 运行时用于打包 Umi-OCR

param(
    [string]$Version = "v1.4.1",
    [string]$OutputDir = ".\pystand"
)

Write-Host "开始下载 PyStand 运行时..." -ForegroundColor Cyan
Write-Host "版本: $Version" -ForegroundColor Yellow

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "创建目录: $OutputDir" -ForegroundColor Green
}

# PyStand 下载 URL（根据实际需要调整）
$BaseUrl = "https://github.com/anthony-tuininga/pystand/releases/download"
$FileName = "pystand-${Version}-windows-amd64.zip"
$DownloadUrl = "$BaseUrl/$Version/$FileName"
$OutputFile = Join-Path $OutputDir $FileName

Write-Host "下载 URL: $DownloadUrl" -ForegroundColor Yellow

# 检查是否已下载
if (Test-Path $OutputFile) {
    Write-Host "文件已存在，跳过下载: $OutputFile" -ForegroundColor Green
} else {
    try {
        Write-Host "正在下载..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $OutputFile -UseBasicParsing
        Write-Host "下载完成: $OutputFile" -ForegroundColor Green
    } catch {
        Write-Host "下载失败: $_" -ForegroundColor Red
        Write-Host "请手动下载 PyStand 并放置在 $OutputDir 目录" -ForegroundColor Yellow
        exit 1
    }
}

# 解压文件
$ExtractDir = Join-Path $OutputDir "extracted"
if (Test-Path $ExtractDir) {
    Remove-Item -Path $ExtractDir -Recurse -Force
}

Write-Host "正在解压..." -ForegroundColor Yellow
Expand-Archive -Path $OutputFile -DestinationPath $ExtractDir -Force

# 移动到主目录
Write-Host "整理文件..." -ForegroundColor Yellow
$ExtractedFiles = Get-ChildItem -Path $ExtractDir -Recurse -File
foreach ($file in $ExtractedFiles) {
    $DestFile = Join-Path $OutputDir $file.Name
    if (Test-Path $DestFile) {
        Remove-Item -Path $DestFile -Force
    }
    Move-Item -Path $file.FullName -Destination $OutputDir -Force
}

# 清理临时文件
Remove-Item -Path $ExtractDir -Recurse -Force

Write-Host "PyStand 下载完成！" -ForegroundColor Green
Write-Host "PyStand 位置: $OutputDir" -ForegroundColor Cyan

# 显示下载的文件
Write-Host "`n已下载的文件:" -ForegroundColor Cyan
Get-ChildItem -Path $OutputDir -File | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Gray
}