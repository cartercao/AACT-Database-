#!/usr/bin/env python3
import os
import sys
import time
import math
import json
import re
import csv
from collections import defaultdict
from typing import Dict, List, Any, Tuple, Optional

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


API_URL = "https://clinicaltrials.gov/api/v2/studies"
DATA_DIR = os.environ.get("DATA_DIR", "/workspace/data")
MAX_PAGES_ENV = os.environ.get("MAX_PAGES")
MAX_PAGES = int(MAX_PAGES_ENV) if MAX_PAGES_ENV and MAX_PAGES_ENV.isdigit() else None


def is_antibody_intervention(name: str) -> bool:
    if not name:
        return False
    n = name.lower()
    # Heuristics for antibody therapeutics
    patterns = [
        r"\bmonoclonal\s+antibody\b",
        r"\bantibody\b",
        r"\bantibodies\b",
        r"\bantibody\s*-\s*drug\s*conjugate\b",
        r"\badc\b",
        r"\bbispecific\s+antibody\b",
        r"\btri\s*-?\s*specific\s+antibody\b",
        r"\b[a-z]+mab\b",  # generic mAb suffix
        r"\b[a-z]+-mab\b",
        r"\bmab\b",
    ]
    return any(re.search(p, n) for p in patterns)


def http_get_json(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    query = urlencode(params, doseq=True)
    req = Request(f"{url}?{query}", headers={"User-Agent": "antibody-toxicity-extractor/1.0"})
    with urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_studies(page_size: int = 100, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
    studies: List[Dict[str, Any]] = []
    cursor = None
    page = 0
    params = {
        "query.term": "antibody",
        "pageSize": page_size,
        "format": "json",
    }

    while True:
        if cursor:
            params["pageToken"] = cursor
        else:
            params.pop("pageToken", None)

        payload = http_get_json(API_URL, params)
        items = payload.get("studies", [])
        studies.extend(items)
        cursor = payload.get("nextPageToken")
        page += 1
        if max_pages is not None and page >= max_pages:
            break
        if not cursor:
            break
        # be polite
        time.sleep(0.25)
    return studies


def extract_interventions(study: Dict[str, Any]) -> List[Dict[str, Any]]:
    proto = (study.get("protocolSection") or {})
    arms_mod = (proto.get("armsInterventionsModule") or {})
    interventions = arms_mod.get("interventions") or []
    clean: List[Dict[str, Any]] = []
    for iv in interventions:
        clean.append(
            {
                "name": iv.get("name"),
                "type": iv.get("type"),
                "description": iv.get("description"),
            }
        )
    return clean


def is_antibody_trial(study: Dict[str, Any]) -> bool:
    interventions = extract_interventions(study)
    if not interventions:
        return False
    for iv in interventions:
        if is_antibody_intervention(str(iv.get("name") or "")):
            # focus on therapeutic, exclude clearly diagnostic imaging antibodies
            # If intervention type hints non-therapeutic, skip.
            iv_type = (iv.get("type") or "").lower()
            if iv_type in {"biological", "drug"}:
                return True
            # Some mAbs are still typed differently; include if name strongly matches mAb suffix
            if re.search(r"\b[a-z]+mab\b", (iv.get("name") or "").lower()):
                return True
    return False


def get_study_metadata(study: Dict[str, Any]) -> Dict[str, Any]:
    proto = (study.get("protocolSection") or {})
    ident = (proto.get("identificationModule") or {})
    status_mod = (proto.get("statusModule") or {})
    design_mod = (proto.get("designModule") or {})
    conditions_mod = (proto.get("conditionsModule") or {})
    sponsor_mod = (proto.get("sponsorCollaboratorsModule") or {})

    return {
        "nct_id": (ident.get("nctId") or study.get("nctId") or study.get("NCTId")),
        "title": ident.get("briefTitle") or study.get("briefTitle"),
        "overall_status": status_mod.get("overallStatus"),
        "study_type": design_mod.get("studyType"),
        "phases": ", ".join(design_mod.get("phases") or []),
        "conditions": ", ".join(conditions_mod.get("conditions") or []),
        "lead_sponsor": (sponsor_mod.get("leadSponsor") or {}).get("name"),
    }


def map_event_groups(study: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    # Collect event group metadata across results modules
    results = (study.get("resultsSection") or {})
    groups: Dict[str, Dict[str, Any]] = {}

    def add_groups(from_module: Dict[str, Any], key: str):
        for g in from_module.get(key) or []:
            gid = g.get("id") or g.get("eventGroupId") or g.get("groupId")
            if not gid:
                continue
            if gid not in groups:
                groups[gid] = {
                    "group_id": gid,
                    "title": g.get("title") or g.get("label") or g.get("description"),
                    "description": g.get("description"),
                }

    # Baseline groups
    base_mod = results.get("baselineCharacteristicsModule") or {}
    if base_mod:
        add_groups(base_mod, "groups")

    # Adverse events module sometimes carries event groups separately
    ae_mod = results.get("adverseEventsModule") or {}
    if ae_mod:
        for g in ae_mod.get("eventGroups") or []:
            gid = g.get("id") or g.get("eventGroupId") or g.get("groupId")
            if not gid:
                continue
            if gid not in groups:
                groups[gid] = {
                    "group_id": gid,
                    "title": g.get("title") or g.get("description"),
                    "description": g.get("description"),
                }

    # Participant flow groups
    flow_mod = results.get("participantFlowModule") or {}
    if flow_mod:
        add_groups(flow_mod, "groups")

    return groups


def extract_adverse_events(study: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Return (long_rows, summary_rows)"""
    meta = get_study_metadata(study)
    results = (study.get("resultsSection") or {})
    ae_mod = results.get("adverseEventsModule") or {}
    if not ae_mod:
        return [], []

    groups_map = map_event_groups(study)

    long_rows: List[Dict[str, Any]] = []
    # Helper to add rows from either serious or other events
    def add_events(kind_key: str):
        # In v2, seriousEvents/otherEvents are lists of event objects, each with 'term', 'organSystem', and 'stats'
        events = ae_mod.get(kind_key) or []
        if not isinstance(events, list):
            return
        for event in events:
            event_name = event.get("term") or event.get("name") or event.get("subTitle")
            category_name = event.get("organSystem") or "Unspecified"
            for stat in event.get("stats") or []:
                group_id = stat.get("eventGroupId") or stat.get("groupId")
                long_rows.append(
                    {
                        **meta,
                        "group_id": group_id,
                        "group_title": groups_map.get(group_id, {}).get("title"),
                        "ae_kind": "serious" if kind_key == "seriousEvents" else "other",
                        "category": category_name,
                        "event": event_name,
                        "num_affected": stat.get("numAffected"),
                        "num_at_risk": stat.get("numAtRisk"),
                        "percentage": stat.get("percentage"),
                    }
                )

    add_events("seriousEvents")
    add_events("otherEvents")

    # Build summarized per-group aggregates
    summary_rows: List[Dict[str, Any]] = []
    if long_rows:
        # Compute per (nct_id, group_id) stats
        max_num_at_risk: Dict[Tuple[str, Any], Optional[int]] = {}
        group_title_map: Dict[Tuple[str, Any], Optional[str]] = {}
        totals_serious: Dict[Tuple[str, Any], int] = defaultdict(int)
        totals_other: Dict[Tuple[str, Any], int] = defaultdict(int)

        for r in long_rows:
            key = (r.get("nct_id"), r.get("group_id"))
            num_at_risk = r.get("num_at_risk")
            if num_at_risk is not None:
                try:
                    num_at_risk_int = int(num_at_risk)
                except Exception:
                    num_at_risk_int = None
            else:
                num_at_risk_int = None
            if key not in max_num_at_risk:
                max_num_at_risk[key] = num_at_risk_int
            else:
                if num_at_risk_int is not None:
                    current = max_num_at_risk[key]
                    if current is None or (num_at_risk_int > current):
                        max_num_at_risk[key] = num_at_risk_int

            if key not in group_title_map or not group_title_map[key]:
                group_title_map[key] = r.get("group_title")

            try:
                affected = int(r.get("num_affected") or 0)
            except Exception:
                affected = 0
            if r.get("ae_kind") == "serious":
                totals_serious[key] += affected
            else:
                totals_other[key] += affected

        for key, size in max_num_at_risk.items():
            nct_id, group_id = key
            summary_rows.append(
                {
                    **meta,
                    "group_id": group_id,
                    "group_title": group_title_map.get(key),
                    "num_at_risk": size if size is not None else None,
                    "total_serious_ae": totals_serious.get(key, 0),
                    "total_other_ae": totals_other.get(key, 0),
                }
            )

    return long_rows, summary_rows


def build_intervention_text(study: Dict[str, Any]) -> str:
    names = []
    for iv in extract_interventions(study):
        nm = iv.get("name")
        if nm:
            names.append(nm)
    return "; ".join(sorted(set(names)))


def write_csv(path: str, rows: List[Dict[str, Any]], field_order: Optional[List[str]] = None) -> None:
    if not rows:
        # still create empty file with header if provided
        with open(path, "w", newline="", encoding="utf-8") as f:
            if field_order:
                writer = csv.DictWriter(f, fieldnames=field_order)
                writer.writeheader()
        return
    # Derive header from union of keys unless explicit
    if field_order is None:
        seen: Dict[str, None] = {}
        for r in rows:
            for k in r.keys():
                seen.setdefault(k, None)
        field_order = list(seen.keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=field_order)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k) for k in field_order})


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    print("Fetching studies from ClinicalTrials.gov v2 API...")
    studies = fetch_studies(page_size=100, max_pages=MAX_PAGES)
    print(f"Fetched {len(studies)} candidate studies with results.")

    all_long: List[Dict[str, Any]] = []
    all_summary: List[Dict[str, Any]] = []

    kept = 0
    for study in studies:
        try:
            # Some results return under key 'protocolSection'/'resultsSection'; guard accordingly
            if not is_antibody_trial(study):
                continue
            kept += 1
            long_rows, summary_rows = extract_adverse_events(study)
            if long_rows:
                # add interventions text for context
                intervention_text = build_intervention_text(study)
                for r in long_rows:
                    r["interventions"] = intervention_text
                for r in summary_rows:
                    r["interventions"] = intervention_text
                all_long.extend(long_rows)
                all_summary.extend(summary_rows)
        except Exception as exc:
            # Continue after logging the error
            sys.stderr.write(f"Error processing study: {exc}\n")

    if not all_long:
        print("No adverse event data found for antibody trials. Exiting.")
        return

    # Save CSVs
    long_path = os.path.join(DATA_DIR, "antibody_trials_adverse_events_long.csv")
    summary_path = os.path.join(DATA_DIR, "antibody_trials_adverse_events_summary.csv")
    write_csv(long_path, all_long)
    write_csv(summary_path, all_summary)
    print(f"Wrote long-form AE data to: {long_path}")
    print(f"Wrote per-arm AE summary to: {summary_path}")

    # Create a lightweight textual summary
    try:
        # Trials and arms counts
        unique_trials = {r.get("nct_id") for r in all_long}
        trial_count = len([t for t in unique_trials if t])
        unique_arms = {(r.get("nct_id"), r.get("group_id")) for r in all_summary}
        arm_count = len([a for a in unique_arms if a[0] and a[1] is not None])

        # SAE rate per arm when possible
        sae_rates: List[float] = []
        for r in all_summary:
            num_at_risk = r.get("num_at_risk")
            total_serious = r.get("total_serious_ae") or 0
            try:
                if num_at_risk and int(num_at_risk) > 0:
                    sae_rates.append(float(total_serious) / float(num_at_risk))
            except Exception:
                pass

        # Common AE categories
        agg_serious: Dict[str, int] = defaultdict(int)
        agg_other: Dict[str, int] = defaultdict(int)
        for r in all_long:
            category = str(r.get("category") or "Unspecified")
            try:
                affected = int(r.get("num_affected") or 0)
            except Exception:
                affected = 0
            if r.get("ae_kind") == "serious":
                agg_serious[category] += affected
            else:
                agg_other[category] += affected

        top_serious = sorted(agg_serious.items(), key=lambda kv: kv[1], reverse=True)[:10]
        top_other = sorted(agg_other.items(), key=lambda kv: kv[1], reverse=True)[:10]

        lines: List[str] = []
        lines.append(f"Antibody therapeutic trials with posted results: {trial_count}")
        lines.append(f"Arms/groups with AE data: {arm_count}")

        if sae_rates:
            sae_rates_sorted = sorted(sae_rates)
            n = len(sae_rates_sorted)
            median = sae_rates_sorted[n // 2] if n % 2 == 1 else (sae_rates_sorted[n // 2 - 1] + sae_rates_sorted[n // 2]) / 2.0
            q1 = sae_rates_sorted[int(0.25 * (n - 1))]
            q3 = sae_rates_sorted[int(0.75 * (n - 1))]
            lines.append(f"Serious adverse events (SAEs) per arm: median {median:.3f}, IQR {q1:.3f}-{q3:.3f}")

        def top_lines(items: List[Tuple[str, int]], label: str) -> List[str]:
            out: List[str] = []
            for cat, total in items:
                out.append(f"- {label} {cat}: {int(total)} affected across studies")
            return out

        lines.append("Top serious AE categories:")
        lines.extend(top_lines(top_serious, "Serious"))
        lines.append("Top other AE categories:")
        lines.extend(top_lines(top_other, "Other"))

        summary_txt = "\n".join(lines)
        summary_path_txt = os.path.join(DATA_DIR, "antibody_trials_toxicity_summary.txt")
        with open(summary_path_txt, "w", encoding="utf-8") as f:
            f.write(summary_txt)
        print(f"Wrote textual summary to: {summary_path_txt}")
    except Exception as exc:
        sys.stderr.write(f"Failed to compute summary: {exc}\n")


if __name__ == "__main__":
    main()

