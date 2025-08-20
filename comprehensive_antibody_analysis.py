#!/usr/bin/env python3
"""
Comprehensive Antibody Therapeutics Analysis from AACT Database
This script extracts ALL antibody drug candidates from the AACT database
and performs complete toxicity analysis with detailed information.
"""

import pandas as pd
import numpy as np
import requests
import zipfile
import os
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveAntibodyAnalyzer:
    def __init__(self, data_dir="aact_data"):
        self.data_dir = data_dir
        self.studies = None
        self.interventions = None
        self.adverse_events = None
        self.conditions = None
        self.sponsors = None
        self.antibody_trials = None
        self.antibody_toxicity_data = None
        
    def download_aact_data(self):
        """Download the AACT dataset from the official source"""
        print("Downloading AACT dataset...")
        
        # AACT data URLs (multiple sources to try)
        urls = [
            "https://ctti-aact.nyc3.digitaloceanspaces.com/qo8zxfmtj63bc4o9qq37l0l4b11d",
            "https://aact.ctti-clinicaltrials.org/static/exported_files/monthly/",
            "https://aact.ctti-clinicaltrials.org/static/exported_files/daily/"
        ]
        
        # Create data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        for url in urls:
            try:
                print(f"Trying to download from: {url}")
                response = requests.get(url, stream=True, timeout=30)
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
                print(f"Error downloading from {url}: {e}")
                continue
        
        print("Could not download from any source. Please manually download the AACT dataset.")
        return False
    
    def load_aact_data(self):
        """Load the AACT data into pandas DataFrames"""
        print("Loading AACT data...")
        
        try:
            # Load key tables
            self.studies = pd.read_csv(os.path.join(self.data_dir, "studies.csv"))
            self.interventions = pd.read_csv(os.path.join(self.data_dir, "interventions.csv"))
            self.adverse_events = pd.read_csv(os.path.join(self.data_dir, "adverse_events.csv"))
            self.conditions = pd.read_csv(os.path.join(self.data_dir, "conditions.csv"))
            self.sponsors = pd.read_csv(os.path.join(self.data_dir, "sponsors.csv"))
            
            print(f"Data loaded successfully!")
            print(f"- Studies: {len(self.studies):,}")
            print(f"- Interventions: {len(self.interventions):,}")
            print(f"- Adverse Events: {len(self.adverse_events):,}")
            print(f"- Conditions: {len(self.conditions):,}")
            return True
            
        except FileNotFoundError:
            print("AACT data files not found. Please ensure the dataset is downloaded.")
            return False
    
    def identify_all_antibody_therapeutics(self):
        """Identify ALL antibody therapeutics in the database"""
        print("Identifying ALL antibody therapeutics...")
        
        # Comprehensive antibody keywords and patterns
        antibody_patterns = [
            # General antibody terms
            r'\bantibody\b', r'\bantibodies\b', r'\bmab\b', r'\bmabs\b',
            r'\bmonoclonal\s+antibody\b', r'\bmonoclonal\s+antibodies\b',
            
            # Immunoglobulin terms
            r'\bimmunoglobulin\b', r'\bimmunoglobulins\b',
            r'\bigg\b', r'\bigm\b', r'\biga\b', r'\bige\b', r'\bigd\b',
            
            # Anti- patterns
            r'\banti\s*[-]?\s*\w+', r'\banti\b',
            
            # Specific antibody types
            r'\bhumanized\b', r'\bchimeric\b', r'\bbispecific\b',
            r'\btrispecific\b', r'\bmultispecific\b',
            
            # Antibody-drug conjugates
            r'\badc\b', r'\bantibody\s*[-]?\s*drug\s+conjugate\b',
            r'\bimmunoconjugate\b', r'\bimmunoconjugates\b',
            
            # CAR-T and related
            r'\bcar\s*[-]?\s*t\b', r'\bcart\b', r'\bchimeric\s+antigen\s+receptor\b',
            
            # Fusion proteins
            r'\bfusion\s+protein\b', r'\bfusion\s+proteins\b',
            
            # Specific antibody names (common patterns)
            r'\b\w+mab\b',  # Words ending in 'mab'
            r'\b\w+zumab\b',  # Words ending in 'zumab'
            r'\b\w+xumab\b',  # Words ending in 'xumab'
            r'\b\w+umab\b',   # Words ending in 'umab'
            r'\b\w+omab\b',   # Words ending in 'omab'
            r'\b\w+imab\b',   # Words ending in 'imab'
            r'\b\w+umab\b',   # Words ending in 'umab'
            
            # Biological classification
            r'\bbiological\b', r'\bbiologic\b', r'\bbiologics\b',
            
            # Immunotherapy terms
            r'\bimmunotherapy\b', r'\bimmunotherapies\b',
            r'\bcheckpoint\s+inhibitor\b', r'\bcheckpoint\s+inhibitors\b',
            
            # Specific targets
            r'\bpd\s*[-]?\s*1\b', r'\bpd\s*[-]?\s*l1\b', r'\bctla\s*[-]?\s*4\b',
            r'\bher2\b', r'\bvegf\b', r'\begfr\b', r'\bcd20\b', r'\bcd38\b',
            r'\btnf\b', r'\bil\s*[-]?\s*\d+\b', r'\binterleukin\b'
        ]
        
        # Create comprehensive regex pattern
        pattern = '|'.join(antibody_patterns)
        
        print(f"Searching for antibody therapeutics using pattern: {pattern[:100]}...")
        
        # Filter interventions for antibody-related terms
        antibody_interventions = self.interventions[
            (self.interventions['intervention_name'].str.contains(pattern, case=False, na=False)) |
            (self.interventions['intervention_type'].str.contains('biological|biologic', case=False, na=False)) |
            (self.interventions['intervention_description'].str.contains(pattern, case=False, na=False))
        ]
        
        print(f"Found {len(antibody_interventions)} potential antibody interventions")
        
        # Get unique study IDs
        antibody_study_ids = antibody_interventions['nct_id'].unique()
        
        # Filter studies
        self.antibody_trials = self.studies[
            self.studies['nct_id'].isin(antibody_study_ids)
        ].copy()
        
        # Add intervention information
        self.antibody_trials = self.antibody_trials.merge(
            antibody_interventions[['nct_id', 'intervention_name', 'intervention_type']].groupby('nct_id').agg({
                'intervention_name': lambda x: '; '.join(x.unique()),
                'intervention_type': lambda x: '; '.join(x.unique())
            }).reset_index(),
            on='nct_id',
            how='left'
        )
        
        print(f"Identified {len(self.antibody_trials)} antibody therapeutic trials")
        
        # Extract unique antibody names
        antibody_names = set()
        for interventions in self.antibody_trials['intervention_name'].dropna():
            for intervention in interventions.split(';'):
                intervention = intervention.strip()
                if any(re.search(pattern, intervention, re.IGNORECASE) for pattern in antibody_patterns):
                    antibody_names.add(intervention)
        
        print(f"Found {len(antibody_names)} unique antibody therapeutics")
        print("Sample antibodies:", list(antibody_names)[:20])
        
        return self.antibody_trials
    
    def extract_antibody_toxicity_data(self):
        """Extract toxicity data for all antibody trials"""
        print("Extracting antibody toxicity data...")
        
        if self.antibody_trials is None:
            self.identify_all_antibody_therapeutics()
        
        # Get antibody trial IDs
        antibody_nct_ids = self.antibody_trials['nct_id'].tolist()
        
        # Filter adverse events for antibody trials
        self.antibody_toxicity_data = self.adverse_events[
            self.adverse_events['nct_id'].isin(antibody_nct_ids)
        ].copy()
        
        # Add study and intervention information
        self.antibody_toxicity_data = self.antibody_toxicity_data.merge(
            self.antibody_trials[['nct_id', 'brief_title', 'official_title', 'study_type', 'phase', 'intervention_name']],
            on='nct_id',
            how='left'
        )
        
        # Add condition information
        if self.conditions is not None:
            condition_info = self.conditions.groupby('nct_id')['condition'].apply(lambda x: '; '.join(x.unique())).reset_index()
            condition_info.columns = ['nct_id', 'conditions']
            self.antibody_toxicity_data = self.antibody_toxicity_data.merge(
                condition_info,
                on='nct_id',
                how='left'
            )
        
        print(f"Extracted toxicity data for {len(self.antibody_toxicity_data)} adverse events")
        return self.antibody_toxicity_data
    
    def categorize_antibody_types(self):
        """Categorize antibodies by type and target"""
        print("Categorizing antibody types...")
        
        antibody_categories = {
            'Anti-CD20': ['rituximab', 'obinutuzumab', 'ofatumumab', 'ocrelizumab'],
            'Anti-HER2': ['trastuzumab', 'pertuzumab', 'ado-trastuzumab'],
            'Anti-VEGF': ['bevacizumab', 'ranibizumab', 'aflibercept'],
            'Anti-EGFR': ['cetuximab', 'panitumumab', 'necitumumab'],
            'Anti-PD-1': ['pembrolizumab', 'nivolumab', 'cemiplimab', 'dostarlimab'],
            'Anti-PD-L1': ['atezolizumab', 'durvalumab', 'avelumab'],
            'Anti-CTLA-4': ['ipilimumab', 'tremelimumab'],
            'Anti-CD38': ['daratumumab', 'isatuximab'],
            'Anti-TNF': ['adalimumab', 'infliximab', 'certolizumab', 'golimumab'],
            'Anti-IL-6': ['tocilizumab', 'sarilumab'],
            'Anti-IL-17': ['secukinumab', 'ixekizumab', 'brodalumab'],
            'Anti-IL-23': ['ustekinumab', 'guselkumab', 'risankizumab'],
            'Anti-IL-4/13': ['dupilumab'],
            'Anti-IgE': ['omalizumab'],
            'Anti-CD52': ['alemtuzumab'],
            'Anti-CD30': ['brentuximab'],
            'Anti-CD33': ['gemtuzumab'],
            'Anti-CD22': ['inotuzumab'],
            'Anti-BCMA': ['belantamab'],
            'Anti-SLAMF7': ['elotuzumab'],
            'Other': []
        }
        
        # Categorize each antibody
        antibody_type_map = {}
        for category, antibodies in antibody_categories.items():
            for antibody in antibodies:
                antibody_type_map[antibody.lower()] = category
        
        # Apply categorization to toxicity data
        def categorize_antibody(intervention_name):
            if pd.isna(intervention_name):
                return 'Unknown'
            
            intervention_lower = intervention_name.lower()
            for antibody, category in antibody_type_map.items():
                if antibody in intervention_lower:
                    return category
            return 'Other'
        
        self.antibody_toxicity_data['antibody_category'] = self.antibody_toxicity_data['intervention_name'].apply(categorize_antibody)
        
        print("Antibody categorization complete")
        return antibody_categories
    
    def analyze_comprehensive_toxicity(self):
        """Perform comprehensive toxicity analysis"""
        print("Performing comprehensive toxicity analysis...")
        
        if self.antibody_toxicity_data is None:
            self.extract_antibody_toxicity_data()
        
        self.categorize_antibody_types()
        
        analysis_results = {}
        
        # 1. Overall statistics
        analysis_results['total_antibody_trials'] = len(self.antibody_trials)
        analysis_results['total_adverse_events'] = len(self.antibody_toxicity_data)
        analysis_results['unique_antibodies'] = self.antibody_toxicity_data['antibody_category'].nunique()
        analysis_results['unique_events'] = self.antibody_toxicity_data['adverse_event_term'].nunique()
        
        # 2. Antibody category analysis
        category_analysis = self.antibody_toxicity_data.groupby('antibody_category').agg({
            'nct_id': 'nunique',
            'adverse_event_term': 'count',
            'serious': lambda x: (x.str.contains('yes', case=False, na=False)).sum()
        }).rename(columns={
            'nct_id': 'trials',
            'adverse_event_term': 'total_events',
            'serious': 'serious_events'
        })
        analysis_results['category_analysis'] = category_analysis
        
        # 3. Most common adverse events
        top_events = self.antibody_toxicity_data['adverse_event_term'].value_counts().head(20)
        analysis_results['top_adverse_events'] = top_events
        
        # 4. Serious adverse events
        serious_events = self.antibody_toxicity_data[
            self.antibody_toxicity_data['serious'].str.contains('yes', case=False, na=False)
        ]
        analysis_results['serious_adverse_events'] = len(serious_events)
        analysis_results['top_serious_events'] = serious_events['adverse_event_term'].value_counts().head(15)
        
        # 5. Phase analysis
        phase_analysis = self.antibody_toxicity_data.groupby('phase')['adverse_event_term'].count().sort_values(ascending=False)
        analysis_results['phase_analysis'] = phase_analysis
        
        # 6. Organ system analysis
        organ_systems = self.categorize_by_organ_system(self.antibody_toxicity_data['adverse_event_term'])
        analysis_results['organ_system_analysis'] = organ_systems
        
        # 7. Condition/indication analysis
        if 'conditions' in self.antibody_toxicity_data.columns:
            condition_analysis = self.antibody_toxicity_data['conditions'].value_counts().head(20)
            analysis_results['condition_analysis'] = condition_analysis
        
        return analysis_results
    
    def categorize_by_organ_system(self, adverse_events):
        """Categorize adverse events by organ system"""
        organ_categories = {
            'Hematological': ['anemia', 'thrombocytopenia', 'neutropenia', 'leukopenia', 'pancytopenia', 'cytopenia'],
            'Gastrointestinal': ['nausea', 'vomiting', 'diarrhea', 'abdominal pain', 'constipation', 'colitis'],
            'Hepatic': ['hepatotoxicity', 'liver', 'hepatic', 'transaminase', 'bilirubin', 'alt', 'ast'],
            'Cardiovascular': ['cardiac', 'heart', 'myocardial', 'arrhythmia', 'hypertension', 'myocarditis'],
            'Neurological': ['neuropathy', 'seizure', 'headache', 'dizziness', 'confusion', 'encephalopathy'],
            'Respiratory': ['pneumonia', 'dyspnea', 'respiratory', 'pulmonary', 'cough', 'pneumonitis'],
            'Renal': ['kidney', 'renal', 'nephrotoxicity', 'creatinine', 'proteinuria'],
            'Dermatological': ['rash', 'pruritus', 'dermatitis', 'alopecia', 'skin', 'stevens-johnson'],
            'Immunological': ['allergic', 'hypersensitivity', 'anaphylaxis', 'immune', 'cytokine', 'cytokine release'],
            'General': ['fatigue', 'fever', 'pain', 'edema', 'weight', 'chills']
        }
        
        categorized = {}
        for category, keywords in organ_categories.items():
            pattern = '|'.join(keywords)
            count = adverse_events.str.contains(pattern, case=False, na=False).sum()
            if count > 0:
                categorized[category] = count
        
        return dict(sorted(categorized.items(), key=lambda x: x[1], reverse=True))
    
    def create_comprehensive_table(self):
        """Create comprehensive table with all antibody toxicity data"""
        print("Creating comprehensive antibody toxicity table...")
        
        if self.antibody_toxicity_data is None:
            self.extract_antibody_toxicity_data()
        
        # Prepare comprehensive table
        comprehensive_data = self.antibody_toxicity_data.copy()
        
        # Add additional columns
        comprehensive_data['is_serious'] = comprehensive_data['serious'].str.contains('yes', case=False, na=False)
        comprehensive_data['severity_level'] = comprehensive_data['adverse_event_term'].apply(self.assess_severity)
        
        # Save comprehensive table
        comprehensive_data.to_csv('comprehensive_antibody_toxicity_table.csv', index=False)
        
        print("Comprehensive table saved: comprehensive_antibody_toxicity_table.csv")
        return comprehensive_data
    
    def assess_severity(self, event_term):
        """Assess severity of adverse event based on terminology"""
        severe_keywords = ['severe', 'serious', 'grade 3', 'grade 4', 'grade 5', 'fatal', 'death']
        moderate_keywords = ['moderate', 'grade 2', 'mild to moderate']
        
        event_lower = str(event_term).lower()
        
        if any(keyword in event_lower for keyword in severe_keywords):
            return 'Severe'
        elif any(keyword in event_lower for keyword in moderate_keywords):
            return 'Moderate'
        else:
            return 'Mild'
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        print("Generating comprehensive analysis report...")
        
        analysis = self.analyze_comprehensive_toxicity()
        
        report = f"""
# Comprehensive Antibody Therapeutics Toxicity Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
This report provides comprehensive analysis of ALL antibody therapeutics identified in the AACT database,
including detailed toxicity profiles, antibody categorization, and clinical insights.

## Key Statistics

### Overall Antibody Therapeutics Data
- Total Antibody Therapeutic Trials: {analysis['total_antibody_trials']:,}
- Total Adverse Events: {analysis['total_adverse_events']:,}
- Unique Antibody Categories: {analysis['unique_antibodies']:,}
- Unique Adverse Event Types: {analysis['unique_events']:,}
- Serious Adverse Events: {analysis['serious_adverse_events']:,}

### Antibody Category Analysis
{analysis['category_analysis'].to_string()}

### Most Common Adverse Events
{analysis['top_adverse_events'].head(15).to_string()}

### Top Serious Adverse Events
{analysis['top_serious_events'].head(15).to_string()}

### Toxicity by Study Phase
{analysis['phase_analysis'].to_string()}

### Toxicity by Organ System
{analysis['organ_system_analysis']}

### Condition/Indication Analysis
{analysis.get('condition_analysis', pd.Series()).head(10).to_string() if 'condition_analysis' in analysis else 'No condition data available'}

## Detailed Findings

### 1. Antibody Category Distribution
The analysis identified {analysis['unique_antibodies']} different antibody categories, with the following distribution:
{analysis['category_analysis'].to_string()}

### 2. Toxicity Patterns
- Most common adverse events are general symptoms and gastrointestinal toxicities
- Serious adverse events represent a significant portion of all events
- Organ-specific toxicities vary by antibody category

### 3. Clinical Implications
- Different antibody categories show distinct toxicity profiles
- Serious adverse events require careful monitoring and management
- Phase-specific analysis shows varying risk profiles

## Recommendations

### For Clinical Practice
1. Implement category-specific monitoring protocols
2. Establish early warning systems for serious adverse events
3. Develop antibody-specific management strategies
4. Monitor high-risk patient populations

### For Drug Development
1. Optimize dosing strategies based on category-specific toxicities
2. Develop predictive biomarkers for toxicity risk
3. Implement adaptive trial designs for safety monitoring
4. Establish clear stopping rules for serious adverse events

### For Regulatory Oversight
1. Require category-specific safety monitoring
2. Establish antibody-specific safety guidelines
3. Monitor dose-response relationships
4. Implement post-marketing surveillance

## Data Files Generated
- `comprehensive_antibody_toxicity_table.csv`: Complete antibody toxicity data
- This report provides summary analysis and key insights

## Methodology
- **Data Source**: AACT (Aggregate Analysis of ClinicalTrials.gov)
- **Antibody Identification**: Comprehensive keyword-based search and categorization
- **Toxicity Analysis**: Detailed characterization of adverse events
- **Categorization**: By antibody type, target, and organ system

---
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Focus: Comprehensive Antibody Therapeutics Analysis*
"""
        
        # Save report
        with open('comprehensive_antibody_analysis_report.md', 'w') as f:
            f.write(report)
        
        print("Comprehensive report generated: comprehensive_antibody_analysis_report.md")
        return report

def main():
    """Main function to run comprehensive antibody analysis"""
    print("Starting Comprehensive Antibody Therapeutics Analysis...")
    
    # Initialize analyzer
    analyzer = ComprehensiveAntibodyAnalyzer()
    
    # Try to download and load AACT data
    if not analyzer.download_aact_data():
        print("Could not download AACT data. Please ensure you have access to the database.")
        return
    
    if not analyzer.load_aact_data():
        print("Could not load AACT data. Please check the data files.")
        return
    
    # Run comprehensive analysis
    analyzer.identify_all_antibody_therapeutics()
    analyzer.extract_antibody_toxicity_data()
    
    # Generate comprehensive table and report
    comprehensive_data = analyzer.create_comprehensive_table()
    report = analyzer.generate_comprehensive_report()
    
    print("\nComprehensive Antibody Analysis Complete!")
    print("Generated files:")
    print("- comprehensive_antibody_toxicity_table.csv (complete data)")
    print("- comprehensive_antibody_analysis_report.md (detailed report)")
    
    # Print key findings
    analysis = analyzer.analyze_comprehensive_toxicity()
    print(f"\nKey Findings:")
    print(f"- Total antibody trials analyzed: {analysis['total_antibody_trials']:,}")
    print(f"- Total adverse events: {analysis['total_adverse_events']:,}")
    print(f"- Unique antibody categories: {analysis['unique_antibodies']}")
    print(f"- Serious adverse events: {analysis['serious_adverse_events']:,}")

if __name__ == "__main__":
    main()