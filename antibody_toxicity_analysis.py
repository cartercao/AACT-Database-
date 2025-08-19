#!/usr/bin/env python3
"""
Antibody Therapeutics Toxicity Analysis from ClinicalTrials.gov
This script analyzes the AACT database to extract and analyze antibody drug therapeutics
with a focus on their toxicity profiles.
"""

import pandas as pd
import numpy as np
import requests
import zipfile
import os
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

class AntibodyToxicityAnalyzer:
    def __init__(self, data_dir="aact_data"):
        self.data_dir = data_dir
        self.connection = None
        self.antibody_trials = None
        self.toxicity_data = None
        
    def download_aact_data(self):
        """Download the AACT dataset from the official source"""
        print("Downloading AACT dataset...")
        
        # AACT data URL (you may need to update this based on the latest version)
        base_url = "https://ctti-aact.nyc3.digitaloceanspaces.com/qo8zxfmtj63bc4o9qq37l0l4b11d"
        
        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Download the dataset
        try:
            response = requests.get(base_url, stream=True)
            response.raise_for_status()
            
            zip_path = os.path.join(self.data_dir, "aact_data.zip")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)
            
            print("AACT dataset downloaded and extracted successfully!")
            return True
            
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            print("Please manually download the AACT dataset from:")
            print("https://aact.ctti-clinicaltrials.org/downloads")
            return False
    
    def load_data(self):
        """Load the AACT data into pandas DataFrames"""
        print("Loading AACT data...")
        
        try:
            # Load key tables
            self.studies = pd.read_csv(os.path.join(self.data_dir, "studies.csv"))
            self.conditions = pd.read_csv(os.path.join(self.data_dir, "conditions.csv"))
            self.interventions = pd.read_csv(os.path.join(self.data_dir, "interventions.csv"))
            self.outcomes = pd.read_csv(os.path.join(self.data_dir, "outcomes.csv"))
            self.adverse_events = pd.read_csv(os.path.join(self.data_dir, "adverse_events.csv"))
            self.sponsors = pd.read_csv(os.path.join(self.data_dir, "sponsors.csv"))
            
            print("Data loaded successfully!")
            return True
            
        except FileNotFoundError:
            print("AACT data files not found. Please ensure the dataset is downloaded.")
            return False
    
    def identify_antibody_trials(self):
        """Identify trials involving antibody therapeutics"""
        print("Identifying antibody therapeutic trials...")
        
        # Keywords to identify antibody therapeutics
        antibody_keywords = [
            'antibody', 'antibodies', 'mab', 'monoclonal antibody', 'monoclonal antibodies',
            'immunoglobulin', 'igg', 'igm', 'iga', 'ige', 'igd',
            'anti-', 'anti ', 'humanized', 'chimeric', 'bispecific',
            'adc', 'antibody-drug conjugate', 'antibody drug conjugate',
            'car-t', 'cart', 'chimeric antigen receptor',
            'fusion protein', 'immunoconjugate'
        ]
        
        # Create regex pattern
        pattern = '|'.join(antibody_keywords)
        
        # Filter interventions for antibody-related terms
        antibody_interventions = self.interventions[
            self.interventions['intervention_name'].str.contains(pattern, case=False, na=False) |
            self.interventions['intervention_type'].str.contains('biological', case=False, na=False)
        ]
        
        # Get unique study IDs
        antibody_study_ids = antibody_interventions['nct_id'].unique()
        
        # Filter studies
        self.antibody_trials = self.studies[
            self.studies['nct_id'].isin(antibody_study_ids)
        ].copy()
        
        print(f"Found {len(self.antibody_trials)} antibody therapeutic trials")
        return self.antibody_trials
    
    def extract_toxicity_data(self):
        """Extract toxicity-related adverse events data"""
        print("Extracting toxicity data...")
        
        if self.antibody_trials is None:
            self.identify_antibody_trials()
        
        # Get antibody trial IDs
        antibody_nct_ids = self.antibody_trials['nct_id'].tolist()
        
        # Filter adverse events for antibody trials
        self.toxicity_data = self.adverse_events[
            self.adverse_events['nct_id'].isin(antibody_nct_ids)
        ].copy()
        
        # Add study information
        self.toxicity_data = self.toxicity_data.merge(
            self.antibody_trials[['nct_id', 'brief_title', 'official_title', 'study_type', 'phase']],
            on='nct_id',
            how='left'
        )
        
        print(f"Extracted toxicity data for {len(self.toxicity_data)} adverse events")
        return self.toxicity_data
    
    def analyze_toxicity_profiles(self):
        """Analyze toxicity profiles of antibody therapeutics"""
        print("Analyzing toxicity profiles...")
        
        if self.toxicity_data is None:
            self.extract_toxicity_data()
        
        # Create analysis results dictionary
        analysis_results = {}
        
        # 1. Overall toxicity statistics
        analysis_results['total_adverse_events'] = len(self.toxicity_data)
        analysis_results['unique_trials'] = self.toxicity_data['nct_id'].nunique()
        analysis_results['unique_events'] = self.toxicity_data['adverse_event_term'].nunique()
        
        # 2. Most common adverse events
        top_adverse_events = self.toxicity_data['adverse_event_term'].value_counts().head(20)
        analysis_results['top_adverse_events'] = top_adverse_events
        
        # 3. Toxicity by study phase
        phase_toxicity = self.toxicity_data.groupby('phase')['adverse_event_term'].count().sort_values(ascending=False)
        analysis_results['toxicity_by_phase'] = phase_toxicity
        
        # 4. Serious adverse events
        serious_events = self.toxicity_data[
            self.toxicity_data['serious'].str.contains('yes', case=False, na=False)
        ]
        analysis_results['serious_adverse_events'] = len(serious_events)
        analysis_results['top_serious_events'] = serious_events['adverse_event_term'].value_counts().head(10)
        
        # 5. Toxicity by organ system (categorize adverse events)
        organ_systems = self.categorize_by_organ_system(self.toxicity_data['adverse_event_term'])
        analysis_results['toxicity_by_organ_system'] = organ_systems
        
        # 6. Study completion rates and reasons for termination
        completion_analysis = self.analyze_study_completion()
        analysis_results['completion_analysis'] = completion_analysis
        
        return analysis_results
    
    def categorize_by_organ_system(self, adverse_events):
        """Categorize adverse events by organ system"""
        organ_categories = {
            'Hematological': ['anemia', 'thrombocytopenia', 'neutropenia', 'leukopenia', 'pancytopenia'],
            'Gastrointestinal': ['nausea', 'vomiting', 'diarrhea', 'abdominal pain', 'constipation'],
            'Hepatic': ['hepatotoxicity', 'liver', 'hepatic', 'transaminase', 'bilirubin'],
            'Cardiovascular': ['cardiac', 'heart', 'myocardial', 'arrhythmia', 'hypertension'],
            'Neurological': ['neuropathy', 'seizure', 'headache', 'dizziness', 'confusion'],
            'Respiratory': ['pneumonia', 'dyspnea', 'respiratory', 'pulmonary', 'cough'],
            'Renal': ['kidney', 'renal', 'nephrotoxicity', 'creatinine', 'proteinuria'],
            'Dermatological': ['rash', 'pruritus', 'dermatitis', 'alopecia', 'skin'],
            'Immunological': ['allergic', 'hypersensitivity', 'anaphylaxis', 'immune', 'cytokine'],
            'General': ['fatigue', 'fever', 'pain', 'edema', 'weight']
        }
        
        categorized = {}
        for category, keywords in organ_categories.items():
            pattern = '|'.join(keywords)
            count = adverse_events.str.contains(pattern, case=False, na=False).sum()
            if count > 0:
                categorized[category] = count
        
        return dict(sorted(categorized.items(), key=lambda x: x[1], reverse=True))
    
    def analyze_study_completion(self):
        """Analyze study completion rates and reasons for termination"""
        completion_stats = self.antibody_trials['overall_status'].value_counts()
        
        # Look for safety-related terminations
        safety_terminations = self.antibody_trials[
            self.antibody_trials['overall_status'].str.contains('terminated|suspended|withdrawn', case=False, na=False)
        ]
        
        return {
            'completion_stats': completion_stats,
            'safety_terminations': len(safety_terminations)
        }
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print("Generating summary report...")
        
        analysis = self.analyze_toxicity_profiles()
        
        report = f"""
# Antibody Therapeutics Toxicity Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
This report analyzes the toxicity profiles of antibody therapeutics based on clinical trial data from ClinicalTrials.gov.

## Key Findings

### Overall Statistics
- Total Antibody Therapeutic Trials: {len(self.antibody_trials)}
- Total Adverse Events: {analysis['total_adverse_events']:,}
- Unique Adverse Event Types: {analysis['unique_events']:,}
- Serious Adverse Events: {analysis['serious_adverse_events']:,}

### Most Common Adverse Events
{analysis['top_adverse_events'].head(10).to_string()}

### Toxicity by Study Phase
{analysis['toxicity_by_phase'].to_string()}

### Toxicity by Organ System
{analysis['toxicity_by_organ_system']}

### Study Completion Analysis
{analysis['completion_analysis']['completion_stats'].to_string()}

Safety-related terminations: {analysis['completion_analysis']['safety_terminations']}

### Top Serious Adverse Events
{analysis['top_serious_events'].to_string()}

## Methodology
- Data Source: AACT (Aggregate Analysis of ClinicalTrials.gov)
- Antibody Identification: Based on intervention keywords and biological classification
- Toxicity Analysis: Adverse events extraction and categorization by organ system
- Time Period: All available data in AACT database

## Limitations
- Adverse events reporting may vary across trials
- Some trials may have incomplete safety data
- Classification of antibody therapeutics based on keywords may miss some cases
"""
        
        # Save report
        with open('antibody_toxicity_report.md', 'w') as f:
            f.write(report)
        
        print("Summary report generated: antibody_toxicity_report.md")
        return report
    
    def create_visualizations(self):
        """Create visualizations for the analysis"""
        print("Creating visualizations...")
        
        analysis = self.analyze_toxicity_profiles()
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Top adverse events
        top_events = analysis['top_adverse_events'].head(10)
        axes[0, 0].barh(range(len(top_events)), top_events.values)
        axes[0, 0].set_yticks(range(len(top_events)))
        axes[0, 0].set_yticklabels(top_events.index, fontsize=8)
        axes[0, 0].set_title('Top 10 Adverse Events in Antibody Trials')
        axes[0, 0].set_xlabel('Number of Events')
        
        # 2. Toxicity by organ system
        organ_data = analysis['toxicity_by_organ_system']
        axes[0, 1].pie(organ_data.values(), labels=organ_data.keys(), autopct='%1.1f%%')
        axes[0, 1].set_title('Toxicity Distribution by Organ System')
        
        # 3. Toxicity by study phase
        phase_data = analysis['toxicity_by_phase']
        axes[1, 0].bar(phase_data.index, phase_data.values)
        axes[1, 0].set_title('Adverse Events by Study Phase')
        axes[1, 0].set_xlabel('Study Phase')
        axes[1, 0].set_ylabel('Number of Events')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Study completion status
        completion_data = analysis['completion_analysis']['completion_stats']
        axes[1, 1].bar(completion_data.index, completion_data.values)
        axes[1, 1].set_title('Study Completion Status')
        axes[1, 1].set_xlabel('Status')
        axes[1, 1].set_ylabel('Number of Studies')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('antibody_toxicity_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Visualizations saved: antibody_toxicity_analysis.png")

def main():
    """Main function to run the analysis"""
    print("Starting Antibody Therapeutics Toxicity Analysis...")
    
    # Initialize analyzer
    analyzer = AntibodyToxicityAnalyzer()
    
    # Download and load data
    if not analyzer.download_aact_data():
        print("Please manually download the AACT dataset and place it in the 'aact_data' directory")
        return
    
    if not analyzer.load_data():
        return
    
    # Run analysis
    analyzer.identify_antibody_trials()
    analyzer.extract_toxicity_data()
    
    # Generate report and visualizations
    report = analyzer.generate_summary_report()
    analyzer.create_visualizations()
    
    print("\nAnalysis complete! Check the generated files:")
    print("- antibody_toxicity_report.md (detailed report)")
    print("- antibody_toxicity_analysis.png (visualizations)")

if __name__ == "__main__":
    main()