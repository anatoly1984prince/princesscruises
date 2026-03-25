#!/usr/bin/env bash
set -euo pipefail
echo "=== Generating Allure Report ==="
allure generate reports/allure-results --clean -o reports/allure-report
allure open reports/allure-report
