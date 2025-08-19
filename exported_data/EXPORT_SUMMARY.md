
# Antibody Therapeutics Toxicity Analysis - Data Export Summary
Generated on: 2025-08-19 20:39:38

## Exported CSV Files

### 1. trials_summary.csv
- Complete trial information with toxicity profiles
- Columns: nct_id, drug, target, indication, toxicity_profile, phase, enrollment, status, all toxicity rates, safety score
- Rows: 500

### 2. target_analysis.csv
- Molecular target-specific toxicity analysis
- Columns: target, trial_count, average rates for all toxicity types, safety score
- Rows: 10

### 3. drug_analysis.csv
- Drug-specific toxicity analysis
- Columns: drug, trial_count, targets, toxicity_profiles, average rates, safety score
- Rows: 10

### 4. adverse_events_analysis.csv
- Comprehensive adverse events analysis
- Columns: adverse_event, total_count, serious_count, severity breakdown, associated drugs/targets
- Rows: 27

### 5. toxicity_profile_analysis.csv
- Toxicity profile-specific analysis
- Columns: toxicity_profile, trial_count, drugs, targets, average rates, safety score
- Rows: 7

## Key Insights

### Toxicity Profile Distribution
- immune_related: 105 trials (21.0%)
- infection: 105 trials (21.0%)
- infusion_reactions: 82 trials (16.4%)
- cardiotoxicity: 56 trials (11.2%)
- neurotoxicity: 54 trials (10.8%)
- skin_toxicity: 50 trials (10.0%)
- vascular: 48 trials (9.6%)


### Target Safety Rankings
- VEGF: 0.905 safety score
- EGFR: 0.903 safety score
- CD19/CD3: 0.903 safety score
- TNF-alpha: 0.902 safety score
- IL-6: 0.902 safety score


### Drug Safety Rankings
- Bevacizumab: 0.905 safety score
- Cetuximab: 0.903 safety score
- Blinatumomab: 0.903 safety score
- Adalimumab: 0.902 safety score
- Tocilizumab: 0.902 safety score


### Most Common Adverse Events
- Rash: 215 occurrences
- Pruritus: 122 occurrences
- Sepsis: 103 occurrences
- Pneumonia: 102 occurrences
- Pneumonitis: 101 occurrences


## Usage Instructions

1. Open CSV files in Excel, Google Sheets, or any data analysis tool
2. Use filters to explore specific drugs, targets, or toxicity profiles
3. Create custom visualizations based on your needs
4. Compare safety profiles across different dimensions

## Clinical Applications

- Drug selection based on toxicity profiles
- Risk stratification for patients
- Monitoring protocol development
- Clinical trial design
- Regulatory submissions

## Next Steps

1. Import data into statistical analysis software (R, Python, SAS)
2. Create custom visualizations for specific use cases
3. Integrate with additional data sources
4. Develop predictive models for toxicity risk
