# ── Princess.com Test Automation — Market Targets ─────────────────────────────

.PHONY: test-us test-uk test-au test-all-markets test-all-markets-parallel \
        test-regression test-smoke test-booking

# ── Single-market runs ─────────────────────────────────────────────────────────

test-us:
	pytest tests/markets/us/ \
	    --alluredir=reports/allure-results-us \
	    --html=reports/html/report-us.html \
	    --self-contained-html \
	    -v --tb=short

test-uk:
	pytest tests/markets/uk/ \
	    --alluredir=reports/allure-results-uk \
	    --html=reports/html/report-uk.html \
	    --self-contained-html \
	    -v --tb=short

test-au:
	pytest tests/markets/au/ \
	    --alluredir=reports/allure-results-au \
	    --html=reports/html/report-au.html \
	    --self-contained-html \
	    -v --tb=short

# ── All 3 markets — sequential ────────────────────────────────────────────────

test-all-markets: test-us test-uk test-au

# ── All 3 markets — parallel (background processes) ──────────────────────────

test-all-markets-parallel:
	@echo "Starting US, UK, and AU market tests in parallel..."
	@mkdir -p reports/html reports/allure-results-us reports/allure-results-uk reports/allure-results-au
	@python run_markets_parallel.py

# ── Existing regression / smoke / booking targets ────────────────────────────

test-regression:
	pytest tests/regression/ -m regression -v --tb=short

test-smoke:
	pytest tests/smoke/ -m smoke -v --tb=short

test-booking:
	pytest -m booking -v --tb=short
