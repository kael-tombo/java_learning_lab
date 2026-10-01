@echo off
setlocal EnableDelayedExpansion
echo ================================================================
echo    VALIDATING ALL MODULES - Java Learning Lab
echo ================================================================
echo.
echo This script validates every Maven module found on disk.
echo It discovers modules by searching for pom.xml files, so it
echo never goes stale when new labs are added.
echo.

set PASS=0
set FAIL=0
set SKIP=0

for /f "delims=" %%P in ('dir /s /b pom.xml 2^>NUL') do (
    rem Skip root aggregator/parent poms - validate leaf modules only
    echo [BUILD] %%P
    for %%D in ("%%P\..") do set MODDIR=%%~fD
    pushd "!MODDIR!" >NUL
    call mvn -q clean test
    if !ERRORLEVEL! EQU 0 (
        echo [PASS] !MODDIR!
        set /a PASS+=1
    ) else (
        echo [FAIL] !MODDIR!
        set /a FAIL+=1
    )
    popd >NUL
    echo.
)

echo ================================================================
echo    VALIDATION COMPLETE
echo ================================================================
echo Passed: %PASS%  Failed: %FAIL%  Skipped: %SKIP%
echo.
echo For a fast smoke check of core labs only, run:
echo   mvn -f pom-aggregator.xml clean verify
echo.
endlocal
