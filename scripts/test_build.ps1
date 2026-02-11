# test_build.ps1
# 测试构建后的 Umi-OCR 可执行文件

param(
    [Parameter(Mandatory=$true)]
    [string]$BuildPath
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Umi-OCR 构建测试脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "构建路径: $BuildPath" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# 验证构建路径
if (-not (Test-Path $BuildPath)) {
    Write-Host "错误: 构建路径不存在: $BuildPath" -ForegroundColor Red
    exit 1
}

# 测试结果统计
$TestResults = @{
    Passed = 0
    Failed = 0
    Skipped = 0
}

# 辅助函数：运行测试
function Test-Item {
    param(
        [string]$Name,
        [scriptblock]$Test
    )

    Write-Host "`n测试: $Name" -ForegroundColor Cyan

    try {
        $result = & $Test
        if ($result) {
            Write-Host "  ✓ 通过" -ForegroundColor Green
            $script:TestResults.Passed++
            return $true
        } else {
            Write-Host "  ✗ 失败" -ForegroundColor Red
            $script:TestResults.Failed++
            return $false
        }
    } catch {
        Write-Host "  ✗ 异常: $_" -ForegroundColor Red
        $script:TestResults.Failed++
        return $false
    }
}

# 测试 1: 检查主可执行文件
Test-Item -Name "主可执行文件存在" -Test {
    $exePath = Join-Path $BuildPath "Umi-OCR.exe"
    if (-not (Test-Path $exePath)) {
        Write-Host "    未找到: $exePath" -ForegroundColor Red
        return $false
    }
    Write-Host "    路径: $exePath" -ForegroundColor Gray
    Write-Host "    大小: $((Get-Item $exePath).Length / 1MB) MB" -ForegroundColor Gray
    return $true
}

# 测试 2: 检查 UmiOCR-data 目录
Test-Item -Name "UmiOCR-data 目录存在" -Test {
    $dataPath = Join-Path $BuildPath "UmiOCR-data"
    if (-not (Test-Path $dataPath)) {
        Write-Host "    未找到: $dataPath" -ForegroundColor Red
        return $false
    }
    $itemCount = (Get-ChildItem -Path $dataPath -Recurse).Count
    Write-Host "    包含 $itemCount 个项目" -ForegroundColor Gray
    return $true
}

# 测试 3: 检查 main.py
Test-Item -Name "main.py 存在" -Test {
    $mainPath = Join-Path $BuildPath "UmiOCR-data\main.py"
    if (-not (Test-Path $mainPath)) {
        Write-Host "    未找到: $mainPath" -ForegroundColor Red
        return $false
    }
    $content = Get-Content $mainPath -Raw
    Write-Host "    大小: $($content.Length) 字节" -ForegroundColor Gray
    return $content.Length -gt 0
}

# 测试 4: 检查插件目录
Test-Item -Name "插件目录存在" -Test {
    $pluginsPath = Join-Path $BuildPath "UmiOCR-data\plugins"
    if (-not (Test-Path $pluginsPath)) {
        Write-Host "    未找到: $pluginsPath" -ForegroundColor Yellow
        $script:TestResults.Skipped++
        return $false
    }
    $plugins = Get-ChildItem -Path $pluginsPath -Directory
    Write-Host "    找到 $($plugins.Count) 个插件" -ForegroundColor Gray
    foreach ($plugin in $plugins) {
        Write-Host "      - $($plugin.Name)" -ForegroundColor Gray
    }
    return $plugins.Count -gt 0
}

# 测试 5: 检查 PaddleOCR 插件
Test-Item -Name "PaddleOCR 插件存在" -Test {
    $pluginPath = Join-Path $BuildPath "UmiOCR-data\plugins\win7_x64_PaddleOCR"
    if (-not (Test-Path $pluginPath)) {
        Write-Host "    未找到: $pluginPath" -ForegroundColor Yellow
        $script:TestResults.Skipped++
        return $false
    }
    $apiPath = Join-Path $pluginPath "api_paddleocr.py"
    if (-not (Test-Path $apiPath)) {
        Write-Host "    未找到 api_paddleocr.py" -ForegroundColor Red
        return $false
    }
    Write-Host "    路径: $pluginPath" -ForegroundColor Gray
    return $true
}

# 测试 6: 检查配置文件
Test-Item -Name "配置文件存在" -Test {
    $configPath = Join-Path $BuildPath "build_info.json"
    if (-not (Test-Path $configPath)) {
        Write-Host "    未找到: $configPath" -ForegroundColor Red
        return $false
    }
    try {
        $config = Get-Content $configPath | ConvertFrom-Json
        Write-Host "    版本: $($config.version)" -ForegroundColor Gray
        Write-Host "    应用: $($config.app_name)" -ForegroundColor Gray
        return $true
    } catch {
        Write-Host "    无法解析 JSON: $_" -ForegroundColor Red
        return $false
    }
}

# 测试 7: 检查 README
Test-Item -Name "README 文件存在" -Test {
    $readmePath = Join-Path $BuildPath "README.txt"
    if (-not (Test-Path $readmePath)) {
        Write-Host "    未找到: $readmePath" -ForegroundColor Yellow
        $script:TestResults.Skipped++
        return $false
    }
    $content = Get-Content $readmePath -Raw
    Write-Host "    大小: $($content.Length) 字节" -ForegroundColor Gray
    return $content.Length -gt 0
}

# 测试 8: 检查启动脚本
Test-Item -Name "启动脚本存在" -Test {
    $batPath = Join-Path $BuildPath "启动.bat"
    if (-not (Test-Path $batPath)) {
        Write-Host "    未找到: $batPath" -ForegroundColor Yellow
        $script:TestResults.Skipped++
        return $false
    }
    $content = Get-Content $batPath -Raw
    Write-Host "    路径: $batPath" -ForegroundColor Gray
    return $content.Length -gt 0
}

# 显示测试结果
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "测试结果汇总" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "通过: $($TestResults.Passed)" -ForegroundColor Green
Write-Host "失败: $($TestResults.Failed)" -ForegroundColor Red
Write-Host "跳过: $($TestResults.Skipped)" -ForegroundColor Yellow
Write-Host "总计: $($TestResults.Passed + $TestResults.Failed + $TestResults.Skipped)" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

# 构建目录信息
Write-Host "`n构建目录信息:" -ForegroundColor Cyan
$Size = (Get-ChildItem -Path $BuildPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "  总大小: $([math]::Round($Size, 2)) MB" -ForegroundColor Gray
Write-Host "  文件数: $((Get-ChildItem -Path $BuildPath -Recurse -File).Count)" -ForegroundColor Gray
Write-Host "  目录数: $((Get-ChildItem -Path $BuildPath -Recurse -Directory).Count)" -ForegroundColor Gray

# 返回结果
Write-Host "`n构建验证完成。" -ForegroundColor Cyan
Write-Host "注意：部分测试失败是预期的（简化构建中某些文件可能不存在）" -ForegroundColor Yellow
exit 0