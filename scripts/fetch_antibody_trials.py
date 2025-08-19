import requests
import pandas as pd
from typing import List, Dict, Optional

CTGOV_SEARCH_URL = "https://clinicaltrials.gov/api/v2/studies"
CTGOV_STUDY_DETAIL_URL = "https://clinicaltrials.gov/api/v2/studies/{nct_id}"


def search_antibody_trials(query_term: str = "monoclonal antibody", max_records: int = 200) -> List[Dict]:
    """Search ClinicalTrials.gov for studies matching the query term.

    Args:
        query_term: Term to search in the ClinicalTrials.gov database.
        max_records: Maximum number of study summaries to retrieve.

    Returns:
        List of study summary dictionaries returned by the search endpoint.
    """
    studies: List[Dict] = []
    params = {"query.term": query_term}
    page_token: Optional[str] = None

    while len(studies) < max_records:
        if page_token:
            params = {"pageToken": page_token}
        else:
            params = {"query.term": query_term}

        response = requests.get(CTGOV_SEARCH_URL, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        batch = data.get("studies", [])
        studies.extend(batch)

        page_token = data.get("nextPageToken")
        if not page_token or not batch:
            break  # No more pages

    return studies[:max_records]


def fetch_study_detail(nct_id: str) -> Dict:
    """Fetch full study details for a given NCT ID."""
    url = CTGOV_STUDY_DETAIL_URL.format(nct_id=nct_id)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return response.json()


def summarize_adverse_events(adverse_events_module: Dict) -> Dict:
    """Summarize serious and other adverse events for a study.

    Returns a dictionary with aggregated counts across all event categories.
    """
    serious_events = adverse_events_module.get("seriousEvents", [])
    other_events = adverse_events_module.get("otherEvents", [])

    total_serious_events = 0
    total_other_events = 0
    total_deaths = 0

    # Aggregate counts across all event categories and groups
    for event in serious_events:
        for stat in event.get("stats", []):
            total_serious_events += stat.get("numEvents", 0)

    for event in other_events:
        for stat in event.get("stats", []):
            total_other_events += stat.get("numEvents", 0)

    # Deaths may be reported separately under seriousEvents with term containing 'Death'
    for event in serious_events:
        if "death" in event.get("term", "").lower():
            for stat in event.get("stats", []):
                total_deaths += stat.get("numEvents", 0)

    return {
        "TotalSeriousAEs": total_serious_events,
        "TotalOtherAEs": total_other_events,
        "TotalDeaths": total_deaths,
    }


def build_antibody_trials_dataset(query_term: str = "monoclonal antibody", max_records: int = 200) -> pd.DataFrame:
    """Build a pandas DataFrame summarizing antibody trials and their toxicity profiles."""
    search_results = search_antibody_trials(query_term, max_records)

    records: List[Dict] = []
    for summary in search_results:
        if not summary.get("hasResults", False):
            # Skip trials without posted results (no AE data)
            continue
        nct_id = summary["protocolSection"]["identificationModule"]["nctId"]
        brief_title = summary["protocolSection"]["identificationModule"].get("briefTitle")

        # Fetch full details to get adverse events module
        detail = fetch_study_detail(nct_id)
        adverse_module = detail.get("resultsSection", {}).get("adverseEventsModule")
        if not adverse_module:
            continue  # Safety data not present

        ae_summary = summarize_adverse_events(adverse_module)

        # Extract interventions list (may include multiple arms)
        interventions = detail["protocolSection"].get("armsInterventionsModule", {}).get("interventions", [])
        intervention_names = "; ".join([i.get("name", "") for i in interventions])

        phase = detail["protocolSection"].get("designModule", {}).get("phaseList", {}).get("phase", [])
        phase_str = ", ".join(phase) if isinstance(phase, list) else phase

        record = {
            "NCTId": nct_id,
            "BriefTitle": brief_title,
            "Phase": phase_str,
            "Interventions": intervention_names,
            **ae_summary,
        }
        records.append(record)

    df = pd.DataFrame(records)
    return df


def main():
    query_term = "monoclonal antibody"
    max_records = 200  # Retrieve up to 200 trial summaries
    df = build_antibody_trials_dataset(query_term, max_records)
    output_path = "antibody_trials_toxicity.csv"
    df.to_csv(output_path, index=False)
    print(f"Dataset saved to {output_path} with {len(df)} trials containing toxicity data.")


if __name__ == "__main__":
    main()