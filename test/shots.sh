#!/usr/bin/env bash
# Launch Boat Timetable with several colour/background settings and grab the
# front screen (curl only). Restores cyan + animated at the end.
#   test/shots.sh [HOST]   -> test/shots/*.raw, then: python3 test/shots.py
cd "$(dirname "$0")"
B=http://${1:-10.0.4.20}
ID=io.github.alexseminoisok.boats
S="$B/api/apps/settings?app_id=$ID"
put() { curl -s -m 5 -X PUT -H 'Content-Type: application/json' \
  -d "{\"version\":1,\"values\":{\"pier\":\"930GMIL\",\"colour\":\"$1\",\"background\":\"$2\"}}" \
  "$S" -o /dev/null -w "put $1/$2 %{http_code}\n"; }
quit() { curl -s -m 5 -X POST "$B/api/apps/quit" -o /dev/null; sleep 1.5; }
launch() { curl -s -m 5 -X POST "$B/api/apps/launch?app_id=$ID" -o /dev/null -w "launch %{http_code}\n"; }
shot() { curl -s -m 5 "$B/api/screen?display=0" -o "shots/$1.raw" -w "shot $1 %{http_code}\n"; }
mkdir -p shots && rm -f shots/*.raw
quit
for combo in cyan/animated white/animated lilac/animated amber/gray yellow/black; do
  c=${combo%/*}; b=${combo#*/}
  put "$c" "$b"; launch; sleep 1.5; shot "${c}_${b}_0"
  sleep 4; for i in 1 2 3 4 5 6; do shot "${c}_${b}_$i"; sleep 1.1; done   # >=1 s apart
  quit
done
put cyan animated
