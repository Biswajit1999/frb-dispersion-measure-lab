"""Plot the CHIME catalog context and two Galactic-disk subtractions."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "data/frb20180916b-analysis.json").read_text(encoding="utf-8"))
    dm = np.sort([event["dm"] for event in data["events"]])
    observed = data["target"]["dm"]
    percentile = 100 * np.searchsorted(dm, observed, side="right") / len(dm)
    names = ["NE2001", "YMW16"]
    disk = [data["sightline"][name.lower()]["milky_way_disk"] for name in names]
    excess = [observed - value for value in disk]

    with plt.rc_context({"font.size": 10.5, "axes.spines.top": False, "axes.spines.right": False}):
        fig, (catalogue, foreground) = plt.subplots(1, 2, figsize=(9.2, 4.0), layout="constrained")
        fig.suptitle("FRB 20180916B · catalogue context and Galactic foreground", x=0.01, ha="left", fontweight="bold")
        catalogue.step(dm, np.arange(1, len(dm) + 1) / len(dm) * 100, where="post", color="#25556b")
        catalogue.scatter([observed], [percentile], color="#a7412b", s=30, zorder=3)
        catalogue.annotate(
            f"FRB 20180916B\n{percentile:.1f}% at or below",
            (observed, percentile), xytext=(12, -8), textcoords="offset points", va="top",
        )
        catalogue.set(xscale="log", ylim=(0, 104), xlabel="Total dispersion measure (pc cm⁻³)",
                      ylabel="Catalogue records at or below (%)", title=f"CHIME Catalog 1 ({len(dm)} records)")
        foreground.barh(names, disk, color="#25556b", label="Modelled Galactic disk")
        foreground.barh(names, excess, left=disk, color="#d4aa64", label="DM left after disk subtraction")
        for index, (left, residual) in enumerate(zip(disk, excess)):
            foreground.text(left / 2, index, f"{left:.1f}", ha="center", va="center", color="white")
            foreground.text(observed + 5, index, f"{residual:.1f} left", va="center", fontsize=9)
        foreground.invert_yaxis()
        foreground.set(xlim=(0, observed + 87), xlabel="Dispersion measure (pc cm⁻³)",
                       title="Same total DM, different disk models")
        foreground.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), frameon=False, fontsize=8)
        for axis in (catalogue, foreground):
            axis.grid(axis="x", alpha=0.2)
            axis.set_axisbelow(True)
        fig.savefig(root / "assets/frb-dispersion-evidence.png", dpi=115)
        plt.close(fig)


if __name__ == "__main__":
    main()
