# Type checking script for SeleniumPelican (PowerShell)
# Usage: .\scripts\type_check.ps1 [-Report]

param(
    [switch]$Report
)

# Function to print colored messages
function Write-Info {
    param([string]$Message)
    Write-Host "🔍 $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Main type checking
Write-Info "Running mypy type checker..."

# Check if in virtual environment
$mypyCmd = if ($env:VIRTUAL_ENV) {
    "mypy"
} else {
    Write-Warning "Not in virtual environment, using uv run"
    "uv run mypy"
}

try {
    # Run mypy on src directory
    $output = & $mypyCmd src/ --config-file pyproject.toml 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Success "Type check completed with no errors"
    } else {
        Write-Host $output
        Write-Error-Custom "Type check failed - please fix the errors above"
        exit 1
    }

    # Generate reports if requested
    if ($Report) {
        Write-Info "Generating type coverage reports..."

        # Generate HTML report
        & $mypyCmd src/ --config-file pyproject.toml --html-report mypy-html --no-error-summary 2>$null

        # Generate text report
        & $mypyCmd src/ --config-file pyproject.toml --txt-report mypy-report --no-error-summary 2>$null

        if (Test-Path "mypy-html") {
            Write-Success "HTML report generated at: mypy-html/index.html"
        }

        if (Test-Path "mypy-report") {
            Write-Success "Text report generated at: mypy-report/"
        }
    }

    exit 0
} catch {
    Write-Error-Custom "Type check execution failed: $_"
    exit 1
}
