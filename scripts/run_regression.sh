#!/usr/bin/env bash
set -euo pipefail
echo "=== Running REGRESSION tests ==="
pytest tests/regression/ -m regression -v --tb=short -n auto \
  --alluredir=reports/allure-results \
  --html=reports/html/regression_report.html \
  --self-contained-html "$@"
