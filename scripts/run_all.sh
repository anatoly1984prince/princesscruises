#!/usr/bin/env bash
set -euo pipefail
echo "=== Running ALL tests in parallel ==="
pytest tests/ -v --tb=short -n auto \
  --alluredir=reports/allure-results \
  --html=reports/html/full_report.html \
  --self-contained-html "$@"
