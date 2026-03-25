#!/usr/bin/env bash
set -euo pipefail
echo "=== Running SMOKE tests ==="
pytest tests/smoke/ -m smoke -v --tb=short \
  --alluredir=reports/allure-results \
  --html=reports/html/smoke_report.html \
  --self-contained-html "$@"
