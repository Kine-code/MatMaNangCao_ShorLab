from __future__ import annotations
import csv, json
from pathlib import Path
import matplotlib.pyplot as plt
from core import Curve, ecc_demo, point_add, rsa_demo, select_mlkem, shor_factor_emulated
from project_info import COURSE_NAME, PROJECT_NAME, TEAM_LEADER, member_label, team_display, team_to_dict

OUT = Path(__file__).with_name("output")
OUT.mkdir(exist_ok=True)

shor = shor_factor_emulated(15, 2)
rsa = rsa_demo(5, 11, 3, 12, 2)
ecc = ecc_demo(7)
opt = select_mlkem()

with (OUT / "demo_results.json").open("w", encoding="utf-8") as f:
    json.dump({"project": {"name": PROJECT_NAME, "course": COURSE_NAME, "team": team_to_dict()}, "shor": shor.to_dict(), "rsa": rsa.to_dict(), "ecc": ecc.to_dict(), "optimization": opt.to_dict()}, f, ensure_ascii=False, indent=2)

with (OUT / "shor_period.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["x", "2^x mod 15"])
    for x, value in enumerate(shor.powers): w.writerow([x, value])

plt.figure(figsize=(8, 4.3))
xs = list(range(len(shor.powers)))
plt.plot(xs, shor.powers, marker="o")
plt.xticks(xs)
plt.xlabel("x")
plt.ylabel("2^x mod 15")
plt.title("Chu kỳ của f(x) = 2^x mod 15 (r = 4)")
plt.grid(True, alpha=.3)
plt.tight_layout(); plt.savefig(OUT / "shor_period.png", dpi=180); plt.close()

plt.figure(figsize=(8, 4.8))
labels = [r["name"] for r in opt.candidates]
scores = [r["score"] for r in opt.candidates]
plt.bar(labels, scores)
plt.ylabel("Hàm chi phí chuẩn hóa (thấp hơn là tốt hơn)")
plt.title("Đánh giá ML-KEM theo mô hình tối ưu có ràng buộc")
for i, row in enumerate(opt.candidates):
    plt.text(i, scores[i] + 0.01, "Khả thi" if row["feasible"] else "Loại", ha="center", fontsize=9)
plt.tight_layout(); plt.savefig(OUT / "mlkem_optimization.png", dpi=180); plt.close()

curve = Curve(17,2,2)
points=[]
for x in range(curve.p):
    for y in range(curve.p):
        if curve.contains((x,y)): points.append((x,y))
plt.figure(figsize=(7,5.4))
plt.scatter([x for x,y in points],[y for x,y in points],s=35,label="Điểm trên E(F17)")
G=ecc.base_point; Q=ecc.public_q
plt.scatter([G[0]],[G[1]],s=110,marker="*",label=f"G={G}")
if Q: plt.scatter([Q[0]],[Q[1]],s=90,marker="s",label=f"Q=[{ecc.private_k}]G={Q}")
plt.xticks(range(17)); plt.yticks(range(17)); plt.xlabel("x"); plt.ylabel("y")
plt.title("Đường cong mẫu y² = x³ + 2x + 2 (mod 17)")
plt.grid(True,alpha=.25); plt.legend(); plt.tight_layout(); plt.savefig(OUT / "ecc_curve.png",dpi=180); plt.close()

plt.figure(figsize=(10,4.8)); plt.axis("off")
steps=[("Khóa công khai",f"(n,e)=({rsa.n},{rsa.e})"),("Mã hóa",f"m={rsa.message} → C={rsa.ciphertext}"),("Shor",f"{rsa.n}={rsa.attack_factor_1}×{rsa.attack_factor_2}"),("Khôi phục",f"d={rsa.recovered_d}"),("Giải mã",f"C^d mod n={rsa.recovered_message}")]
for i,(title,text) in enumerate(steps):
    x=0.05+i*0.19
    plt.gca().add_patch(plt.Rectangle((x,0.35),0.15,0.3,fill=False,linewidth=1.5))
    plt.text(x+0.075,0.56,title,ha="center",va="center",weight="bold")
    plt.text(x+0.075,0.43,text,ha="center",va="center")
    if i<len(steps)-1: plt.arrow(x+0.15,0.5,0.035,0,head_width=.025,head_length=.012,length_includes_head=True)
plt.title("Luồng demo tấn công RSA đầu-cuối",pad=16)
plt.tight_layout(); plt.savefig(OUT / "rsa_attack_flow.png",dpi=180,bbox_inches="tight"); plt.close()

print("Generated outputs in", OUT)

# Dashboard summary figure (based on real default calculations)
fig = plt.figure(figsize=(12, 7.2))
fig.patch.set_facecolor('#eef3f8')
fig.text(0.04, 0.93, f'{PROJECT_NAME} - Hệ thống demo {COURSE_NAME}', fontsize=22, weight='bold')
fig.text(0.04, 0.89, 'Mô phỏng Shor, tấn công RSA, minh họa ECC và tối ưu lựa chọn ML-KEM', fontsize=11)

def card(x, y, w, h, title, lines):
    ax = fig.add_axes([x, y, w, h])
    ax.set_facecolor('white')
    for spine in ax.spines.values():
        spine.set_color('#d8e1eb')
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.04, 0.86, title, transform=ax.transAxes, fontsize=14, weight='bold', color='#173f73')
    yy = 0.68
    for text, bold in lines:
        ax.text(0.05, yy, text, transform=ax.transAxes, fontsize=10.5, weight='bold' if bold else 'normal', color='#172033')
        yy -= 0.16
    return ax

card(0.04,0.52,0.44,0.30,'1. Phân tích N = 15',[(f'Cơ số a = 2, chu kỳ r = {shor.order_r}',False),(f'GCD → {shor.factor_1} và {shor.factor_2}',True),('Trạng thái: THÀNH CÔNG',True)])
card(0.52,0.52,0.44,0.30,'2. Tấn công RSA đầu-cuối',[(f'(n,e)=({rsa.n},{rsa.e}), C={rsa.ciphertext}',False),(f'd khôi phục = {rsa.recovered_d}',True),(f'm khôi phục = {rsa.recovered_message}',True)])
card(0.04,0.14,0.44,0.30,'3. Minh họa ECDLP',[(f'E(F17), G={ecc.base_point}',False),(f'Q=[{ecc.private_k}]G={ecc.public_q}',False),(f'k vét cạn = {ecc.recovered_k_classical}',True)])
card(0.52,0.14,0.44,0.30,'4. Tối ưu ML-KEM',[(f'Ràng buộc category ≥ {opt.required_category}',False),(f'PK ≤ {opt.max_public_key}, CT ≤ {opt.max_ciphertext}',False),(f'Chọn: {opt.selected["name"]}',True)])
fig.text(0.04,0.065,'Lưu ý: bước tìm chu kỳ được mô phỏng cổ điển; hậu xử lý RSA và mô hình tối ưu được thực thi đầy đủ.',fontsize=9.2,color='#607089')
fig.text(0.04,0.035,f'Nhóm trưởng: {member_label(TEAM_LEADER)} | Thành viên: Nguyễn Cảnh Huỳnh - B25CHKH071; Phạm Anh Tuấn - B25CHKH086',fontsize=8.6,color='#607089')
plt.savefig(OUT/'shorlab_dashboard.png',dpi=180,bbox_inches='tight'); plt.close(fig)

# Architecture diagram
fig = plt.figure(figsize=(11,5.8)); ax=fig.add_axes([0,0,1,1]); ax.axis('off')
boxes=[(0.05,0.68,0.18,0.18,'Người dùng','Nhập N, RSA, k ECC,\nràng buộc IoT'),
       (0.31,0.68,0.18,0.18,'Web UI','HTTP cục bộ\nkhông cần thư viện ngoài'),
       (0.57,0.68,0.18,0.18,'Khối tính toán','Số học mô-đun\nECC + tối ưu'),
       (0.79,0.68,0.16,0.18,'Kết quả','Bảng, thừa số,\nkhóa, phương án')]
for x,y,w,h,t,s in boxes:
    ax.add_patch(plt.Rectangle((x,y),w,h,fill=False,linewidth=1.6))
    ax.text(x+w/2,y+h*0.68,t,ha='center',va='center',weight='bold',fontsize=12)
    ax.text(x+w/2,y+h*0.32,s,ha='center',va='center',fontsize=9.5)
for i in range(len(boxes)-1):
    x=boxes[i][0]+boxes[i][2]; y=boxes[i][1]+boxes[i][3]/2
    x2=boxes[i+1][0]
    ax.arrow(x+0.01,y,x2-x-0.025,0,head_width=.018,head_length=.012,length_includes_head=True)
mods=[(0.12,0.25,'Shor/RSA','Tìm chu kỳ mô phỏng\nGCD và khôi phục d'),(0.37,0.25,'ECC','Cộng điểm, nhân vô hướng\nECDLP trên nhóm nhỏ'),(0.62,0.25,'Optimization','Biến nhị phân xᵢ\nHàm chi phí trọng số'),(0.82,0.25,'Xuất dữ liệu','JSON, CSV, PNG\nvà báo cáo')]
for x,y,t,s in mods:
    ax.add_patch(plt.Rectangle((x,y),0.17,0.20,fill=False,linewidth=1.4))
    ax.text(x+0.085,y+0.14,t,ha='center',weight='bold',fontsize=11)
    ax.text(x+0.085,y+0.06,s,ha='center',fontsize=9)
    ax.arrow(0.66,0.68,x+0.085-0.66,y+0.20-0.68,head_width=.012,head_length=.01,length_includes_head=True,alpha=.5)
ax.text(0.5,0.95,f'Kiến trúc hệ thống demo {PROJECT_NAME}',ha='center',fontsize=18,weight='bold')
ax.text(0.5,0.055,team_display(' | '),ha='center',fontsize=8.8,color='#607089')
plt.savefig(OUT/'system_architecture.png',dpi=180,bbox_inches='tight'); plt.close(fig)
