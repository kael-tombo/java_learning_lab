#!/bin/bash

###############################################################################
# Multi-Agent All Modules Validation Script
# 
# This script validates ALL modules in the Java Learning Journey using
# the multi-agent validation system.
#
# Usage: ./validate-all-modules.sh
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REPORT_DIR="$PROJECT_ROOT/validation-reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SUMMARY_FILE="$REPORT_DIR/summary_${TIMESTAMP}.txt"

# Statistics
TOTAL_MODULES=0
PASSED_MODULES=0
FAILED_MODULES=0

###############################################################################
# Module Lists
###############################################################################

# Core Java Modules (auto-discovered: every 01-core-java/*/pom.xml on disk)
# NOTE: historic hard-coded lists (01-hello-world, 02-spring-boot/*,
# hello-quarkus, EclipseVert.XLearning, micronaut-learning) were removed
# because those paths do not exist. Modules are discovered dynamically below.
CORE_JAVA_MODULES=()
SPRING_BOOT_MODULES=()
QUARKUS_MODULES=()
VERTX_MODULES=()
MICRONAUT_MODULES=()
# When set to 1, discover all leaf Maven modules via find instead of lists.
DISCOVER_MODULES=1

###############################################################################
# Helper Functions
###############################################################################

print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                  ║"
    echo "║        🤖 Multi-Agent All Modules Validation System 🤖          ║"
    echo "║                                                                  ║"
    echo "║              Validating Every Module with 10+ Agents            ║"
    echo "║                                                                  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

print_category_header() {
    local category=$1
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  📦 $category${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

validate_module() {
    local module_path=$1
    local module_name=$(basename "$module_path")
    
    TOTAL_MODULES=$((TOTAL_MODULES + 1))
    
    echo -e "${BLUE}▶ Validating: $module_name${NC}"
    
    # Check if module exists
    if [ ! -d "$PROJECT_ROOT/$module_path" ]; then
        echo -e "${YELLOW}  ⚠ Module not found: $module_path${NC}"
        echo "  ⚠ $module_name - NOT FOUND" >> "$SUMMARY_FILE"
        return
    fi
    
    # Run validation
    if bash "$SCRIPT_DIR/validate-module.sh" "$module_path" > /dev/null 2>&1; then
        echo -e "${GREEN}  ✓ $module_name - PASSED${NC}"
        echo "  ✓ $module_name - PASSED" >> "$SUMMARY_FILE"
        PASSED_MODULES=$((PASSED_MODULES + 1))
    else
        echo -e "${RED}  ✗ $module_name - FAILED${NC}"
        echo "  ✗ $module_name - FAILED" >> "$SUMMARY_FILE"
        FAILED_MODULES=$((FAILED_MODULES + 1))
    fi
}

validate_category() {
    local category_name=$1
    shift
    local modules=("$@")
    
    print_category_header "$category_name"
    
    for module in "${modules[@]}"; do
        validate_module "$module"
    done
}

print_final_summary() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}                    📊 FINAL VALIDATION SUMMARY                   ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local pass_rate=0
    if [ $TOTAL_MODULES -gt 0 ]; then
        pass_rate=$((PASSED_MODULES * 100 / TOTAL_MODULES))
    fi
    
    echo "Total Modules Validated: $TOTAL_MODULES"
    echo -e "${GREEN}Passed: $PASSED_MODULES${NC}"
    echo -e "${RED}Failed: $FAILED_MODULES${NC}"
    echo "Pass Rate: ${pass_rate}%"
    echo ""
    
    if [ $FAILED_MODULES -eq 0 ]; then
        echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║${NC}                  🎉 ALL MODULES PASSED! 🎉                      ${GREEN}║${NC}"
        echo -e "${GREEN}║${NC}              Every module is production-ready!                  ${GREEN}║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    else
        echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║${NC}              ⚠ Some modules need improvement ⚠                 ${YELLOW}║${NC}"
        echo -e "${YELLOW}║${NC}          Please review the validation reports                  ${YELLOW}║${NC}"
        echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════════╝${NC}"
    fi
    
    echo ""
    echo "Detailed reports saved to: $REPORT_DIR"
    echo "Summary saved to: $SUMMARY_FILE"
    echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
    print_banner
    
    # Create report directory
    mkdir -p "$REPORT_DIR"
    
    # Initialize summary file
    echo "╔══════════════════════════════════════════════════════════════════╗" > "$SUMMARY_FILE"
    echo "║        Multi-Agent Module Validation Summary                    ║" >> "$SUMMARY_FILE"
    echo "║        Generated: $(date)                      ║" >> "$SUMMARY_FILE"
    echo "╚══════════════════════════════════════════════════════════════════╝" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"
    
    # Validate all categories (dynamic discovery — never stale)
    if [ "$DISCOVER_MODULES" = "1" ]; then
        print_category_header "All Maven Modules (auto-discovered)"
        while IFS= read -r pom; do
            module_dir=$(dirname "$pom")
            # Skip root poms; validate leaf modules only
            if [ "$module_dir" = "." ]; then
                continue
            fi
            validate_module "$module_dir"
        done < <(find "$PROJECT_ROOT" -name pom.xml -not -path "*/target/*" -not -path "*/.git/*" | sed "s|^$PROJECT_ROOT/||" | sort)
    else
        validate_category "Core Java Modules" "${CORE_JAVA_MODULES[@]}"
        validate_category "Spring Boot Modules" "${SPRING_BOOT_MODULES[@]}"
        validate_category "Quarkus Modules" "${QUARKUS_MODULES[@]}"
        validate_category "Vert.x Modules" "${VERTX_MODULES[@]}"
        validate_category "Micronaut Modules" "${MICRONAUT_MODULES[@]}"
    fi
    
    # Print final summary
    print_final_summary
    
    # Return exit code
    if [ $FAILED_MODULES -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Execute main function
main