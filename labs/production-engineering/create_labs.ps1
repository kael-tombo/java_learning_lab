$labs = @(
    "01-jvm-memory-gc",
    "02-concurrency-production",
    "03-production-debugging",
    "04-distributed-resilience",
    "05-database-production",
    "06-microservices-scale",
    "07-kubernetes-java",
    "08-observability-sre",
    "09-security-production",
    "10-api-design-scale",
    "11-event-driven-production",
    "12-caching-production",
    "13-cicd-release-engineering",
    "14-incident-response",
    "15-performance-engineering",
    "16-cost-engineering",
    "17-data-architecture",
    "18-chaos-engineering",
    "19-architect-decisions",
    "20-production-readiness"
)

$files = @(
    "README.md",
    "THEORY.md",
    "PRODUCTION_SCENARIOS.md",
    "CODE_DEEP_DIVE.md",
    "ARCHITECTURE_DECISIONS.md",
    "RUNBOOKS.md",
    "INTERVIEW_QUESTIONS.md",
    "EXERCISES.md",
    "ANTI_PATTERNS.md",
    "CHECKLIST.md"
)

foreach ($lab in $labs) {
    $dir = Join-Path $PSScriptRoot $lab
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    foreach ($file in $files) {
        $path = Join-Path $dir $file
        if (-not (Test-Path $path)) {
            New-Item -ItemType File -Path $path -Force | Out-Null
        }
    }
    Write-Host "Created: $lab"
}
Write-Host "Done! All lab directories created."
