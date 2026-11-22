#!/usr/bin/env bash
# Uji CRUD UTS IF133 - 19 skenario Soal 2 + Soal 3
# Jalankan SETELAH memastikan database kosong (delete uts-if133.db lalu
# dotnet ef database update), atau script ini akan gagal di skenario POST valid
# karena Code PRD-001 sudah terdaftar dari run sebelumnya.

BASE="http://localhost:5070/api"
OUT="C:/Users/Administrator/AppData/Local/hermes/profiles/college/cache/scratch/rb_uts.json"
HDR="C:/Users/Administrator/AppData/Local/hermes/profiles/college/cache/scratch/hdr_uts.txt"
PASS=0; FAIL=0

chk() {
  if [ "$2" = "$3" ]; then echo "  [OK]    $1 -> $3"; PASS=$((PASS+1));
  else echo "  [GAGAL] $1 -> dapat '$3', harusnya '$2'"; FAIL=$((FAIL+1)); fi
}

req() {
  local m=$1 p=$2 d=$3
  local args=(-s -o "$OUT" -D "$HDR" -w "%{http_code}" -X "$m" "$BASE$p" -H "Content-Type: application/json")
  [ -n "$d" ] && args+=(-d "$d")
  CODE=$(curl "${args[@]}")
  BODY=$(cat "$OUT" 2>/dev/null)
}

jget() { echo "$BODY" | py -3.13 -c "import sys,json;d=json.load(sys.stdin);print(d.get('$1',''))" 2>/dev/null; }

echo "=========== A. GET LIST (awal, harus kosong) ==========="
req GET /products
chk "GET /api/products" 200 "$CODE"
echo "     body: $BODY"

echo
echo "=========== B. POST valid (data contoh soal) ==========="
req POST /products '{"code":"PRD-001","name":"Keyboard Mechanical","price":750000,"stock":12,"isActive":true}'
chk "POST produk valid" 201 "$CODE"
PID=$(jget id)
echo "     body: $BODY"
echo "     Location: $(grep -i '^location:' "$HDR" | tr -d '\r' | cut -d' ' -f2-)"
grep -qi "^location:.*$PID" "$HDR" && { echo "  [OK]    Location mengarah ke resource baru"; PASS=$((PASS+1)); } || { echo "  [GAGAL] Location salah"; FAIL=$((FAIL+1)); }

echo
echo "=========== C. POST Code duplikat -> 409 ==========="
req POST /products '{"code":"PRD-001","name":"Produk Lain","price":100000,"stock":5,"isActive":true}'
chk "POST Code duplikat" 409 "$CODE"
echo "     body: $BODY"

echo
echo "=========== D. POST validasi gagal -> 400 ==========="
req POST /products '{"code":"","name":"","price":0,"stock":-5,"isActive":true}'
chk "POST semua field tidak valid" 400 "$CODE"
echo "     errors: $(jget errors)"

req POST /products '{"code":"PRD-002-EXTRA-PANJANG-SEKALI","name":"X","price":1000,"stock":1,"isActive":true}'
chk "POST Code > 20 karakter" 400 "$CODE"

req POST /products '{"code":"PRD 003","name":"Produk Spasi","price":1000,"stock":1,"isActive":true}'
chk "POST Code mengandung spasi" 400 "$CODE"

echo
echo "=========== E. POST data kedua & ketiga ==========="
req POST /products '{"code":"PRD-002","name":"Mouse Wireless","price":275000,"stock":30,"isActive":true}'
chk "POST produk kedua" 201 "$CODE"
PID2=$(jget id)

req POST /products '{"code":"PRD-003","name":"Monitor 24 Inch","price":1850000,"stock":0,"isActive":false}'
chk "POST produk ketiga" 201 "$CODE"
echo "     body: $BODY"

echo
echo "=========== F. GET by id ==========="
req GET "/products/$PID"
chk "GET id ada" 200 "$CODE"
echo "     body: $BODY"

req GET /products/9999
chk "GET id tidak ada" 404 "$CODE"
echo "     body: $BODY"

echo
echo "=========== G. GET list berisi 3 produk ==========="
req GET /products
chk "GET list" 200 "$CODE"
echo "     jumlah: $(echo "$BODY" | py -3.13 -c "import sys,json;print(len(json.load(sys.stdin)))" 2>/dev/null)"

echo
echo "=========== H. PUT ==========="
req PUT "/products/$PID" '{"code":"PRD-001","name":"Keyboard Mechanical RGB","price":825000,"stock":8,"isActive":true}'
chk "PUT produk ada" 204 "$CODE"
echo "     sesudah update: $(curl -s "$BASE/products/$PID")"

req PUT /products/9999 '{"code":"PRD-999","name":"Hantu","price":1000,"stock":1,"isActive":true}'
chk "PUT id tidak ada" 404 "$CODE"

req PUT "/products/$PID2" '{"code":"PRD-001","name":"Tabrak Kode","price":100000,"stock":1,"isActive":true}'
chk "PUT Code milik produk lain" 409 "$CODE"

req PUT "/products/$PID" '{"code":"PRD-001","name":"","price":-1,"stock":-2,"isActive":true}'
chk "PUT payload tidak valid" 400 "$CODE"

echo
echo "=========== I. DELETE ==========="
req DELETE "/products/$PID2"
chk "DELETE produk ada" 204 "$CODE"

req DELETE "/products/$PID2"
chk "DELETE produk yang sama lagi" 404 "$CODE"

req GET "/products/$PID2"
chk "GET produk terhapus" 404 "$CODE"

echo
echo "=========== J. Centralized error handling -> 500 ==========="
CODE=$(curl -s -o "$OUT" -w "%{http_code}" "$BASE/diagnostics/error")
BODY=$(cat "$OUT")
chk "GET /api/diagnostics/error" 500 "$CODE"
echo "     body: $BODY"
if echo "$BODY" | grep -qiE "stack|at Microsoft|Exception|C:\\\\"; then
  echo "  [GAGAL] body membocorkan detail internal"; FAIL=$((FAIL+1))
else
  echo "  [OK]    body tidak membocorkan stack trace / path server"; PASS=$((PASS+1))
fi

echo
echo "=========== K. Kondisi akhir ==========="
req GET /products
echo "     sisa: $(echo "$BODY" | py -3.13 -c "import sys,json;d=json.load(sys.stdin);print(len(d),'->',[p['code'] for p in d])" 2>/dev/null)"

echo
echo "=========================================="
echo "RINGKASAN: $PASS lulus, $FAIL gagal"
