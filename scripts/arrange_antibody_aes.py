#!/usr/bin/env python3
import os
import csv
import math
import re
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict, Counter

DATA_DIR = os.environ.get("DATA_DIR", "/workspace/data")


def read_csv(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return rows
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def write_csv(path: str, rows: List[Dict[str, Any]], header: Optional[List[str]] = None) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not rows:
        with open(path, "w", newline="", encoding="utf-8") as f:
            if header:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
        return
    if header is None:
        seen: Dict[str, None] = {}
        for r in rows:
            for k in r.keys():
                seen.setdefault(k, None)
        header = list(seen.keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k) for k in header})


def safe_int(x: Any) -> Optional[int]:
    try:
        if x is None or x == "":
            return None
        return int(float(x))
    except Exception:
        return None


def safe_float(x: Any) -> Optional[float]:
    try:
        if x is None or x == "":
            return None
        v = float(x)
        if math.isnan(v):
            return None
        return v
    except Exception:
        return None


def classify_intervention(name: Optional[str]) -> str:
    if not name:
        return "other"
    n = name.lower()
    if "antibody-drug conjugate" in n or re.search(r"\badc\b", n):
        return "adc"
    if "bispecific" in n or "bi-specific" in n:
        return "bispecific"
    if "trispecific" in n or "tri-specific" in n:
        return "trispecific"
    if re.search(r"[a-z]+mab\b", n):
        return "mab"
    if "antibody" in n or "monoclonal antibody" in n:
        return "antibody"
    return "other"


def infer_arm_intervention(group_title: str, interventions_text: str) -> Optional[str]:
    if not group_title or not interventions_text:
        return None
    lt = group_title.lower()
    candidates = [s.strip() for s in interventions_text.split(";") if s.strip()]
    best: Tuple[int, Optional[str]] = (0, None)
    for cand in candidates:
        lc = cand.lower()
        if lc in lt:
            if len(lc) > best[0]:
                best = (len(lc), cand)
    return best[1]


def enhance_per_arm(summary_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enhanced: List[Dict[str, Any]] = []
    for r in summary_rows:
        num_at_risk = safe_int(r.get("num_at_risk")) or 0
        sae = safe_int(r.get("total_serious_ae")) or 0
        oae = safe_int(r.get("total_other_ae")) or 0
        sae_rate = (sae / num_at_risk) if num_at_risk > 0 else None
        oae_rate = (oae / num_at_risk) if num_at_risk > 0 else None
        group_title = r.get("group_title") or ""
        interventions_text = r.get("interventions") or ""
        inferred = infer_arm_intervention(group_title, interventions_text)
        cls = classify_intervention(inferred)
        enhanced.append(
            {
                **r,
                "arm_label": r.get("arm_label") or group_title,
                "arm_inferred_intervention": inferred,
                "intervention_class": cls,
                "sae_rate": f"{sae_rate:.6f}" if sae_rate is not None else "",
                "other_ae_rate": f"{oae_rate:.6f}" if oae_rate is not None else "",
            }
        )
    return enhanced


def aggregate_by_intervention(per_arm: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in per_arm:
        key = r.get("arm_inferred_intervention") or "Unmapped"
        buckets[key].append(r)

    rows: List[Dict[str, Any]] = []
    for iv, items in buckets.items():
        arms_count = len(items)
        num_at_risk = sum(safe_int(x.get("num_at_risk")) or 0 for x in items)
        sae_total = sum(safe_int(x.get("total_serious_ae")) or 0 for x in items)
        oae_total = sum(safe_int(x.get("total_other_ae")) or 0 for x in items)
        sae_rates = [safe_float(x.get("sae_rate")) for x in items if safe_float(x.get("sae_rate")) is not None]
        oae_rates = [safe_float(x.get("other_ae_rate")) for x in items if safe_float(x.get("other_ae_rate")) is not None]
        def median(vals: List[float]) -> Optional[float]:
            if not vals:
                return None
            vs = sorted(vals)
            n = len(vs)
            if n % 2 == 1:
                return vs[n // 2]
            return (vs[n // 2 - 1] + vs[n // 2]) / 2.0
        def iqr(vals: List[float]) -> Tuple[Optional[float], Optional[float]]:
            if not vals:
                return None, None
            vs = sorted(vals)
            n = len(vs)
            q1 = vs[int(0.25 * (n - 1))]
            q3 = vs[int(0.75 * (n - 1))]
            return q1, q3
        sae_med = median(sae_rates)
        oae_med = median(oae_rates)
        sae_q1, sae_q3 = iqr(sae_rates)
        oae_q1, oae_q3 = iqr(oae_rates)
        cls = classify_intervention(iv if iv != "Unmapped" else None)
        rows.append(
            {
                "intervention": iv,
                "class": cls,
                "arms": arms_count,
                "total_num_at_risk": num_at_risk,
                "total_serious_ae": sae_total,
                "total_other_ae": oae_total,
                "sae_rate_median": f"{sae_med:.6f}" if sae_med is not None else "",
                "sae_rate_q1": f"{sae_q1:.6f}" if sae_q1 is not None else "",
                "sae_rate_q3": f"{sae_q3:.6f}" if sae_q3 is not None else "",
                "other_rate_median": f"{oae_med:.6f}" if oae_med is not None else "",
                "other_rate_q1": f"{oae_q1:.6f}" if oae_q1 is not None else "",
                "other_rate_q3": f"{oae_q3:.6f}" if oae_q3 is not None else "",
            }
        )
    rows.sort(key=lambda r: (-(safe_float(r.get("sae_rate_median")) or -1.0), -(safe_int(r.get("total_serious_ae")) or 0)))
    return rows


def aggregate_by_class(per_arm: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in per_arm:
        key = r.get("intervention_class") or "other"
        buckets[key].append(r)
    rows: List[Dict[str, Any]] = []
    for cls, items in buckets.items():
        arms = len(items)
        num_at_risk = sum(safe_int(x.get("num_at_risk")) or 0 for x in items)
        sae_total = sum(safe_int(x.get("total_serious_ae")) or 0 for x in items)
        oae_total = sum(safe_int(x.get("total_other_ae")) or 0 for x in items)
        sae_rates = [safe_float(x.get("sae_rate")) for x in items if safe_float(x.get("sae_rate")) is not None]
        oae_rates = [safe_float(x.get("other_ae_rate")) for x in items if safe_float(x.get("other_ae_rate")) is not None]
        def median(vals: List[float]) -> Optional[float]:
            if not vals:
                return None
            vs = sorted(vals)
            n = len(vs)
            if n % 2 == 1:
                return vs[n // 2]
            return (vs[n // 2 - 1] + vs[n // 2]) / 2.0
        def iqr(vals: List[float]) -> Tuple[Optional[float], Optional[float]]:
            if not vals:
                return None, None
            vs = sorted(vals)
            n = len(vs)
            q1 = vs[int(0.25 * (n - 1))]
            q3 = vs[int(0.75 * (n - 1))]
            return q1, q3
        sae_med = median(sae_rates)
        oae_med = median(oae_rates)
        sae_q1, sae_q3 = iqr(sae_rates)
        oae_q1, oae_q3 = iqr(oae_rates)
        rows.append(
            {
                "class": cls,
                "arms": arms,
                "total_num_at_risk": num_at_risk,
                "total_serious_ae": sae_total,
                "total_other_ae": oae_total,
                "sae_rate_median": f"{sae_med:.6f}" if sae_med is not None else "",
                "sae_rate_q1": f"{sae_q1:.6f}" if sae_q1 is not None else "",
                "sae_rate_q3": f"{sae_q3:.6f}" if sae_q3 is not None else "",
                "other_rate_median": f"{oae_med:.6f}" if oae_med is not None else "",
                "other_rate_q1": f"{oae_q1:.6f}" if oae_q1 is not None else "",
                "other_rate_q3": f"{oae_q3:.6f}" if oae_q3 is not None else "",
            }
        )
    rows.sort(key=lambda r: r.get("class"))
    return rows


def top_ae_categories_by_intervention(long_rows: List[Dict[str, Any]], per_arm_enhanced: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    # Map (nct_id, group_id) -> inferred intervention
    key_to_iv: Dict[Tuple[str, str], Optional[str]] = {}
    for r in per_arm_enhanced:
        key = (str(r.get("nct_id")), str(r.get("group_id")))
        key_to_iv[key] = r.get("arm_inferred_intervention")
    # Aggregate category counts per intervention
    agg: Dict[str, Counter] = defaultdict(Counter)
    for r in long_rows:
        key = (str(r.get("nct_id")), str(r.get("group_id")))
        iv = key_to_iv.get(key) or "Unmapped"
        cat = r.get("category") or "Unspecified"
        try:
            num = int(r.get("num_affected") or 0)
        except Exception:
            num = 0
        agg[iv][cat] += num
    # Flatten top categories per intervention
    out: List[Dict[str, Any]] = []
    for iv, counter in agg.items():
        for cat, total in counter.most_common(top_n):
            out.append({"intervention": iv, "category": cat, "affected": total})
    return out


def main() -> None:
    sum_path = os.path.join(DATA_DIR, "antibody_trials_adverse_events_summary.csv")
    long_path = os.path.join(DATA_DIR, "antibody_trials_adverse_events_long.csv")
    summary_rows = read_csv(sum_path)
    long_rows = read_csv(long_path)
    if not summary_rows:
        print("No summary CSV found; run extractor first.")
        return
    # Enhance per-arm
    per_arm = enhance_per_arm(summary_rows)
    write_csv(os.path.join(DATA_DIR, "antibody_ae_per_arm_enhanced.csv"), per_arm)
    # Aggregates
    by_iv = aggregate_by_intervention(per_arm)
    write_csv(os.path.join(DATA_DIR, "antibody_ae_by_intervention.csv"), by_iv)
    by_cls = aggregate_by_class(per_arm)
    write_csv(os.path.join(DATA_DIR, "antibody_ae_by_class.csv"), by_cls)
    # Top AE categories per intervention
    top_cats = top_ae_categories_by_intervention(long_rows, per_arm)
    write_csv(os.path.join(DATA_DIR, "antibody_ae_top_categories_by_intervention.csv"), top_cats)
    print("Wrote arranged outputs:")
    print(" - antibody_ae_per_arm_enhanced.csv")
    print(" - antibody_ae_by_intervention.csv")
    print(" - antibody_ae_by_class.csv")
    print(" - antibody_ae_top_categories_by_intervention.csv")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import os
import csv
import math
import re
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict, Counter

DATA_DIR = os.environ.get("DATA_DIR", "/workspace/data")


def read_csv(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not os.path.exists(path):
        return rows
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def write_csv(path: str, rows: List[Dict[str, Any]], header: Optional[List[str]] = None) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not rows:
        with open(path, "w", newline="", encoding="utf-8") as f:
            if header:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
        return
    if header is None:
        seen: Dict[str, None] = {}
        for r in rows:
            for k in r.keys():
                seen.setdefault(k, None)
        header = list(seen.keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k) for k in header})


def safe_int(x: Any) -> Optional[int]:
    try:
        if x is None or x == "":
            return None
        return int(float(x))
    except Exception:
        return None


def safe_float(x: Any) -> Optional[float]:
    try:
        if x is None or x == "":
            return None
        v = float(x)
        if math.isnan(v):
            return None
        return v
    except Exception:
        return None


def classify_intervention(name: Optional[str]) -> str:
    if not name:
        return "other"
    n = name.lower()
    if "antibody-drug conjugate" in n or re.search(r"\badc\b", n):
        return "adc"
    if "bispecific" in n or "bi-specific" in n:
        return "bispecific"
    if "trispecific" in n or "tri-specific" in n:
        return "trispecific"
    if re.search(r"[a-z]+mab\b", n):
        return "mab"
    if "antibody" in n or "monoclonal antibody" in n:
        return "antibody"
    return "other"


def infer_arm_intervention(group_title: str, interventions_text: str) -> Optional[str]:
    if not group_title or not interventions_text:
        return None
    lt = group_title.lower()
    candidates = [s.strip() for s in interventions_text.split(";") if s.strip()]
    best: Tuple[int, Optional[str]] = (0, None)
    for cand in candidates:
        lc = cand.lower()
        if lc in lt:
            if len(lc) > best[0]:
                best = (len(lc), cand)
    return best[1]


def enhance_per_arm(summary_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enhanced: List[Dict[str, Any]] = []
    for r in summary_rows:
        num_at_risk = safe_int(r.get("num_at_risk")) or 0
        sae = safe_int(r.get("total_serious_ae")) or 0
        oae = safe_int(r.get("total_other_ae")) or 0
        sae_rate = (sae / num_at_risk) if num_at_risk > 0 else None
        oae_rate = (oae / num_at_risk) if num_at_risk > 0 else None
        group_title = r.get("group_title") or ""
        interventions_text = r.get("interventions") or ""
        inferred = infer_arm_intervention(group_title, interventions_text)
        cls = classify_intervention(inferred)
        enhanced.append(
            {
                **r,
                "arm_label": r.get("arm_label") or group_title,
                "arm_inferred_intervention": inferred,
                "intervention_class": cls,
                "sae_rate": f"{sae_rate:.6f}" if sae_rate is not None else "",
                "other_ae_rate": f"{oae_rate:.6f}" if oae_rate is not None else "",
            }
        )
    return enhanced


def aggregate_by_intervention(per_arm: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in per_arm:
        key = r.get("arm_inferred_intervention") or "Unmapped"
        buckets[key].append(r)

    rows: List[Dict[str, Any]] = []
    for iv, items in buckets.items():
        arms_count = len(items)
        num_at_risk = sum(safe_int(x.get("num_at_risk")) or 0 for x in items)
        sae_total = sum(safe_int(x.get("total_serious_ae")) or 0 for x in items)
        oae_total = sum(safe_int(x.get("total_other_ae")) or 0 for x in items)
        sae_rates = [safe_float(x.get("sae_rate")) for x in items if safe_float(x.get("sae_rate")) is not None]
        oae_rates = [safe_float(x.get("other_ae_rate")) for x in items if safe_float(x.get("other_ae_rate")) is not None]
        def median(vals: List[float]) -> Optional[float]:
            if not vals:
                return None
            vs = sorted(vals)
            n = len(vs)
            if n % 2 == 1:
                return vs[n // 2]
            return (vs[n // 2 - 1] + vs[n // 2]) / 2.0
        def iqr(vals: List[float]) -> Tuple[Optional[float], Optional[float]]:
            if not vals:
                return None, None
            vs = sorted(vals)
            n = len(vs)
            q1 = vs[int(0.25 * (n - 1))]
            q3 = vs[int(0.75 * (n - 1))]
            return q1, q3
        sae_med = median(sae_rates)
        oae_med = median(oae_rates)
        sae_q1, sae_q3 = iqr(sae_rates)
        oae_q1, oae_q3 = iqr(oae_rates)
        cls = classify_intervention(iv if iv != "Unmapped" else None)
        rows.append(
            {
                "intervention": iv,
                "class": cls,
                "arms": arms_count,
                "total_num_at_risk": num_at_risk,
                "total_serious_ae": sae_total,
                "total_other_ae": oae_total,
                "sae_rate_median": f"{sae_med:.6f}" if sae_med is not None else "",
                "sae_rate_q1": f"{sae_q1:.6f}" if sae_q1 is not None else "",
                "sae_rate_q3": f"{sae_q3:.6f}" if sae_q3 is not None else "",
                "other_rate_median": f"{oae_med:.6f}" if oae_med is not None else "",
                "other_rate_q1": f"{oae_q1:.6f}" if oae_q1 is not None else "",
                "other_rate_q3": f"{oae_q3:.6f}" if oae_q3 is not None else "",
            }
        )
    # sort by median SAE rate desc then total SAEs
    rows.sort(key=lambda r: (-(safe_float(r.get("sae_rate_median")) or -1.0), -(safe_int(r.get("total_serious_ae")) or 0)))
    return rows


def aggregate_by_class(per_arm: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in per_arm:
        key = r.get("intervention_class") or "other"
        buckets[key].append(r)
    rows: List[Dict[str, Any]] = []
    for cls, items in buckets.items():
        arms = len(items)
        num_at_risk = sum(safe_int(x.get("num_at_risk")) or 0 for x in items)
        sae_total = sum(safe_int(x.get("total_serious_ae")) or 0 for x in items)
        oae_total = sum(safe_int(x.get("total_other_ae")) or 0 for x in items)
        sae_rates = [safe_float(x.get("sae_rate")) for x in items if safe_float(x.get("sae_rate")) is not None]
        oae_rates = [safe_float(x.get("other_ae_rate")) for x in items if safe_float(x.get("other_ae_rate")) is not None]
        def median(vals: List[float]) -> Optional[float]:
            if not vals:
                return None
            vs = sorted(vals)
            n = len(vs)
            if n % 2 == 1:
                return vs[n // 2]
            return (vs[n // 2 - 1] + vs[n // 2]) / 2.0
        def iqr(vals: List[float]) -> Tuple[Optional[float], Optional[float]]:
            if not vals:
                return None, None
            vs = sorted(vals)
            n = len(vs)
            q1 = vs[int(0.25 * (n - 1))]
            q3 = vs[int(0.75 * (n - 1))]
            return q1, q3
        sae_med = median(sae_rates)
        oae_med = median(oae_rates)
        sae_q1, sae_q3 = iqr(sae_rates)
        oae_q1, oae_q3 = iqr(oae_rates)
        rows.append(
            {
                "class": cls,
                "arms": arms,
                "total_num_at_risk": num_at_risk,
                "total_serious_ae": sae_total,
                "total_other_ae": oae_total,
                "sae_rate_median": f"{sae_med:.6f}" if sae_med is not None else "",
                "sae_rate_q1": f"{sae_q1:.6f}" if sae_q1 is not None else "",
                "sae_rate_q3": f"{sae_q3:.6f}" if sae_q3 is not None else "",
                "other_rate_median": f"{oae_med:.6f}" if oae_med is not None else "",
                "other_rate_q1": f"{oae_q1:.6f}" if oae_q1 is not None else "",
                "other_rate_q3": f"{oae_q3:.6f}" if oae_q3 is not None else "",
            }
        )
    rows.sort(key=lambda r: r.get("class"))
    return rows


def top_ae_categories_by_intervention(long_rows: List[Dict[str, Any]], per_arm_enhanced: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    # Map (nct_id, group_id) -> inferred intervention
    key_to_iv: Dict[Tuple[str, str], Optional[str]] = {}
    for r in per_arm_enhanced:
        key = (str(r.get("nct_id")), str(r.get("group_id")))
        key_to_iv[key] = r.get("arm_inferred_intervention")
    # Aggregate category counts per intervention
    agg: Dict[str, Counter] = defaultdict(Counter)
    for r in long_rows:
        key = (str(r.get("nct_id")), str(r.get("group_id")))
        iv = key_to_iv.get(key) or "Unmapped"
        cat = r.get("category") or "Unspecified"
        try:
            num = int(r.get("num_affected") or 0)
        except Exception:
            num = 0
        agg[iv][cat] += num
    # Flatten top categories per intervention
    out: List[Dict[str, Any]] = []
    for iv, counter in agg.items():
        for cat, total in counter.most_common(top_n):
            out.append({"intervention": iv, "category": cat, "affected": total})
    return out


def main() -> None:
    sum_path = os.path.join(DATA_DIR, "antibody_trials_adverse_events_summary.csv")
    long_path = os.path.join(DATA_DIR, "antibody_trials_adverse_events_long.csv")
    summary_rows = read_csv(sum_path)
    long_rows = read_csv(long_path)
    if not summary_rows:
        print("No summary CSV found; run extractor first.")
        return
    # Enhance per-arm
    per_arm = enhance_per_arm(summary_rows)
    write_csv(os.path.join(DATA_DIR, "antibody_ae_per_arm_enhanced.csv"), per_arm)
    # Aggregates
    by_iv = aggregate_by_intervention(per_arm)
    write_csv(os.path.join(DATA_DIR, "antibody_ae_by_intervention.csv"), by_iv)
    by_cls = aggregate_by_class(per_arm)
    write_csv(os.path.join(DATA_DIR, "antibody_ae_by_class.csv"), by_cls)
    # Top AE categories per intervention
    top_cats = top_ae_categories_by_intervention(long_rows, per_arm)
    write_csv(os.path.join(DATA_DIR, "antibody_ae_top_categories_by_intervention.csv"), top_cats)
    print("Wrote arranged outputs:")
    print(" - antibody_ae_per_arm_enhanced.csv")
    print(" - antibody_ae_by_intervention.csv")
    print(" - antibody_ae_by_class.csv")
    print(" - antibody_ae_top_categories_by_intervention.csv")


if __name__ == "__main__":
    main()

