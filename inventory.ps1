$targetFiles = @('README.md', 'THEORY.md', 'CODE_DEEP_DIVE.md', 'MATH_FOUNDATION.md', 'EXERCISES.md', 'QUIZ.md', 'FLASHCARDS.md', 'MINI_PROJECT', 'REAL_WORLD_PROJECT')
$academies = @('data-science', 'ml', 'mlops')
$results = @()

foreach ($academy in $academies) {
    $path = "C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\$academy\"
    $dirs = Get-ChildItem -Path $path -Directory | Where-Object { $_.Name -match '^\d{2}-' } | Sort-Object Name
    Write-Host "=== $academy ==="
    foreach ($dir in $dirs) {
        $files = Get-ChildItem -Path $dir.FullName
        $has = @{}
        foreach ($tf in $targetFiles) {
            if ($tf -eq 'MINI_PROJECT' -or $tf -eq 'REAL_WORLD_PROJECT') {
                $has[$tf] = (Get-ChildItem -Path $dir.FullName -Directory -Name -ErrorAction SilentlyContinue | Where-Object { $_ -eq $tf }).Count -gt 0
            } else {
                $has[$tf] = (Get-ChildItem -Path $dir.FullName -File -Name -ErrorAction SilentlyContinue | Where-Object { $_ -eq $tf }).Count -gt 0
            }
        }
        $missing = $targetFiles | Where-Object { -not $has[$_] }
        $present = $targetFiles | Where-Object { $has[$_] }
        $result = [PSCustomObject]@{
            Academy = $academy
            Lab = $dir.Name
            Present = ($present -join ', ')
            Missing = ($missing -join ', ')
            MissingCount = $missing.Count
        }
        $results += $result
        Write-Host "$($dir.Name): Present=$($present.Count) Missing=$($missing.Count) [$($missing -join ', ')]"
    }
}

$results | Export-Csv -Path "C:\Users\jratombo-adm\Desktop\java_learning_lab\inventory_results.csv" -NoTypeInformation
Write-Host "Done. Results saved to inventory_results.csv"