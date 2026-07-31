from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from core import ecc_demo, rsa_demo, select_mlkem, shor_factor_emulated
from project_info import COURSE_NAME, PROJECT_NAME, TEAM_LEADER, member_label, team_display, team_to_dict


def int_value(data, key, default):
    try:
        return int(data.get(key, [str(default)])[0])
    except (TypeError, ValueError):
        return default


def float_value(data, key, default):
    try:
        return float(data.get(key, [str(default)])[0])
    except (TypeError, ValueError):
        return default


def render_rows(rows):
    body = []
    for x, value in enumerate(rows):
        body.append(f"<tr><td>{x}</td><td>{value}</td></tr>")
    return "".join(body)


def render_page(data=None, error=None):
    data = data or {}
    n = int_value(data, "n", 15)
    a = int_value(data, "a", 2)
    p = int_value(data, "p", 5)
    q = int_value(data, "q", 11)
    e = int_value(data, "e", 3)
    message = int_value(data, "message", 12)
    rsa_base = int_value(data, "rsa_base", 2)
    ecc_k = int_value(data, "ecc_k", 7)
    required_category = int_value(data, "required_category", 3)
    max_pk = int_value(data, "max_pk", 1400)
    max_ct = int_value(data, "max_ct", 1200)
    w_pk = float_value(data, "w_pk", 0.35)
    w_sk = float_value(data, "w_sk", 0.15)
    w_ct = float_value(data, "w_ct", 0.35)
    w_sec = float_value(data, "w_sec", 0.15)

    shor = shor_factor_emulated(n, a)
    rsa = rsa_demo(p, q, e, message, rsa_base)
    ecc = ecc_demo(ecc_k)
    opt = select_mlkem(required_category, max_pk, max_ct, w_pk, w_sk, w_ct, w_sec)

    alert = f'<div class="alert">{html.escape(error)}</div>' if error else ''
    shor_status = "THÀNH CÔNG" if shor.success else "CẦN THỬ LẠI"
    rsa_status = "THÀNH CÔNG" if rsa.attack_success else "CẦN ĐỔI CƠ SỐ"
    ecc_status = "THÀNH CÔNG" if ecc.success else "THẤT BẠI"
    selected = opt.selected["name"] if opt.selected else "Không có phương án thỏa ràng buộc"

    opt_rows = "".join(
        f"<tr><td>{r['name']}</td><td>{r['category']}</td><td>{r['public_key']}</td>"
        f"<td>{r['ciphertext']}</td><td>{r['score']}</td><td>{'Có' if r['feasible'] else 'Không'}</td></tr>"
        for r in opt.candidates
    )

    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ShorLab - Demo Mật mã nâng cao</title>
<style>
:root{{--bg:#eef3f8;--card:#fff;--ink:#172033;--muted:#607089;--primary:#173f73;--accent:#0f8c86;--line:#d8e1eb;--ok:#0a7b45;--warn:#a15c00}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 Arial,sans-serif}}
header{{background:linear-gradient(135deg,#102d55,#17646f);color:white;padding:34px 6vw 28px}}
header h1{{margin:0 0 8px;font-size:34px}}header p{{margin:0;max-width:930px;color:#dceaf4}}
main{{width:min(1180px,92vw);margin:24px auto 50px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;box-shadow:0 8px 25px rgba(17,43,70,.06)}}
.card h2{{margin:0 0 4px;color:var(--primary);font-size:22px}}.sub{{color:var(--muted);margin:0 0 16px}}
form{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 14px;margin-bottom:18px}}
label{{font-size:13px;color:var(--muted)}}input{{width:100%;padding:9px;border:1px solid #bfcbd8;border-radius:8px;margin-top:3px}}
button{{grid-column:1/-1;border:0;border-radius:8px;padding:11px 16px;background:var(--primary);color:white;font-weight:700;cursor:pointer}}
.result{{border-left:4px solid var(--accent);background:#f5fafb;padding:12px 14px;border-radius:8px;margin:10px 0}}
.status{{font-weight:700;color:var(--ok)}}.warn{{color:var(--warn)}}table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:14px}}
th,td{{padding:8px 9px;border-bottom:1px solid var(--line);text-align:left}}th{{background:#f1f5f9;color:#334a62}}
code{{background:#edf2f7;padding:2px 5px;border-radius:5px}}.wide{{grid-column:1/-1}}.alert{{background:#fff3cd;border:1px solid #f4da82;padding:12px;border-radius:8px;margin-bottom:15px}}
footer{{color:var(--muted);text-align:center;padding:20px}}@media(max-width:850px){{.grid{{grid-template-columns:1fr}}.wide{{grid-column:auto}}}}
</style></head><body>
<header><h1>{PROJECT_NAME}</h1><p>Hệ thống demo phục vụ bài tập lớn {COURSE_NAME}: mô phỏng hậu xử lý của thuật toán Shor, khôi phục khóa RSA, minh họa ECDLP trên đường cong elliptic nhỏ và tối ưu lựa chọn ML-KEM cho thiết bị IoT.</p><p style="margin-top:10px;font-size:13px;color:#c9deea"><b>Nhóm trưởng:</b> {member_label(TEAM_LEADER)}<br><b>Thành viên:</b> {team_display(" &nbsp;|&nbsp; ")}</p></header>
<main>{alert}<div class="grid">
<section class="card"><h2>1. Tìm chu kỳ và phân tích N</h2><p class="sub">Bước lượng tử được mô phỏng bằng phép tìm chu kỳ cổ điển để chạy được trên máy tính thông thường.</p>
<form method="post"><label>N<input name="n" value="{n}"></label><label>Cơ số a<input name="a" value="{a}"></label><button>Chạy mô phỏng Shor</button></form>
<div class="result"><b>Trạng thái:</b> <span class="status {'warn' if not shor.success else ''}">{shor_status}</span><br>
GCD ban đầu: {shor.gcd_initial}; chu kỳ r: {shor.order_r}; a^(r/2) mod N: {shor.x_half}<br>
Thừa số: <b>{shor.factor_1}</b> và <b>{shor.factor_2}</b><br><small>{html.escape(shor.note)}</small></div>
<table><thead><tr><th>x</th><th>a^x mod N</th></tr></thead><tbody>{render_rows(shor.powers)}</tbody></table></section>

<section class="card"><h2>2. Tấn công RSA đầu-cuối</h2><p class="sub">Tạo khóa, mã hóa, phân tích n, khôi phục d và giải mã bản mã.</p>
<form method="post"><label>p<input name="p" value="{p}"></label><label>q<input name="q" value="{q}"></label><label>e<input name="e" value="{e}"></label><label>Bản rõ m<input name="message" value="{message}"></label><label>Cơ số Shor<input name="rsa_base" value="{rsa_base}"></label><button>Chạy tấn công RSA</button></form>
<div class="result"><b>Trạng thái:</b> <span class="status {'warn' if not rsa.attack_success else ''}">{rsa_status}</span><br>
Khóa công khai: (n,e)=({rsa.n},{rsa.e}); khóa bí mật d={rsa.d}<br>
Bản mã C={rsa.ciphertext}; giải mã hợp lệ={rsa.decrypted}<br>
Phân tích n: {rsa.attack_factor_1} x {rsa.attack_factor_2}; d khôi phục={rsa.recovered_d}; m khôi phục={rsa.recovered_message}<br><small>{html.escape(rsa.note)}</small></div></section>

<section class="card"><h2>3. Minh họa tác động đến ECC</h2><p class="sub">Đường cong mẫu E(F17): y²=x³+2x+2; G=(5,1). Demo tìm k bằng vét cạn trên máy cổ điển.</p>
<form method="post"><label>Khóa bí mật k<input name="ecc_k" value="{ecc_k}"></label><button>Chạy demo ECDLP</button></form>
<div class="result"><b>Trạng thái:</b> <span class="status">{ecc_status}</span><br>
Bậc của G: {ecc.base_order}; khóa công khai Q=[k]G={ecc.public_q}<br>
k thực tế={ecc.private_k}; k khôi phục={ecc.recovered_k_classical}<br><small>{html.escape(ecc.note)}</small></div></section>

<section class="card"><h2>4. Tối ưu lựa chọn ML-KEM</h2><p class="sub">Bài toán biến nhị phân: chọn đúng một bộ tham số, thỏa mức an toàn và giới hạn bộ nhớ/mạng, đồng thời tối thiểu hóa hàm chi phí trọng số.</p>
<form method="post"><label>Security category tối thiểu<input name="required_category" value="{required_category}"></label><label>Public key tối đa (byte)<input name="max_pk" value="{max_pk}"></label><label>Ciphertext tối đa (byte)<input name="max_ct" value="{max_ct}"></label><label>Trọng số public key<input name="w_pk" value="{w_pk}"></label><label>Trọng số secret key<input name="w_sk" value="{w_sk}"></label><label>Trọng số ciphertext<input name="w_ct" value="{w_ct}"></label><label>Trọng số an toàn<input name="w_sec" value="{w_sec}"></label><button>Giải bài toán lựa chọn</button></form>
<div class="result"><b>Phương án tối ưu:</b> <span class="status {'warn' if not opt.feasible else ''}">{selected}</span><br><small>{html.escape(opt.mathematical_model)}</small></div>
<table><thead><tr><th>Thuật toán</th><th>Cat.</th><th>PK</th><th>CT</th><th>Điểm</th><th>Khả thi</th></tr></thead><tbody>{opt_rows}</tbody></table></section>

<section class="card wide"><h2>Phạm vi và tính trung thực của demo</h2><p>ShorLab là hệ thống minh họa giáo dục. Phần tìm chu kỳ được <b>mô phỏng cổ điển</b>, không tuyên bố chạy Shor thật trên phần cứng lượng tử. Phần RSA hoàn chỉnh từ tạo khóa đến khôi phục bản rõ. Phần ECC minh họa bài toán logarit rời rạc trên nhóm nhỏ; báo cáo phân tích vì sao Shor tổng quát giải được discrete logarithm trên nhóm cyclic khi phép toán nhóm được hiện thực lượng tử. Module Optimization áp dụng mô hình hàm mục tiêu, miền khả thi, ràng buộc và biến nhị phân từ giáo trình <i>Optimization for Communications and Networks</i>.</p></section>
</div></main><footer>{PROJECT_NAME} - Bài tập lớn {COURSE_NAME}<br>{team_display(" | ")}</footer></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/demo":
            payload = {
                "project": {"name": PROJECT_NAME, "course": COURSE_NAME, "team": team_to_dict()},
                "shor": shor_factor_emulated(15, 2).to_dict(),
                "rsa": rsa_demo(5, 11, 3, 12, 2).to_dict(),
                "ecc": ecc_demo(7).to_dict(),
                "optimization": select_mlkem().to_dict(),
            }
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
            return
        body = render_page().encode("utf-8")
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        data = parse_qs(self.rfile.read(length).decode("utf-8"))
        try:
            body_text = render_page(data)
        except Exception as exc:
            body_text = render_page(data, str(exc))
        body = body_text.encode("utf-8")
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("[ShorLab]", fmt % args)


def run_tests():
    assert shor_factor_emulated(15, 2).success
    assert set([shor_factor_emulated(15, 2).factor_1, shor_factor_emulated(15, 2).factor_2]) == {3, 5}
    assert rsa_demo(5, 11, 3, 12, 2).attack_success
    assert ecc_demo(7).success
    assert select_mlkem().selected["name"] == "ML-KEM-768"
    assert TEAM_LEADER["name"] == "Dương Công Kiên"
    assert len(team_to_dict()) == 3
    print("All ShorLab tests passed for team:", team_display())


def main():
    parser = argparse.ArgumentParser(description="ShorLab educational web demo")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    if args.test:
        run_tests(); return
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"ShorLab is running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
