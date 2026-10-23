"""17 自锁：低压（12 V 继电器）版控制回路 + 24 V 导线压降。在仓库根目录运行：python spice/17/run.py
主电路（380 V 三相）、220 V 控制回路不仿真：按任务规则跳过市电部分。"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ng
from ng import check


def pwl(intervals, lo=0.0, hi=1.0, base=None):
    """[(t0, t1, level), ...] -> PWL 字符串，边沿 10 µs"""
    pts = [(0, lo)]
    for iv in intervals:
        t0, t1 = iv[0], iv[1]
        lev = iv[2] if len(iv) > 2 else hi
        pts += [(t0, lo), (t0 + 1e-5, lev), (t1, lev), (t1 + 1e-5, lo)]
    return " ".join(f"{a:.6g} {b:.6g}" for a, b in pts)


def load(r):
    d = np.loadtxt(pathlib.Path(r["_dir"]) / "sl.txt")
    t = d[:, 0]
    return t, {n: d[:, 1 + 2 * i] for i, n in enumerate(["A", "W1", "W2", "T", "coil", "hl2", "filt"])}


def at(t, y, x):
    return float(np.interp(x, t, y))


_run = ng.run


def run_sl(params):
    full = dict(SB1="0 0", SB2="0 0", SB3="0 0", SB4="0 0", FR="0 0", SUP="0 1", TSTOP="10")
    full.update(params)
    return _run("selflock.cir", full)


ON = lambda y: "吸合" if y > 0.5 else "释放"
print("== 17 自锁（低压 12 V 继电器版）==")
# ---- page2 主仿真：七个事件
p = dict(SB2=pwl([(1.0, 1.3), (4.0, 4.3), (8.0, 8.3), (9.0, 9.3)]),
         SB1=pwl([(3.0, 3.3), (9.0, 9.3)]),
         SUP=pwl([(5.0, 5.4, 0.70), (6.0, 6.5, 0.30)], lo=1.0))
r = run_sl(p)
t, y = load(r)
ton = t[np.argmax(y["A"] > 0.5)]
check("p2 代码输出 / p1 §吸合时间", "按下启动后多久吸合", 20, (ton - 1.0) * 1e3, "ms",
      "模型的 τ 就是按 20 ms 定的，所以这一行只说明模型和页面一致")
for x, want, why in [(2.0, 1, "① 松开启动后仍吸合（自锁）"), (3.5, 0, "② 按停止后释放"),
                     (4.5, 1, "③ 再按启动"),
                     (5.2, 1, "④ 电压跌到 70% 仍吸合"), (6.2, 0, "⑤ 电压跌到 30% 释放"),
                     (7.5, 0, "⑤ 来电后不会自己再启动（失压保护）"), (8.5, 1, "⑥ 重新按启动"),
                     (9.5, 0, "⑦ 启动、停止一起按：停止优先")]:
    s = at(t, y["A"], x)
    check("p2 图17-p2-2", f"t={x} s {why}", None, s, "", f"SPICE：KM {ON(s)}",
          v="✅" if (s > 0.5) == bool(want) else "❌")
# 释放时间（按停止 3.0 s 后，衔铁在滤波电压降到 0.45 时释放）
toff = t[(t > 3.0) & (y["A"] < 0.5)][0]
check("p3 参数表", "按停止到释放的时间(模型)", None, (toff - 3.0) * 1e3, "ms",
      "落在手册的 4～19 ms 范围内")
# 例 3：指示灯
check("p2 例3", "运转时(t=2 s) HL1 两端电压", 12, at(t, y["coil"], 2.0), "V")
check("p2 例3", "运转时(t=2 s) HL2 两端电压", 0, at(t, y["hl2"], 2.0), "V")
check("p2 例3", "停机时(t=3.5 s) HL2 两端电压", 12, at(t, y["hl2"], 3.5), "V")
check("p2 例3", "停机时(t=3.5 s) HL1 两端电压", 0, at(t, y["coil"], 3.5), "V")

# ---- page2 图17-p2-3：错误接法（1 s 按启动，3.5 s 按停止）
p = dict(SB2=pwl([(1.0, 1.3)]), SB1=pwl([(3.5, 3.8)]), TSTOP="5")
r = run_sl(p)
t, y = load(r)
for key, x, want, why in [("A", 4.5, 0, "正确接法：按停止后停"), ("W1", 4.5, 1, "错误①：按停止停不下来"),
                          ("W2", 2.0, 0, "错误②：停止按钮用常开，永远启动不了")]:
    s = at(t, y[key], x)
    check("p2 图17-p2-3", why, None, s, "", f"SPICE：KM {ON(s)}",
          v="✅" if (s > 0.5) == bool(want) else "❌")

# ---- p2 例1：FR 在 3.0~3.5 s 断开后自动复位
p = dict(SB2=pwl([(1.0, 1.3)]), FR=pwl([(3.0, 3.5)]), TSTOP="5")
r = run_sl(p)
t, y = load(r)
s = at(t, y["A"], 4.5)
check("p2 例1", "FR 过载断开、复位后电机不会自己重启", None, s, "", f"SPICE：KM {ON(s)}",
      v="✅" if s < 0.5 else "❌")

# ---- p3 练习1：按住停止 1~3 s，期间按启动 1.5~2.0 s
p = dict(SB1=pwl([(1.0, 3.0)]), SB2=pwl([(1.5, 2.0)]), TSTOP="4")
r = run_sl(p)
t, y = load(r)
s = max(y["A"])
check("p3 练习1", "先按住停止再按启动：全过程 KM 最大状态", None, s, "", f"SPICE：KM 从未{'吸合' if s < 0.5 else '……吸合过'}",
      v="✅" if s < 0.5 else "❌")

# ---- p3 练习2（低压版）：12 V 继电器电压跌到 82%
p = dict(SB2=pwl([(1.0, 1.3), (3.0, 3.3)]), SB1=pwl([(2.0, 2.3)]),
         SUP=pwl([(2.5, 4.0, 0.82)], lo=1.0), TSTOP="4.5")
# 1 s 满压启动 → 2 s 停 → 2.5 s 起电压 82% → 3 s 再按启动：(a) 吸不上
r = run_sl(p)
t, y = load(r)
s = at(t, y["A"], 3.8)
check("p3 练习2(a)", "电压 82% 时按启动", None, s, "", f"SPICE：KM {ON(s)}（低于 85% 吸合门限）",
      v="✅" if s < 0.5 else "❌")
p = dict(SB2=pwl([(1.0, 1.3)]), SUP=pwl([(2.0, 4.0, 0.82)], lo=1.0), TSTOP="4.5")
r = run_sl(p)
t, y = load(r)
s = at(t, y["A"], 3.8)
check("p3 练习2(b)", "运转中电压跌到 82%", None, s, "", f"SPICE：KM {ON(s)}（高于 45% 释放门限）",
      v="✅" if s > 0.5 else "❌")

# ---- p3 练习4：两地控制
p = dict(SB4=pwl([(1.0, 1.3)]), SB3=pwl([(3.0, 3.3)]), SB2=pwl([(5.0, 5.3)]), SB1=pwl([(7.0, 7.3)]),
         TSTOP="8")
r = run_sl(p)
t, y = load(r)
for x, want, why in [(2.0, 1, "乙地 SB4 启动"), (4.0, 0, "乙地 SB3 停止"), (6.0, 1, "甲地 SB2 启动"),
                     (7.8, 0, "甲地 SB1 停止")]:
    s = at(t, y["T"], x)
    check("p3 练习4 图17-p3-3", why, None, s, "", f"SPICE：KM {ON(s)}",
          v="✅" if (s > 0.5) == bool(want) else "❌")

# ---- p3 §2 导线压降（24 V）
r = ng.run("wire.cir")
rw = r["rw85"]
check("p3 §2 图17-p3-2", "24 V 控制：线圈电压降到 85% 的距离(1 mm²)", 42, rw / (2 * 0.01724 / 1.0), "m")
check("p3 练习3", "同上，1.5 mm² 导线", 63, rw / (2 * 0.01724 / 1.5), "m")
check("p3 §2", "24 V / 70 VA 等效线圈电阻(手算)", 8.2, 24 ** 2 / 70, "Ω", "核对页面的 8.2 Ω")
check("p3 §2", "220 V / 70 VA 等效线圈电阻(手算，不仿真)", 691.4, 220 ** 2 / 70, "Ω", "市电：只做算术核对")
Rw400 = 2 * 400 * 0.01724
check("p3 §2", "220 V 400 m 处线圈电压比例(手算，不仿真)", 98.0, 100 * 691.4 / (691.4 + Rw400), "%",
      "市电：只做算术核对")
ng.save()
