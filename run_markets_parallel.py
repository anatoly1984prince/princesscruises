"""Run US, UK, and AU market tests in parallel using subprocess.

Usage:
    python run_markets_parallel.py [--markets us uk au] [--no-html]

Each market runs as a separate pytest subprocess writing to its own log file
and HTML report. The script waits for all three to finish and prints a summary.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

MARKETS = {
    "us": {
        "test_path": "tests/markets/us/",
        "allure_dir": "reports/allure-results-us",
        "html_report": "reports/html/report-us.html",
        "log_file": "reports/us-market.log",
    },
    "uk": {
        "test_path": "tests/markets/uk/",
        "allure_dir": "reports/allure-results-uk",
        "html_report": "reports/html/report-uk.html",
        "log_file": "reports/uk-market.log",
    },
    "au": {
        "test_path": "tests/markets/au/",
        "allure_dir": "reports/allure-results-au",
        "html_report": "reports/html/report-au.html",
        "log_file": "reports/au-market.log",
    },
}


def run_market(market: str, cfg: dict, html: bool = True) -> subprocess.Popen:
    """Launch a pytest subprocess for the given market."""
    cmd = [
        sys.executable, "-m", "pytest",
        cfg["test_path"],
        f"--alluredir={cfg['allure_dir']}",
        "-v", "--tb=short",
        "--reruns=1", "--reruns-delay=2",
    ]
    if html:
        cmd += [f"--html={cfg['html_report']}", "--self-contained-html"]

    log_path = Path(cfg["log_file"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = log_path.open("w", encoding="utf-8")

    print(f"[{market.upper()}] Starting - output -> {log_path}")
    proc = subprocess.Popen(cmd, stdout=log_fh, stderr=subprocess.STDOUT)
    proc._market = market
    proc._log_path = log_path
    proc._log_fh = log_fh
    return proc


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Princess.com market tests in parallel")
    parser.add_argument(
        "--markets", nargs="+", default=list(MARKETS.keys()),
        choices=list(MARKETS.keys()),
        help="Which markets to run (default: all three)",
    )
    parser.add_argument("--no-html", action="store_true", help="Skip HTML report generation")
    args = parser.parse_args()

    Path("reports/html").mkdir(parents=True, exist_ok=True)

    start = time.time()
    procs = [
        run_market(m, MARKETS[m], html=not args.no_html)
        for m in args.markets
    ]

    print(f"\nRunning {len(procs)} market(s) in parallel. Press Ctrl+C to abort.\n")

    results: dict[str, int] = {}
    for proc in procs:
        try:
            proc.wait()
        except KeyboardInterrupt:
            for p in procs:
                p.terminate()
            print("\nAborted.")
            return 1
        finally:
            proc._log_fh.close()
        results[proc._market] = proc.returncode

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"MARKET TEST RESULTS  ({elapsed:.0f}s total)")
    print(f"{'='*60}")
    overall = 0
    for market, rc in results.items():
        status = "PASSED" if rc == 0 else "FAILED"
        log = MARKETS[market]["log_file"]
        print(f"  {market.upper():4s}  {status}  (exit {rc})  ->  {log}")
        if rc != 0:
            overall = rc
    print(f"{'='*60}")
    return overall


if __name__ == "__main__":
    sys.exit(main())
