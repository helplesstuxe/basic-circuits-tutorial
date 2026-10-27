"""34 开关电容滤波：SPICE 核对。运行：/workspace/circuits-venv/bin/python spice/34/run.py
页面数值写在 PAGE 里，每项与 SPICE 比，偏差 ≤10% 记 ✅。"""
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ng

# 页面（page2/page4 与 code/34_sim.py）写的数值
PAGE = dict(
    f68=105.7, f136=52.9, voh=7.79, vol=0.64, vavg=4.42, vhi=5.597, vlo=3.213,
    t63_68=0.962, t95_68=2.884, t63_136=1.916, t95_136=5.741, vfin=4.5,
    vrl_68=2.298, vrl_136=1.548,
)

CASES = {
    "osc68":  ("osc.cir", dict(RT="68k", TSTOP=0.25)),
    "osc136": ("osc.cir", dict(RT="136k", TSTOP=0.5)),
    "sc68":   ("sc_step.cir", dict(RT="68k", TSTOP=7, TA=6.9)),
    "sc136":  ("sc_step.cir", dict(RT="136k", TSTOP=13, TA=12.9)),
    "sc68r470": ("sc_step.cir", dict(RT="68k", RON=470, TSTOP=4, TA=3.9)),
    "sc68r1050": ("sc_step.cir", dict(RT="68k", RON=1050, TSTOP=4, TA=3.9)),
    "rl68":   ("sc_step.cir", dict(RT="68k", RL="1Meg", TSTOP=4, TA=3.9)),
    "rl136":  ("sc_step.cir", dict(RT="136k", RL="1Meg", TSTOP=6, TA=5.9)),
}


def job(k):
    cir, p = CASES[k]
    return k, ng.run(cir, p)


if __name__ == "__main__":
    with ProcessPoolExecutor() as ex:
        R = dict(ex.map(job, CASES))
    for k, v in R.items():
        print(k, v)
    P = PAGE
    c = ng.check
    c("page2 §四 / 图2-5", "时钟频率 RT=68k", P["f68"], R["osc68"]["f"], "Hz")
    c("page2 §四 / 图2-5", "时钟频率 RT=136k（2×68k）", P["f136"], R["osc136"]["f"], "Hz")
    c("page2 §四", "时钟高电平 VOH（34_sim 取用此值）", P["voh"], R["osc68"]["vmax"], "V")
    c("page2 §四", "时钟低电平 VOL（34_sim 取用此值）", P["vol"], R["osc68"]["vmin"], "V")
    c("page2 §四", "上门限", P["vhi"], R["osc68"]["vhi"], "V")
    c("page2 §四", "下门限", P["vlo"], R["osc68"]["vlo"], "V")
    c("page4 步骤2", "万用表直流挡读时钟（平均值）", P["vavg"], R["osc68"]["vavg"], "V")
    c("page2 §三 / page4 步骤5、6", "63% 时间（104.4 Hz）", P["t63_68"], R["sc68"]["t63"], "s")
    c("page2 §三 / page4 步骤5、6", "95% 时间（104.4 Hz）", P["t95_68"], R["sc68"]["t95"], "s")
    c("page2 §三 / page4 步骤5、6", "63% 时间（52 Hz）", P["t63_136"], R["sc136"]["t63"], "s")
    c("page2 §三 / page4 步骤5、6", "95% 时间（52 Hz）", P["t95_136"], R["sc136"]["t95"], "s")
    c("page4 步骤5", "最终读数（跟随器输出）", P["vfin"], R["sc68"]["vfin"], "V")
    c("page3 §三", "63% 时间，RON = 470 Ω（5 V 典型）", P["t63_68"], R["sc68r470"]["t63"], "s")
    c("page3 §三", "63% 时间，RON = 1050 Ω（5 V 最大，最坏）", P["t63_68"], R["sc68r1050"]["t63"], "s")
    c("page2 §四", "时钟高电平比 CD4053 的 VIH（10 V 时 7 V）高", 0.79, R["osc68"]["vmax"] - 7.0, "V")
    c("page4 步骤7 / page3 §三", "接 1 MΩ 后读数（104.4 Hz）", P["vrl_68"], R["rl68"]["vfin"], "V")
    c("page4 步骤7 / page3 §三", "接 1 MΩ 后读数（52 Hz）", P["vrl_136"], R["rl136"]["vfin"], "V")
    ng.save()
