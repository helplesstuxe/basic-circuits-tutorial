"""20 有源滤波：ngspice + TI LM358B 官方模型核对。在仓库根目录运行：python spice/20/run.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ng
from ng import check

db = lambda g: 20 * np.log10(g)
print("== 20 有源滤波 ==")
r = ng.run("filters_ac.cir")
check("p2 代数", "一阶截止频率 fc(带 1k 负载)", 995, r["fc1"], "Hz")
check("p1 示波器第1步", "100 Hz 输出(输入 1 V)", 0.99, r["g1_100"], "V")
check("p1 示波器第2步", "1 kHz 输出", 0.71, r["g1_1k"], "V")
check("p1 示波器第3步", "10 kHz 输出", 0.1, r["g1_10k"], "V")
check("p1 示波器第4步", "100 kHz 输出", 0.01, r["g1_100k"], "V", "", tol=15)
check("p1 示波器第5步", "接 1k 负载前后 1 kHz 读数比", 1.0, r["g1_1k"] / r["g1u_1k"], "倍")
check("p1 示波器第5步", "接 1k 负载前后 100 kHz 读数比", 1.0, r["g1_100k"] / r["g1u_100k"], "倍", "", tol=15)
check("p1 示波器第5步", "对照：无源 RC 直接带 1k，100 Hz 输出", None, r["g1n_100"], "V", "约为空载的 1/17")
check("p1 示波器第5步", "对照：无源 RC 带 1k 后的 -3 dB 频率", None, r["fc1n"], "Hz", "从 995 Hz 移到约 15 kHz，100 Hz 读数只剩约 0.06 V")
check("p2 例1", "50 Hz 幅度比", 0.999, r["g1_50"], "倍")
check("p2 代码输出", "一阶 1 kHz", 0.705, r["g1_1k"], "倍")
check("p2 代码输出", "一阶 10 kHz", 0.099, r["g1_10k"], "倍")
check("p2 代码输出", "二阶 1 kHz", 0.705, r["g2_1k"], "倍")
check("p2 代码输出", "二阶 10 kHz", 0.010, r["g2_10k"], "倍")
check("p2 §Sallen-Key", "二阶 -3 dB 频率(≈f0, Q=0.707)", 994, r["f02"], "Hz")
check("p2 §Sallen-Key", "二阶通带最大值(巴特沃斯无鼓包)", 1.0, r["g2max"], "倍")
check("p3 练习2", "一阶 3 kHz", -10, db(r["g1_3k"]), "dB", tol=5)
check("p3 练习2", "二阶 3 kHz", -19, db(r["g2_3k"]), "dB", tol=5)
check("p3 故障表", "电容接反：1 kHz", -13, db(r["g3_1k"]), "dB")
check("p3 图20-p3-2", "漏 2π：截止频率", 159, r["fc4"], "Hz")
check("p3 图20-p3-2", "漏 2π：1 kHz 处", -16, db(r["g4_1k"]), "dB")
check("p2 例3 图20-p2-3", "高通截止频率", 100, r["fc5"], "Hz")
check("p2 例3", "高通 10 Hz 幅度比", 0.1, r["g5_10"], "倍")
check("p3 练习4", "高通×2：100 Hz", 1.41, r["g6_100"], "倍")
check("p3 练习4", "高通×2：通带(2 kHz)", 2.0, r["g6_2k"], "倍")
check("p3 练习1", "R=10k C=100n 截止频率", 159, r["fc7"], "Hz")

r = ng.run("filters_tran.cir")
d = np.loadtxt(pathlib.Path(r["_dir"]) / "tran.txt"); t = d[:, 0]
k = t > 20e-3
res = d[k, 3] - d[k, 5]          # 有噪声输出 − 无噪声输出 = 剩余噪声
check("p1 图20-p1-1", "输出剩余噪声幅度", 0.03, np.ptp(res) / 2, "V")
check("p1 图20-p1-1", "50 Hz 信号输出幅度", 1.0, np.ptp(d[k, 5]) / 2, "V")
sq, ob, oc = d[:, 7], d[:, 9], d[:, 11]
k = (t > 40.5e-3) & (t < 41.5e-3)
check("p3 图20-p3-1", "二阶方波响应峰值", 1.04, oc[k].max(), "V")
check("p3 图20-p3-1", "一阶方波响应峰值(无过冲)", 1.0, ob[k].max(), "V")
ng.save()
