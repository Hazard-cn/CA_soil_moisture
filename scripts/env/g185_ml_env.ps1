$ErrorActionPreference = "Stop"

$ProjectRoot = "C:\YangSu\00_Project\CA_mechanism\regression_SR"
$env:PYTHON_ML = Join-Path $ProjectRoot ".venv-ml\Scripts\python.exe"
$env:RSCRIPT_EXE = "C:\Users\Lenovo\AppData\Local\Programs\R\bin\Rscript.exe"

if (!(Test-Path -LiteralPath $env:PYTHON_ML)) {
    throw "Missing ML Python interpreter: $env:PYTHON_ML"
}
if (!(Test-Path -LiteralPath $env:RSCRIPT_EXE)) {
    throw "Missing Rscript executable: $env:RSCRIPT_EXE"
}

Write-Output "PYTHON_ML=$env:PYTHON_ML"
Write-Output "RSCRIPT_EXE=$env:RSCRIPT_EXE"
