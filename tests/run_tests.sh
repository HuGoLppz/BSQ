#!/bin/bash
# Runs every BSQ test. Usage: bash run_tests.sh   (from any directory, on Linux)

cd "$(dirname "$0")" || exit 1
BSQ=../ex00/bsq
TMP=$(mktemp -d)
PASS=0
FAIL=0
trap 'rm -rf "$TMP"' EXIT

ok() { PASS=$((PASS + 1)); echo "  OK  $1"; }
ko() { FAIL=$((FAIL + 1)); echo "  KO  $1"; }
check() { if eval "$2"; then ok "$1"; else ko "$1"; fi; }

echo "== Makefile"
make -C ../ex00 fclean >/dev/null
check "make compiles with -Wall -Wextra -Werror" "make -C ../ex00 >/dev/null 2>&1"
check "make does not relink" "make -C ../ex00 2>&1 | grep -q 'Nothing to be done'"

echo "== Subject example"
$BSQ maps/valid/example_subject >"$TMP/out" 2>"$TMP/err"
check "output equals the PDF" "cmp -s $TMP/out maps/valid/example_subject.expected"

echo "== Valid maps (compared with reference.py)"
for map in maps/valid/*; do
	[[ $map == *.expected ]] && continue
	python3 reference.py "$map" >"$TMP/exp"
	$BSQ "$map" >"$TMP/out" 2>"$TMP/err"
	check "$(basename "$map")" "cmp -s $TMP/exp $TMP/out && [ ! -s $TMP/err ]"
done

echo "== Invalid maps (expect 'map error' on stderr, nothing on stdout)"
for map in maps/invalid/* /does/not/exist; do
	$BSQ "$map" >"$TMP/out" 2>"$TMP/err"
	check "$(basename "$map")" "[ ! -s $TMP/out ] && [ \"\$(cat $TMP/err)\" = 'map error' ]"
done

echo "== Standard input"
$BSQ <maps/valid/example_subject >"$TMP/out"
check "./bsq < map" "cmp -s $TMP/out maps/valid/example_subject.expected"
cat maps/valid/example_subject | $BSQ >"$TMP/out"
check "cat map | ./bsq" "cmp -s $TMP/out maps/valid/example_subject.expected"
$BSQ <maps/invalid/empty_file >"$TMP/out" 2>"$TMP/err"
check "empty stdin -> map error" "[ \"\$(cat $TMP/err)\" = 'map error' ]"

echo "== Several files (blank line between results)"
{ cat maps/valid/example_subject.expected; echo; echo; \
  python3 reference.py maps/valid/tie_break; } >"$TMP/exp"
$BSQ maps/valid/example_subject maps/invalid/fewer_lines maps/valid/tie_break \
	>"$TMP/out" 2>"$TMP/err"
check "valid + invalid + valid" "cmp -s $TMP/exp $TMP/out && [ \"\$(cat $TMP/err)\" = 'map error' ]"

echo "== 300 random maps (random sizes, densities and characters)"
mkdir "$TMP/random"
python3 reference.py --random 42 "$TMP/random" 300
BAD=0
for map in "$TMP"/random/*; do
	python3 reference.py "$map" >"$TMP/exp"
	$BSQ "$map" >"$TMP/out" 2>/dev/null
	cmp -s "$TMP/exp" "$TMP/out" || { BAD=$((BAD + 1)); echo "     differs: $map"; }
done
check "all random maps match the reference" "[ $BAD -eq 0 ]"

if command -v valgrind >/dev/null; then
	echo "== Valgrind (no leaks, no errors)"
	VG="valgrind --leak-check=full --error-exitcode=42 --errors-for-leak-kinds=all -q"
	check "valid map" "$VG $BSQ maps/valid/example_subject >/dev/null"
	check "invalid map" "$VG $BSQ maps/invalid/different_lengths >/dev/null 2>&1; [ \$? -ne 42 ]"
	check "stdin" "$VG $BSQ <maps/valid/all_empty >/dev/null"
	check "several files" "$VG $BSQ maps/valid/* /nope >/dev/null 2>&1; [ \$? -ne 42 ]"
fi

echo
echo "Result: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ]
