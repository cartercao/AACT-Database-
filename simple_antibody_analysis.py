#!/usr/bin/env python3
"""
Simple Antibody Therapeutics Toxicity Analysis
A simplified version that works with basic Python libraries
"""

import csv
import json
import os
from datetime import datetime
from collections import defaultdict, Counter
import random

class SimpleAntibodyAnalyzer:
    def __init__(self):
        self.antibody_keywords = [
            'antibody', 'mab', 'monoclonal', 'immunoglobulin', 'igg', 'igm', 'iga',
            'bispecific', 'trispecific', 'adc', 'antibody-drug conjugate',
            'immunoconjugate', 'fusion protein', 'fc fusion'
        ]
        
        # Real antibody drug data
        self.antibody_drugs = {
            'Rituximab': {'target': 'CD20', 'indication': 'B-cell lymphoma', 'toxicity_profile': 'infusion_reactions'},
            'Trastuzumab': {'target': 'HER2', 'indication': 'Breast cancer', 'toxicity_profile': 'cardiotoxicity'},
            'Pembrolizumab': {'target': 'PD-1', 'indication': 'Multiple cancers', 'toxicity_profile': 'immune_related'},
            'Bevacizumab': {'target': 'VEGF', 'indication': 'Multiple cancers', 'toxicity_profile': 'vascular'},
            'Adalimumab': {'target': 'TNF-alpha', 'indication': 'Autoimmune', 'toxicity_profile': 'infection'},
            'Tocilizumab': {'target': 'IL-6', 'indication': 'Rheumatoid arthritis', 'toxicity_profile': 'infection'},
            'Cetuximab': {'target': 'EGFR', 'indication': 'Colorectal cancer', 'toxicity_profile': 'skin_toxicity'},
            'Blinatumomab': {'target': 'CD19/CD3', 'indication': 'ALL', 'toxicity_profile': 'neurotoxicity'},
            'Daratumumab': {'target': 'CD38', 'indication': 'Multiple myeloma', 'toxicity_profile': 'infusion_reactions'},
            'Ipilimumab': {'target': 'CTLA-4', 'indication': 'Melanoma', 'toxicity_profile': 'immune_related'}
        }
    
    def create_sample_data(self):
        """Create realistic sample data"""
        print("Creating sample antibody therapeutic data...")
        
        random.seed(42)
        n_trials = 500
        
        # Generate trials data
        trials_data = []
        for i in range(n_trials):
            drug = random.choice(list(self.antibody_drugs.keys()))
            drug_info = self.antibody_drugs[drug]
            
            phase = random.choice(['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4'])
            enrollment = random.randint(20, 2000) if phase in ['Phase 1', 'Phase 2'] else random.randint(100, 5000)
            
            trials_data.append({
                'nct_id': f'NCT{str(i).zfill(8)}',
                'official_title': f'Study of {drug} in {drug_info["indication"]}',
                'intervention_name': drug,
                'target': drug_info['target'],
                'indication': drug_info['indication'],
                'toxicity_profile': drug_info['toxicity_profile'],
                'phase': phase,
                'enrollment': enrollment,
                'status': random.choice(['Completed', 'Recruiting', 'Terminated', 'Suspended'])
            })
        
        self.trials_df = trials_data
        
        # Generate adverse events
        self.generate_adverse_events()
        
        # Generate toxicity profiles
        self.generate_toxicity_profiles()
        
        print(f"Created sample dataset with {len(self.trials_df)} trials")
    
    def generate_adverse_events(self):
        """Generate realistic adverse events"""
        adverse_events = []
        
        profile_events = {
            'infusion_reactions': ['Infusion reaction', 'Chills', 'Fever', 'Rash', 'Pruritus'],
            'cardiotoxicity': ['Cardiac dysfunction', 'Heart failure', 'Arrhythmia', 'Hypertension'],
            'immune_related': ['Colitis', 'Pneumonitis', 'Hepatitis', 'Thyroiditis', 'Rash'],
            'vascular': ['Hypertension', 'Thromboembolism', 'Bleeding', 'Proteinuria'],
            'infection': ['Infection', 'Pneumonia', 'Sepsis', 'Tuberculosis'],
            'skin_toxicity': ['Rash', 'Acneiform rash', 'Pruritus', 'Dry skin'],
            'neurotoxicity': ['Confusion', 'Seizure', 'Tremor', 'Headache', 'Dizziness']
        }
        
        for trial in self.trials_df:
            profile = trial['toxicity_profile']
            events = profile_events.get(profile, ['Fatigue', 'Nausea', 'Fever'])
            
            n_events = random.randint(3, 8)
            selected_events = random.sample(events, min(n_events, len(events)))
            
            for event in selected_events:
                severity = random.choice(['Mild', 'Moderate', 'Severe', 'Life-threatening'])
                frequency = random.randint(1, 100)
                
                adverse_events.append({
                    'nct_id': trial['nct_id'],
                    'adverse_event': event,
                    'severity': severity,
                    'frequency': frequency,
                    'serious': random.choice([True, False]),
                    'drug': trial['intervention_name'],
                    'target': trial['target']
                })
        
        self.adverse_events_df = adverse_events
    
    def generate_toxicity_profiles(self):
        """Generate toxicity profiles"""
        toxicity_profiles = []
        
        for trial in self.trials_df:
            profile = trial['toxicity_profile']
            
            # Generate realistic rates based on profile
            if profile == 'infusion_reactions':
                rates = {
                    'hepatotoxicity_rate': random.uniform(0.01, 0.1),
                    'cardiotoxicity_rate': random.uniform(0.01, 0.05),
                    'neurotoxicity_rate': random.uniform(0.01, 0.08),
                    'immunotoxicity_rate': random.uniform(0.05, 0.15),
                    'cytokine_release_rate': random.uniform(0.1, 0.3),
                    'infusion_reaction_rate': random.uniform(0.2, 0.6)
                }
            elif profile == 'cardiotoxicity':
                rates = {
                    'hepatotoxicity_rate': random.uniform(0.01, 0.08),
                    'cardiotoxicity_rate': random.uniform(0.1, 0.4),
                    'neurotoxicity_rate': random.uniform(0.01, 0.05),
                    'immunotoxicity_rate': random.uniform(0.02, 0.1),
                    'cytokine_release_rate': random.uniform(0.05, 0.2),
                    'infusion_reaction_rate': random.uniform(0.05, 0.25)
                }
            elif profile == 'immune_related':
                rates = {
                    'hepatotoxicity_rate': random.uniform(0.05, 0.2),
                    'cardiotoxicity_rate': random.uniform(0.01, 0.08),
                    'neurotoxicity_rate': random.uniform(0.02, 0.1),
                    'immunotoxicity_rate': random.uniform(0.1, 0.4),
                    'cytokine_release_rate': random.uniform(0.05, 0.25),
                    'infusion_reaction_rate': random.uniform(0.05, 0.2)
                }
            else:
                rates = {
                    'hepatotoxicity_rate': random.uniform(0.01, 0.15),
                    'cardiotoxicity_rate': random.uniform(0.01, 0.1),
                    'neurotoxicity_rate': random.uniform(0.01, 0.12),
                    'immunotoxicity_rate': random.uniform(0.02, 0.2),
                    'cytokine_release_rate': random.uniform(0.02, 0.18),
                    'infusion_reaction_rate': random.uniform(0.05, 0.3)
                }
            
            overall_safety = 1.0 - (sum(rates.values()) / len(rates))
            
            toxicity_profiles.append({
                'nct_id': trial['nct_id'],
                'drug': trial['intervention_name'],
                'target': trial['target'],
                'toxicity_profile': profile,
                **rates,
                'overall_safety_score': overall_safety
            })
        
        self.toxicity_df = toxicity_profiles
    
    def identify_antibody_trials(self):
        """Identify antibody trials"""
        print("Identifying antibody therapeutic trials...")
        
        antibody_trials = []
        for trial in self.trials_df:
            if any(keyword in trial['official_title'].lower() for keyword in self.antibody_keywords):
                antibody_trials.append(trial)
        
        self.antibody_trials = antibody_trials
        print(f"Identified {len(self.antibody_trials)} antibody therapeutic trials")
        return antibody_trials
    
    def analyze_toxicity_by_target(self):
        """Analyze toxicity by molecular target"""
        print("Analyzing toxicity by molecular target...")
        
        target_analysis = defaultdict(lambda: {
            'trials': 0,
            'hepatotoxicity_rates': [],
            'cardiotoxicity_rates': [],
            'neurotoxicity_rates': [],
            'immunotoxicity_rates': [],
            'cytokine_release_rates': [],
            'infusion_reaction_rates': [],
            'safety_scores': []
        })
        
        for trial in self.antibody_trials:
            target = trial['target']
            target_analysis[target]['trials'] += 1
            
            # Find corresponding toxicity data
            for toxicity in self.toxicity_df:
                if toxicity['nct_id'] == trial['nct_id']:
                    target_analysis[target]['hepatotoxicity_rates'].append(toxicity['hepatotoxicity_rate'])
                    target_analysis[target]['cardiotoxicity_rates'].append(toxicity['cardiotoxicity_rate'])
                    target_analysis[target]['neurotoxicity_rates'].append(toxicity['neurotoxicity_rate'])
                    target_analysis[target]['immunotoxicity_rates'].append(toxicity['immunotoxicity_rate'])
                    target_analysis[target]['cytokine_release_rates'].append(toxicity['cytokine_release_rate'])
                    target_analysis[target]['infusion_reaction_rates'].append(toxicity['infusion_reaction_rate'])
                    target_analysis[target]['safety_scores'].append(toxicity['overall_safety_score'])
                    break
        
        # Calculate averages
        for target in target_analysis:
            data = target_analysis[target]
            if data['trials'] > 0:
                data['avg_hepatotoxicity'] = sum(data['hepatotoxicity_rates']) / len(data['hepatotoxicity_rates'])
                data['avg_cardiotoxicity'] = sum(data['cardiotoxicity_rates']) / len(data['cardiotoxicity_rates'])
                data['avg_neurotoxicity'] = sum(data['neurotoxicity_rates']) / len(data['neurotoxicity_rates'])
                data['avg_immunotoxicity'] = sum(data['immunotoxicity_rates']) / len(data['immunotoxicity_rates'])
                data['avg_cytokine_release'] = sum(data['cytokine_release_rates']) / len(data['cytokine_release_rates'])
                data['avg_infusion_reaction'] = sum(data['infusion_reaction_rates']) / len(data['infusion_reaction_rates'])
                data['avg_safety_score'] = sum(data['safety_scores']) / len(data['safety_scores'])
        
        self.target_analysis = target_analysis
        return target_analysis
    
    def analyze_adverse_events(self):
        """Analyze adverse events"""
        print("Analyzing adverse events...")
        
        antibody_ae = [ae for ae in self.adverse_events_df 
                      if any(trial['nct_id'] == ae['nct_id'] for trial in self.antibody_trials)]
        
        # Analyze by severity
        severity_counts = Counter(ae['severity'] for ae in antibody_ae)
        
        # Analyze by event type
        event_counts = Counter(ae['adverse_event'] for ae in antibody_ae)
        
        # Analyze serious events
        serious_events = [ae for ae in antibody_ae if ae['serious']]
        serious_event_counts = Counter(ae['adverse_event'] for ae in serious_events)
        
        self.severity_analysis = severity_counts
        self.event_analysis = event_counts
        self.serious_event_analysis = serious_event_counts
        
        return severity_counts, event_counts, serious_event_counts
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("Generating comprehensive report...")
        
        report = f"""
# Antibody Therapeutics Toxicity Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
This analysis examines the toxicity profiles of antibody therapeutics based on clinical trial data, providing insights into safety patterns across different molecular targets and drug classes.

## Dataset Overview
- **Total Trials Analyzed**: {len(self.trials_df)}
- **Antibody Therapeutic Trials**: {len(self.antibody_trials)}
- **Adverse Events Recorded**: {len(self.adverse_events_df)}
- **Unique Drugs Analyzed**: {len(set(trial['intervention_name'] for trial in self.antibody_trials))}
- **Molecular Targets**: {len(set(trial['target'] for trial in self.antibody_trials))}

## Key Findings

### 1. Toxicity Profile Distribution
"""
        
        # Toxicity profile distribution
        profile_counts = Counter(trial['toxicity_profile'] for trial in self.antibody_trials)
        for profile, count in profile_counts.most_common():
            report += f"- **{profile}**: {count} trials\n"
        
        report += "\n### 2. Molecular Target Analysis\n"
        
        # Target analysis
        for target, data in self.target_analysis.items():
            if data['trials'] > 0:
                report += f"""
#### {target} Target
- **Trials**: {data['trials']}
- **Average Safety Score**: {data['avg_safety_score']:.3f}
- **Hepatotoxicity Rate**: {data['avg_hepatotoxicity']:.3f}
- **Cardiotoxicity Rate**: {data['avg_cardiotoxicity']:.3f}
- **Neurotoxicity Rate**: {data['avg_neurotoxicity']:.3f}
- **Immunotoxicity Rate**: {data['avg_immunotoxicity']:.3f}
- **Cytokine Release Rate**: {data['avg_cytokine_release']:.3f}
- **Infusion Reaction Rate**: {data['avg_infusion_reaction']:.3f}
"""
        
        # Adverse events analysis
        if hasattr(self, 'event_analysis'):
            report += "\n### 3. Adverse Events Analysis\n"
            
            report += "\n#### Most Common Adverse Events:\n"
            for event, count in self.event_analysis.most_common(10):
                report += f"- **{event}**: {count} occurrences\n"
            
            report += "\n#### Adverse Events by Severity:\n"
            for severity, count in self.severity_analysis.items():
                report += f"- **{severity}**: {count} events\n"
            
            report += "\n#### Serious Adverse Events:\n"
            for event, count in self.serious_event_analysis.most_common(10):
                report += f"- **{event}**: {count} serious events\n"
        
        report += """
## Clinical Implications

### High-Risk Toxicity Profiles
1. **Infusion Reactions**: Most common across antibody therapies
   - Premedication protocols essential
   - Monitor for early signs (fever, chills, rash)
   
2. **Cardiotoxicity**: Particularly with HER2-targeting antibodies
   - Regular cardiac monitoring required
   - Risk stratification based on cardiac history
   
3. **Immune-Related Adverse Events**: Common with checkpoint inhibitors
   - Early recognition and intervention critical
   - Multidisciplinary management approach

### Safety Monitoring Recommendations
1. **Baseline Assessment**: Comprehensive pre-treatment evaluation
2. **Regular Monitoring**: Protocol-driven safety assessments
3. **Risk Stratification**: Patient-specific risk factors
4. **Early Intervention**: Prompt management of adverse events

## Methodology
This analysis utilized clinical trial data to identify antibody therapeutic trials and analyze their toxicity profiles. The analysis included:
- Text-based identification of antibody trials
- Toxicity profile categorization
- Statistical analysis of adverse events
- Target-specific safety analysis

## Limitations
- Sample data used for demonstration
- Adverse event reporting may be incomplete
- Severity grading may vary across studies
- Real-world safety may differ from clinical trial data

## Future Directions
1. Integration with real-world evidence databases
2. Machine learning approaches for toxicity prediction
3. Biomarker identification for toxicity risk
4. Personalized safety monitoring protocols
"""
        
        # Save report
        with open('simple_antibody_report.md', 'w') as f:
            f.write(report)
        
        print("Report saved as 'simple_antibody_report.md'")
        return report
    
    def save_data_to_csv(self):
        """Save data to CSV files for further analysis"""
        print("Saving data to CSV files...")
        
        # Save trials data
        with open('antibody_trials.csv', 'w', newline='') as f:
            if self.trials_df:
                writer = csv.DictWriter(f, fieldnames=self.trials_df[0].keys())
                writer.writeheader()
                writer.writerows(self.trials_df)
        
        # Save adverse events data
        with open('adverse_events.csv', 'w', newline='') as f:
            if self.adverse_events_df:
                writer = csv.DictWriter(f, fieldnames=self.adverse_events_df[0].keys())
                writer.writeheader()
                writer.writerows(self.adverse_events_df)
        
        # Save toxicity profiles
        with open('toxicity_profiles.csv', 'w', newline='') as f:
            if self.toxicity_df:
                writer = csv.DictWriter(f, fieldnames=self.toxicity_df[0].keys())
                writer.writeheader()
                writer.writerows(self.toxicity_df)
        
        print("Data saved to CSV files:")
        print("- antibody_trials.csv")
        print("- adverse_events.csv")
        print("- toxicity_profiles.csv")

def main():
    """Main analysis function"""
    print("Starting Simple Antibody Therapeutics Toxicity Analysis...")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = SimpleAntibodyAnalyzer()
    
    # Create sample data
    analyzer.create_sample_data()
    
    # Perform analysis
    antibody_trials = analyzer.identify_antibody_trials()
    target_analysis = analyzer.analyze_toxicity_by_target()
    severity_analysis, event_analysis, serious_event_analysis = analyzer.analyze_adverse_events()
    
    # Generate report
    report = analyzer.generate_report()
    
    # Save data
    analyzer.save_data_to_csv()
    
    print("\n" + "=" * 60)
    print("Analysis completed successfully!")
    print("Files generated:")
    print("- simple_antibody_report.md (comprehensive report)")
    print("- antibody_trials.csv (trial data)")
    print("- adverse_events.csv (adverse event data)")
    print("- toxicity_profiles.csv (toxicity data)")
    print("\nKey findings:")
    print(f"- Analyzed {len(analyzer.antibody_trials)} antibody therapeutic trials")
    print(f"- Identified {len(analyzer.event_analysis)} different adverse event types")
    print(f"- Found {len(analyzer.target_analysis)} molecular targets")
    
    return analyzer

if __name__ == "__main__":
    analyzer = main()