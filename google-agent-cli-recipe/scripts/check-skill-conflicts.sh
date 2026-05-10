#!/usr/bin/env bash
# check-skill-conflicts.sh — detect (and optionally isolate) other skills
# that may conflict with the retail-* skills' Q-MODE flow.
#
# Usage:
#   ./scripts/check-skill-conflicts.sh           # detect only
#   ./scripts/check-skill-conflicts.sh --isolate # rename conflicting skills out of the way
#   ./scripts/check-skill-conflicts.sh --restore # rename them back
#
# Conflicting skills (known): adk-scaffold, google-agents-cli-workflow, and any
# user-scoped retail-* skill from a previous install.

set -euo pipefail

bold=$'\033[1m'; green=$'\033[32m'; yellow=$'\033[33m'; red=$'\033[31m'; nc=$'\033[0m'

KNOWN_CONFLICTS=(
  "adk-scaffold"
  "google-agents-cli-workflow"
)

# User-scoped skill directories across common AI coding agents
SKILL_DIRS=(
  "$HOME/.agents/skills"
  "$HOME/.gemini/skills"
  "$HOME/.claude/skills"
)

mode="${1:-detect}"
case "$mode" in
  --isolate) action="isolate" ;;
  --restore) action="restore" ;;
  ""|--detect|detect) action="detect" ;;
  -h|--help)
    sed -n '2,12p' "$0"
    exit 0
    ;;
  *) echo "${red}unknown flag:${nc} $mode" >&2; exit 1 ;;
esac

found=0
for dir in "${SKILL_DIRS[@]}"; do
  [[ -d "$dir" ]] || continue
  for c in "${KNOWN_CONFLICTS[@]}"; do
    src="$dir/$c"
    disabled="$dir/_disabled-$c"
    if [[ -d "$src" || -f "$src.md" ]]; then
      found=1
      case "$action" in
        detect)
          printf "  ${yellow}!${nc} conflict at: %s\n" "$src"
          ;;
        isolate)
          if [[ -d "$src" ]]; then
            mv "$src" "$disabled"
          else
            mv "$src.md" "$disabled.md"
          fi
          printf "  ${green}✓${nc} isolated: %s -> %s\n" "$src" "$disabled"
          ;;
      esac
    fi
    if [[ "$action" == "restore" && (-d "$disabled" || -f "$disabled.md") ]]; then
      found=1
      if [[ -d "$disabled" ]]; then
        mv "$disabled" "$src"
      else
        mv "$disabled.md" "$src.md"
      fi
      printf "  ${green}✓${nc} restored: %s\n" "$src"
    fi
  done
done

if [[ $found -eq 0 ]]; then
  case "$action" in
    detect)  printf "${green}No conflicting skills found.${nc} Safe to proceed.\n" ;;
    isolate) printf "${green}Nothing to isolate.${nc}\n" ;;
    restore) printf "${green}Nothing to restore.${nc}\n" ;;
  esac
  exit 0
fi

case "$action" in
  detect)
    printf "\n${bold}Three ways to force precedence for the retail skill:${nc}\n"
    printf "  1. ${cyan-}./scripts/check-skill-conflicts.sh --isolate${nc}\n"
    printf "     (renames the conflicting skills out of the way; reverse with --restore)\n"
    printf "  2. Prefix your first message with: \"Use only the retail-product-search skill.\"\n"
    printf "  3. Run the demo from a project dir; project-scoped .gemini/skills/ usually wins.\n"
    ;;
  isolate)
    printf "\n${green}Done.${nc} Reverse with: ./scripts/check-skill-conflicts.sh --restore\n"
    ;;
  restore)
    printf "\n${green}Done.${nc}\n"
    ;;
esac
