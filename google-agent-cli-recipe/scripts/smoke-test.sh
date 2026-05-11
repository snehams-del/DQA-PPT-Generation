#!/usr/bin/env bash
# smoke-test.sh — offline structural sanity check for the whole repo.
#
# Verifies that Python, Bash, Node, and JSON files all parse, that the static
# catalog exists, and that CLI tools dispatch correctly. No GCP, no costs.
#
# Usage: ./scripts/smoke-test.sh

set -uo pipefail

cd "$(dirname "$0")/.."

PASS=0
FAIL=0
FAIL_MSGS=()

bold=$'\033[1m'; green=$'\033[32m'; red=$'\033[31m'; yellow=$'\033[33m'; nc=$'\033[0m'

check() {
    local label="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        printf "  ${green}✓${nc} %s\n" "$label"
        PASS=$((PASS + 1))
    else
        printf "  ${red}✗${nc} %s\n" "$label"
        FAIL=$((FAIL + 1))
        FAIL_MSGS+=("$label")
    fi
}

echo "${bold}1. Python syntax checks${nc}"
check "evals/run.py"       python -c "import ast; ast.parse(open('evals/run.py').read())"
check "evals/improve.py"   python -c "import ast; ast.parse(open('evals/improve.py').read())"
check "tryon_processor.py" python -c "import ast; ast.parse(open('samples/retail-virtual-tryon/app/tryon_processor.py').read())"
check "tryon_agent.py"     python -c "import ast; ast.parse(open('samples/retail-virtual-tryon/app/tryon_agent.py').read())"
check "setup_tryon.py"     python -c "import ast; ast.parse(open('samples/retail-virtual-tryon/scripts/setup_tryon.py').read())"

echo ""
echo "${bold}2. Bash syntax checks${nc}"
check "vs CLI"          bash -n vs
check "smoke-test.sh"   bash -n scripts/smoke-test.sh

echo ""
echo "${bold}3. Node syntax check${nc}"
if command -v node >/dev/null 2>&1; then
    check "npx installer"   node --check packages/install-vertical-skill/bin/install.js
else
    printf "  ${yellow}-${nc} node not installed, skipping\n"
fi

echo ""
echo "${bold}4. Evalset JSON validation${nc}"
for f in evals/sets/*.evalset.json; do
    check "$(basename "$f")" python -c "import json; json.load(open('$f'))"
done

echo ""
echo "${bold}5. SKILL.md presence${nc}"
for skill in retail-product-search retail-virtual-tryon retail-product-recommendation retail-content-generation; do
    check "skills/$skill/SKILL.md" test -f "skills/$skill/SKILL.md"
done

echo ""
echo "${bold}6. Static catalog present${nc}"
check "catalog/index.html"  test -f catalog/index.html
check "catalog/style.css"   test -f catalog/style.css

echo ""
echo "${bold}7. CLI dispatches${nc}"
check "vs --help"   bash -c "./vs --help | grep -q 'Usage:'"
check "vs list"     bash -c "./vs list | grep -q retail-product-search"
check "npx --list"  bash -c "node packages/install-vertical-skill/bin/install.js --list | grep -q retail-product-search"

echo ""
echo "${bold}Summary:${nc} ${green}${PASS} passed${nc}, ${red}${FAIL} failed${nc}"

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "${red}Failures:${nc}"
    for m in "${FAIL_MSGS[@]}"; do
        echo "  - $m"
    done
    exit 1
fi
