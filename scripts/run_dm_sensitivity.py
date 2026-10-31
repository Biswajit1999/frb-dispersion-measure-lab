"""Reproduce sensitivity calculations from the pinned compact CHIME JSON."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.dm_sensitivity import delay_error_budget, dm_delay_covariance, residual_budget  # noqa: E402


def run(source: Path) -> dict:
    payload = json.loads(source.read_text(encoding="utf-8"))
    target = payload["target"]
    sightline = payload["sightline"]
    dm, err = target["dm"], target["dm_error"]
    bands = [(400, 800), (400, 600), (600, 800)]
    return {
        "source_sha256": payload["provenance"]["source_sha256"],
        "frequency_edge_sigma_mhz_assumed": 0.1,
        "bands": [
            {"low_mhz": lo, "high_mhz": hi,
             **delay_error_budget(dm, err, lo, hi, sigma_edge_mhz=0.1)}
            for lo, hi in bands
        ],
        "shared_dm_covariance_s2": dm_delay_covariance(err, bands),
        "foreground_assumptions": {"halo_dm": [30, 80], "mean_igm_dm_per_redshift": 900},
        "foreground_models": {
            model: residual_budget(dm, sightline[model]["milky_way_disk"],
                                   (30, 80), target["host_redshift"])
            for model in ("ne2001", "ymw16")
        },
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "data/frb20180916b-analysis.json")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = run(args.input)
    serialized = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
