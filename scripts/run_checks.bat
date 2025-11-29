@echo off
echo ==========================================
echo Running Local Quality Checks
echo ==========================================

echo.
echo [1/3] Running Black (Code Formatting)...
black --check .
if %errorlevel% neq 0 (
    echo [ERROR] Black failed. Run 'black .' to fix formatting.
    exit /b %errorlevel%
)

echo.
echo [2/3] Running Flake8 (Linting)...
flake8 .
if %errorlevel% neq 0 (
    echo [ERROR] Flake8 failed. Fix linting errors.
    exit /b %errorlevel%
)

echo.
echo [3/3] Running Tests...
pytest
if %errorlevel% neq 0 (
    echo [ERROR] Tests failed.
    exit /b %errorlevel%
)

echo.
echo ==========================================
echo [SUCCESS] All checks passed!
echo ==========================================
