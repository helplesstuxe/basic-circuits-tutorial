"""20 双控开关：9 V + 1 kΩ + 红 LED 低压版。在仓库根目录运行：python spice/20/run.py
220 V 照明回路不仿真（市电）。"""
import itertools, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ng
from ng import check

ON = 1e-3          # LED 电流 >1 mA 视为「亮」（7 mA 档的七分之一，肉眼明显可见）
res = {}
for s1, s2, s3 in itertools.product((0, 1), repeat=3):
    res[(s1, s2, s3)] = ng.run("twoway.cir", dict(S1=str(s1), S2=str(s2), S3=str(s3)))

print("== 20 双控开关（低压 LED 版）==")
lit = lambda k, s1, s2: res[(s1, s2, 0)][f"I{k}"] > ON
for s1, s2 in itertools.product((0, 1), repeat=2):
    on = lit(1, s1, s2)
    want = bool(s1 ^ s2)
    check("p2 [A] / p1 真值表", f"正确接法 S1={s1} S2={s2} 页面「{'亮' if want else '灭'}」", None,
          res[(s1, s2, 0)]["I1"] * 1e3, "mA", "SPICE：" + ("亮" if on else "灭"), v="✅" if on == want else "❌")


def flips(k):
    n = 0
    for s1, s2 in itertools.product((0, 1), repeat=2):
        n += lit(k, 1 - s1, s2) != lit(k, s1, s2)
        n += lit(k, s1, 1 - s2) != lit(k, s1, s2)
    return n


names = {1: "正确接法", 2: "跨线一端对调", 3: "公共端接错", 4: "开关接在零线"}
page = {1: (2, 8, 0), 2: (2, 8, 0), 3: (1, 4, 0), 4: (2, 8, 2)}
for k in (1, 2, 3, 4):
    nlit = sum(lit(k, a, b) for a, b in itertools.product((0, 1), repeat=2))
    live = 0
    if k == 4:   # 灯灭时 LED 阳极（灯头）对负极的电压 > 4.5 V 视为「灯头带电」
        live = sum((not lit(4, a, b)) and res[(a, b, 0)]["VJ4"] > 4.5 for a, b in itertools.product((0, 1), repeat=2))
    pl, pf, pd = page[k]
    check("p2 [C]", f"{names[k]}：亮几种", pl, nlit, "/4", v="✅" if nlit == pl else "❌")
    check("p2 [C]", f"{names[k]}：拨开关有效", pf, flips(k), "/8", v="✅" if flips(k) == pf else "❌")
    if k == 4:
        check("p2 [C]", f"{names[k]}：灯灭时灯头带电", pd, live, "/4", v="✅" if live == pd else "❌")
check("p2 例3", "跨线对调、两只都在 0：灯", None, float(lit(2, 0, 0)), "", "页面：亮", v="✅" if lit(2, 0, 0) else "❌")
on_I = res[(1, 0, 0)]["I1"] * 1e3
check("p2 §六 第2步", "LED 电流 (9−2)/1k", 7.0, on_I, "mA", f"LED 正向压降 SPICE {9 - on_I:.2f} V（页面约 2 V）")
check("p2 §六 第2步", "红 LED 压降", 2.0, res[(1, 0, 0)]["VF1"], "V")
v_neutral = res[(0, 0, 0)]["VJ4"]
check("p2 §六 第6步", "开关接零线、LED 灭：R-LED 相接点对负极（10 MΩ 表）", 9.0, v_neutral, "V")
v_ok = res[(0, 0, 0)]["VJ1"]
check("p2 §六 第6步", "正确接法、LED 灭：同一点对负极", 0.0, v_ok, "V", v="✅" if v_ok < 0.5 else "❌")
for s in itertools.product((0, 1), repeat=3):
    on = res[s]["I5"] > ON
    want = bool(s[0] ^ s[1] ^ s[2])
    check("p3 变体1 [D]", f"三地控制 S1={s[0]} 中途={s[1]} S3={s[2]} 页面「{'亮' if want else '灭'}」", None,
          res[s]["I5"] * 1e3, "mA", "SPICE：" + ("亮" if on else "灭"), v="✅" if on == want else "❌")
check("p3 练习1", "三地：依次拨 S2、S3、S2 → (0,0,1)", None, res[(0, 0, 1)]["I5"] * 1e3, "mA", "页面：亮",
      v="✅" if res[(0, 0, 1)]["I5"] > ON else "❌")
ng.save()
