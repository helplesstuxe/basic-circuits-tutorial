"""全教程共用的 matplotlib 作图风格（波形、曲线、方框图）。

用法：在 code/NN_*.py 或 code/figs/NN_figs.py 开头写
    import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))  # code/ 下的脚本
    from figstyle import *
**只由总纲（协调者）修改本文件**；节点脚本需要新工具时向总纲提出，不要在节点脚本里改全局设置。
（改编自上一个教程项目的 figstyle.py：换成电路语义色，去掉音频专用工具。）

内容：
  1. 中文字体（Noto Sans CJK SC 优先）+ 缺字检查 check_cjk("文字")；rcParams 集中设置
  2. 语义颜色 C、线型 LS、尺寸 SIZE、DPI = 150；save(fig, "NN", "NN_名字.png") → NN-slug/img/（≤ 200 KB，超了自动压缩，仍超就 assert 失败）
  3. 轴标签统一写成「量 / 单位」：axlabels(ax, "时间", "ms", "电压", "V") → x 轴「时间 / ms」、y 轴「电压 / V」
  4. 参考线 ref_h / ref_v（灰色细点线），事件竖线 event_line，双向箭头 span，数值标注 mark
  5. 常用信号：sine、square、triangle、rc_step；方框图工具 diagram / box / arrow（DAG 图、框图用）
运行 `python figstyle.py --demo` 把示例图写到 /tmp/figstyle_demo.png（不进仓库）并检查缺字。
"""
import os, sys, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, cycler
from matplotlib.ft2font import FT2Font
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 仓库根目录
DPI = 150
MAX_KB = 200

# ---------------- 颜色（Okabe & Ito 色盲友好配色：https://jfly.uni-koeln.de/color/ ） ----------------
# 语义固定：同一种颜色在全书永远表示同一种东西。正文里的颜色词必须和这里一致（见 notes/AUTHOR_GUIDE.md）。
C = dict(
    vin="#0072B2",    # 蓝：输入电压 V_i（第一条曲线）
    vout="#E69F00",   # 橙：输出电压 V_o（第二条曲线）
    third="#CC79A7",  # 红紫：第三条曲线（如电容电压 V_C、电感电流、控制信号、对比方案）
    fb="#009E73",     # 蓝绿：反馈量、基准电压 V_ref、第四条曲线
    cur="#56B4E9",    # 天蓝：电流 I（单独画电流时）
    bad="#D55E00",    # 朱红：错误、故障、超限、削顶（配 × 标记）
    good="#000000",   # 黑：理想值、理论值、正确答案（配 -- 虚线）
    ref="0.6",        # 灰：参考线、门限、0 V、V_CC 边界（细点线）
    hi="#F0E442",     # 黄：只当高亮填充色
    fill="#e6f0f8", fill2="#fdf1d8", edge="#34495e",   # 方框图：方框填充 / 第二种填充 / 边框
)
# 颜色词对照（写正文时照抄）：蓝色=V_i、橙色=V_o、红紫色=第三条曲线、蓝绿色=反馈/基准、天蓝色=电流、朱红色=故障、黑色虚线=理想值、灰色点线=参考线
COLOR_WORDS = {"vin": "蓝色", "vout": "橙色", "third": "红紫色", "fb": "蓝绿色", "cur": "天蓝色",
               "bad": "朱红色", "good": "黑色虚线", "ref": "灰色点线"}
LS = dict(
    vin=dict(color=C["vin"], ls="-", lw=1.6),
    vout=dict(color=C["vout"], ls="-", lw=1.8),
    third=dict(color=C["third"], ls="-.", lw=1.6),
    fb=dict(color=C["fb"], ls="--", lw=1.4),
    cur=dict(color=C["cur"], ls="-", lw=1.4),
    bad=dict(color=C["bad"], ls="-", marker="x", markevery=0.1),
    good=dict(color=C["good"], ls="--", lw=1.2),
    ref=dict(color=C["ref"], ls=":", lw=0.9),
)
# 默认颜色循环："C0" 蓝 V_i、"C1" 橙 V_o、"C2" 红紫 第三条、"C3" 蓝绿、"C4" 天蓝、"C5" 朱红、"C6" 黑、"C7" 灰
CYCLE = [C["vin"], C["vout"], C["third"], C["fb"], C["cur"], C["bad"], "#000000", "0.5"]
SIZE = dict(single=(7, 2.8), pair=(8.8, 3.0), tall=(7, 4.6), grid=(10, 5.2), diagram=(8, 2.6))

FONT = None


def _setup():
    global FONT
    want = ["Noto Sans CJK SC", "Source Han Sans SC", "WenQuanYi Zen Hei", "Noto Sans CJK JP",
            "Microsoft YaHei", "SimHei", "PingFang SC", "Heiti SC"]
    have = {f.name for f in font_manager.fontManager.ttflist}
    for name in want:
        if name in have:
            FONT = name
            plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
            break
    else:
        print("[提示] 没找到中文字体，图中汉字可能显示成方框。Debian/Ubuntu 可安装 fonts-noto-cjk。")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "axes.unicode_minus": False,          # 负号用 ASCII，中文字体缺 U+2212
        "mathtext.fontset": "dejavusans",     # $V_o$ 这类下标用 mathtext 写
        "font.size": 11, "axes.titlesize": 11, "legend.fontsize": 9,
        "legend.frameon": True, "legend.framealpha": 0.9,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": ":",
        "axes.prop_cycle": cycler(color=CYCLE),
        "axes.formatter.useoffset": False,    # 禁止坐标轴角上的偏移记号
        "image.cmap": "viridis",
        "savefig.dpi": DPI,
    })


_setup()


def check_cjk(text="反相同相放大电压跟随器差分精密整流桥式射极稳压开关电源二极管过载保护积分微分比较器有源滤波振荡自锁互锁星三角降压启动双控继电器接触器电阻电容电感（）：，。/±×≈→①②③④Ω°"):
    """检查当前中文字体（缺字时回退 DejaVu Sans）能否显示 text 的每个字符；返回缺字列表（空 = 没有豆腐块）。"""
    path = font_manager.findfont(font_manager.FontProperties(family=FONT or "DejaVu Sans"), fallback_to_default=False)
    ft = FT2Font(path)
    fallback = FT2Font(font_manager.findfont("DejaVu Sans"))
    missing = [ch for ch in set(text) if not ch.isspace() and ft.get_char_index(ord(ch)) == 0
               and fallback.get_char_index(ord(ch)) == 0]
    if missing:
        print("[警告] 字体", FONT, "缺字：", "".join(sorted(missing)))
    return missing


# ---------------- 保存 ----------------
def node_dir(prefix):
    """prefix 如 '12' 或 '01'，返回 12-voltage-follower/img 的绝对路径；prefix='00' 返回仓库根目录 img/。"""
    if prefix in ("00", "", None):
        img = os.path.join(ROOT, "img")
    else:
        hits = glob.glob(os.path.join(ROOT, f"{prefix}-*"))
        assert len(hits) == 1, f"找不到唯一的节点目录 {prefix}-*：{hits}"
        img = os.path.join(hits[0], "img")
    os.makedirs(img, exist_ok=True)
    return img


def shrink_png(path):
    """PNG 超过 200 KB 时用 256 色调色板重新压缩（肉眼几乎无差别）；仍超就 assert 失败。返回 KB。"""
    if os.path.getsize(path) > MAX_KB * 1024:
        from PIL import Image
        Image.open(path).convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT).save(path, optimize=True)
    kb = os.path.getsize(path) / 1024
    assert kb < MAX_KB, f"{path} 有 {kb:.0f} KB，超过 {MAX_KB} KB：请缩小 figsize 或减少点数"
    return kb


def save(fig, prefix, name, tight=True):
    """保存到 NN-slug/img/name（dpi 150，≤ 200 KB），打印路径和大小。name 建议写成 'NN_pX_k_含义.png'。"""
    path = os.path.join(node_dir(prefix), name)
    if tight:
        fig.tight_layout()
    fig.savefig(path, dpi=DPI, pil_kwargs={"optimize": True})
    plt.close(fig)
    kb = shrink_png(path)
    print(f"[图] {os.path.relpath(path, ROOT)}  {kb:.0f} KB")
    return path


# ---------------- 坐标轴与标注 ----------------
def qlabel(quantity, unit=None):
    """统一轴标签格式「量 / 单位」，如 qlabel("电压", "V") → '电压 / V'；无单位时只写量。"""
    return f"{quantity} / {unit}" if unit else quantity


def axlabels(ax, xq, xu=None, yq=None, yu=None):
    """一次设好 x、y 轴标签：axlabels(ax, "时间", "ms", "电压", "V")。"""
    ax.set_xlabel(qlabel(xq, xu))
    if yq:
        ax.set_ylabel(qlabel(yq, yu))


def ref_h(ax, y, text=None, fs=9, x=1.0, ha="right"):
    """水平参考线（灰色细点线），如 0 V、V_CC、门限电压；text 写在右端上方（轴坐标 x）。"""
    ax.axhline(y, **LS["ref"], zorder=1)
    if text:
        ax.text(x, y, text, transform=ax.get_yaxis_transform(), ha=ha, va="bottom", fontsize=fs, color="0.3")


def ref_v(ax, x, text=None, fs=9, y=0.98):
    """竖直参考线 / 事件线（灰色细点线），如开关闭合时刻、t = τ；标签写在顶端。"""
    ax.axvline(x, **LS["ref"], zorder=1)
    if text:
        ax.text(x, y, text, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=fs,
                color="k", bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))


event_line = ref_v


def span(ax, x0, x1, y, text=None, color="k", fs=9, dy=0.0):
    """(x0, y) 到 (x1, y) 的双向箭头，中点上方写 text（标周期、τ、纹波等），数据坐标。"""
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<->", color=color, lw=1.1, shrinkA=0, shrinkB=0))
    if text:
        ax.text((x0 + x1) / 2, y + dy, text, ha="center", va="bottom", fontsize=fs, color="k")


def mark(ax, x, y, fmt="{:.2f}", unit="", color="k", fs=9, dx=0, dy=0, marker="o"):
    """在 (x, y) 画一个点并标出数值。**同时把数值打印到终端**（图上的每个数字都要由脚本打印出来）。"""
    s = fmt.format(y) + unit
    ax.plot([x], [y], marker=marker, color=color, ms=4, zorder=5)
    ax.annotate(s, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=fs, color=color)
    print(f"[数值] ({x:g}, {s})")
    return s


# ---------------- 常用信号 ----------------
def sine(t, f, amp=1.0, phase=0.0, offset=0.0):
    """正弦：amp·sin(2π f t + phase) + offset。t 单位 s，f 单位 Hz。"""
    return offset + amp * np.sin(2 * np.pi * f * np.asarray(t) + phase)


def square(t, f, amp=1.0, duty=0.5, offset=0.0):
    """方波：在 +amp 与 -amp 之间跳（duty 为高电平占空比）；要 0/amp 的脉冲用 offset=amp, amp=amp/2。"""
    ph = (np.asarray(t) * f) % 1.0
    return offset + np.where(ph < duty, amp, -amp)


def triangle(t, f, amp=1.0, offset=0.0):
    """三角波：峰值 ±amp。"""
    ph = (np.asarray(t) * f) % 1.0
    return offset + amp * (4 * np.abs(ph - 0.5) - 1) * -1


def rc_step(t, tau, v0=0.0, vinf=1.0):
    """RC 一阶电路的阶跃响应：v(t) = vinf + (v0 - vinf)·e^(-t/τ)（t < 0 时保持 v0）。"""
    t = np.asarray(t, dtype=float)
    return np.where(t < 0, v0, vinf + (v0 - vinf) * np.exp(-np.clip(t, 0, None) / tau))


# ---------------- 方框图工具（DAG、信号流框图；电路图请用 schem.py） ----------------
def diagram(w=8, h=2.6, xlim=None, ylim=None):
    """无坐标轴画布。默认坐标范围 0..w × 0..h。"""
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*(xlim or (0, w))); ax.set_ylim(*(ylim or (0, h)))
    ax.set_aspect("equal"); ax.axis("off"); ax.grid(False)
    return fig, ax


def box(ax, x, y, text, w=1.4, h=0.6, fc=None, ec=None, fs=10, **kw):
    """以 (x, y) 为中心的圆角方框；返回 dict（中心与左右上下接线点）。"""
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc or C["fill"], ec=ec or C["edge"], lw=1.2, **kw))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs)
    return dict(c=(x, y), l=(x - w / 2, y), r=(x + w / 2, y), t=(x, y + h / 2), b=(x, y - h / 2))


def arrow(ax, p, q, text=None, bend=0.0, dashed=False, color=None, fs=9, lw=1.2, ls=None):
    """从 p 到 q 的箭头；bend≠0 画弧线。"""
    a = FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=11, lw=lw, color=color or C["edge"],
                        connectionstyle=f"arc3,rad={bend}", linestyle=ls or ("--" if dashed else "-"),
                        shrinkA=0, shrinkB=0)
    ax.add_patch(a)
    if text:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 0.1, text, ha="center", va="bottom", fontsize=fs)
    return a


def _demo():
    t = np.linspace(0, 4e-3, 800)
    vi = sine(t, 1000, 1.0)
    fig, ax = plt.subplots(figsize=SIZE["single"])
    ax.plot(t * 1e3, vi, **LS["vin"], label="$V_i$ 输入")
    ax.plot(t * 1e3, -2 * vi, **LS["vout"], label="$V_o$ 输出（反相 ×2）")
    ax.plot(t * 1e3, rc_step(t - 1e-3, 0.5e-3), **LS["third"], label="第三条曲线 $V_C$")
    ref_h(ax, 0, "0 V"); ref_v(ax, 1.0, "t = 1 ms"); mark(ax, 0.25, 1.0, unit=" V", dy=4)
    axlabels(ax, "时间", "ms", "电压", "V"); ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    fig.tight_layout(); fig.savefig("/tmp/figstyle_demo.png", dpi=DPI); plt.close(fig)
    kb = shrink_png("/tmp/figstyle_demo.png")
    miss = check_cjk()
    print("字体:", FONT, " 缺字:", miss or "无", f" 示例图 → /tmp/figstyle_demo.png（{kb:.0f} KB）")
    assert not miss


if __name__ == "__main__" and "--demo" in sys.argv:
    _demo()
