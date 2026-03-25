#!/usr/bin/env bash
set -euo pipefail
echo "=== Running E2E tests ==="
pytest tests/e2e/ -m e2e -v --tb=long \
  --alluredir=reports/allure-results \
  --html=reports/html/e2e_report.html \
  --self-contained-html "$@"
