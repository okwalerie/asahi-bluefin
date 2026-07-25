#!/usr/bin/env bash
# make update-m1n1 compatible with rpm-ostree's epoch-zero file mtimes.
set -euo pipefail

target=${1:-/usr/bin/update-m1n1}
# these are literal source lines, not expressions to expand here.
# shellcheck disable=SC2016
old='gzip -c "$U_BOOT" >>"${TARGET}.new"'
# shellcheck disable=SC2016
new='gzip -nc "$U_BOOT" >>"${TARGET}.new"'

if [[ $(grep -Fxc "$old" "$target") -ne 1 ]]; then
  echo "error: expected exactly one unpatched update-m1n1 gzip command" >&2
  exit 1
fi

temporary=$(mktemp)
trap 'rm -f "$temporary"' exit

while IFS= read -r line; do
  if [[ $line == "$old" ]]; then
    printf '%s\n' "$new"
  else
    printf '%s\n' "$line"
  fi
done <"$target" >"$temporary"

cat "$temporary" >"$target"
grep -Fqx "$new" "$target"
