#!/usr/bin/env python3
"""
Comprehensive Data Export and Creative Visualization
Exports all antibody toxicity analysis data to CSV and generates creative plots
"""

import csv
import json
import os
from datetime import datetime
from collections import defaultdict, Counter
import random
import math

class DataExporterAndVisualizer:
    def __init__(self):
        self.output_dir = "exported_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_analysis_data(self):
        """Load the analysis data from CSV files"""
        print("Loading analysis data...")
        
        # Load trials data
        self.trials_data = []
        with open('antibody_trials.csv', 'r') as f:
            reader = csv.DictReader(f)
            self.trials_data = list(reader)
        
        # Load adverse events data
        self.adverse_events_data = []
        with open('adverse_events.csv', 'r') as f:
            reader = csv.DictReader(f)
            self.adverse_events_data = list(reader)
        
        # Load toxicity profiles data
        self.toxicity_data = []
        with open('toxicity_profiles.csv', 'r') as f:
            reader = csv.DictReader(f)
            self.toxicity_data = list(reader)
        
        print(f"Loaded {len(self.trials_data)} trials, {len(self.adverse_events_data)} adverse events, {len(self.toxicity_data)} toxicity profiles")
    
    def export_comprehensive_csv_data(self):
        """Export all data in comprehensive CSV format"""
        print("Exporting comprehensive CSV data...")
        
        # 1. Export trials summary
        trials_summary = []
        for trial in self.trials_data:
            # Find corresponding toxicity data
            toxicity = next((t for t in self.toxicity_data if t['nct_id'] == trial['nct_id']), None)
            
            summary = {
                'nct_id': trial['nct_id'],
                'drug': trial['intervention_name'],
                'target': trial['target'],
                'indication': trial['indication'],
                'toxicity_profile': trial['toxicity_profile'],
                'phase': trial['phase'],
                'enrollment': trial['enrollment'],
                'status': trial['status'],
                'hepatotoxicity_rate': toxicity['hepatotoxicity_rate'] if toxicity else 'N/A',
                'cardiotoxicity_rate': toxicity['cardiotoxicity_rate'] if toxicity else 'N/A',
                'neurotoxicity_rate': toxicity['neurotoxicity_rate'] if toxicity else 'N/A',
                'immunotoxicity_rate': toxicity['immunotoxicity_rate'] if toxicity else 'N/A',
                'cytokine_release_rate': toxicity['cytokine_release_rate'] if toxicity else 'N/A',
                'infusion_reaction_rate': toxicity['infusion_reaction_rate'] if toxicity else 'N/A',
                'overall_safety_score': toxicity['overall_safety_score'] if toxicity else 'N/A'
            }
            trials_summary.append(summary)
        
        with open(os.path.join(self.output_dir, 'trials_summary.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=trials_summary[0].keys())
            writer.writeheader()
            writer.writerows(trials_summary)
        
        # 2. Export target analysis
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
        
        for trial in self.trials_data:
            target = trial['target']
            target_analysis[target]['trials'] += 1
            
            toxicity = next((t for t in self.toxicity_data if t['nct_id'] == trial['nct_id']), None)
            if toxicity:
                target_analysis[target]['hepatotoxicity_rates'].append(float(toxicity['hepatotoxicity_rate']))
                target_analysis[target]['cardiotoxicity_rates'].append(float(toxicity['cardiotoxicity_rate']))
                target_analysis[target]['neurotoxicity_rates'].append(float(toxicity['neurotoxicity_rate']))
                target_analysis[target]['immunotoxicity_rates'].append(float(toxicity['immunotoxicity_rate']))
                target_analysis[target]['cytokine_release_rates'].append(float(toxicity['cytokine_release_rate']))
                target_analysis[target]['infusion_reaction_rates'].append(float(toxicity['infusion_reaction_rate']))
                target_analysis[target]['safety_scores'].append(float(toxicity['overall_safety_score']))
        
        target_summary = []
        for target, data in target_analysis.items():
            if data['trials'] > 0:
                summary = {
                    'target': target,
                    'trial_count': data['trials'],
                    'avg_hepatotoxicity': sum(data['hepatotoxicity_rates']) / len(data['hepatotoxicity_rates']),
                    'avg_cardiotoxicity': sum(data['cardiotoxicity_rates']) / len(data['cardiotoxicity_rates']),
                    'avg_neurotoxicity': sum(data['neurotoxicity_rates']) / len(data['neurotoxicity_rates']),
                    'avg_immunotoxicity': sum(data['immunotoxicity_rates']) / len(data['immunotoxicity_rates']),
                    'avg_cytokine_release': sum(data['cytokine_release_rates']) / len(data['cytokine_release_rates']),
                    'avg_infusion_reaction': sum(data['infusion_reaction_rates']) / len(data['infusion_reaction_rates']),
                    'avg_safety_score': sum(data['safety_scores']) / len(data['safety_scores'])
                }
                target_summary.append(summary)
        
        with open(os.path.join(self.output_dir, 'target_analysis.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=target_summary[0].keys())
            writer.writeheader()
            writer.writerows(target_summary)
        
        # 3. Export drug analysis
        drug_analysis = defaultdict(lambda: {
            'trials': 0,
            'targets': set(),
            'toxicity_profiles': set(),
            'hepatotoxicity_rates': [],
            'cardiotoxicity_rates': [],
            'neurotoxicity_rates': [],
            'immunotoxicity_rates': [],
            'cytokine_release_rates': [],
            'infusion_reaction_rates': [],
            'safety_scores': []
        })
        
        for trial in self.trials_data:
            drug = trial['intervention_name']
            drug_analysis[drug]['trials'] += 1
            drug_analysis[drug]['targets'].add(trial['target'])
            drug_analysis[drug]['toxicity_profiles'].add(trial['toxicity_profile'])
            
            toxicity = next((t for t in self.toxicity_data if t['nct_id'] == trial['nct_id']), None)
            if toxicity:
                drug_analysis[drug]['hepatotoxicity_rates'].append(float(toxicity['hepatotoxicity_rate']))
                drug_analysis[drug]['cardiotoxicity_rates'].append(float(toxicity['cardiotoxicity_rate']))
                drug_analysis[drug]['neurotoxicity_rates'].append(float(toxicity['neurotoxicity_rate']))
                drug_analysis[drug]['immunotoxicity_rates'].append(float(toxicity['immunotoxicity_rate']))
                drug_analysis[drug]['cytokine_release_rates'].append(float(toxicity['cytokine_release_rate']))
                drug_analysis[drug]['infusion_reaction_rates'].append(float(toxicity['infusion_reaction_rate']))
                drug_analysis[drug]['safety_scores'].append(float(toxicity['overall_safety_score']))
        
        drug_summary = []
        for drug, data in drug_analysis.items():
            if data['trials'] > 0:
                summary = {
                    'drug': drug,
                    'trial_count': data['trials'],
                    'targets': ', '.join(data['targets']),
                    'toxicity_profiles': ', '.join(data['toxicity_profiles']),
                    'avg_hepatotoxicity': sum(data['hepatotoxicity_rates']) / len(data['hepatotoxicity_rates']),
                    'avg_cardiotoxicity': sum(data['cardiotoxicity_rates']) / len(data['cardiotoxicity_rates']),
                    'avg_neurotoxicity': sum(data['neurotoxicity_rates']) / len(data['neurotoxicity_rates']),
                    'avg_immunotoxicity': sum(data['immunotoxicity_rates']) / len(data['immunotoxicity_rates']),
                    'avg_cytokine_release': sum(data['cytokine_release_rates']) / len(data['cytokine_release_rates']),
                    'avg_infusion_reaction': sum(data['infusion_reaction_rates']) / len(data['infusion_reaction_rates']),
                    'avg_safety_score': sum(data['safety_scores']) / len(data['safety_scores'])
                }
                drug_summary.append(summary)
        
        with open(os.path.join(self.output_dir, 'drug_analysis.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=drug_summary[0].keys())
            writer.writeheader()
            writer.writerows(drug_summary)
        
        # 4. Export adverse events analysis
        ae_analysis = defaultdict(lambda: {
            'count': 0,
            'serious_count': 0,
            'severity_counts': defaultdict(int),
            'drugs': set(),
            'targets': set()
        })
        
        for ae in self.adverse_events_data:
            event = ae['adverse_event']
            ae_analysis[event]['count'] += 1
            if ae['serious'] == 'True':
                ae_analysis[event]['serious_count'] += 1
            ae_analysis[event]['severity_counts'][ae['severity']] += 1
            ae_analysis[event]['drugs'].add(ae['drug'])
            ae_analysis[event]['targets'].add(ae['target'])
        
        ae_summary = []
        for event, data in ae_analysis.items():
            summary = {
                'adverse_event': event,
                'total_count': data['count'],
                'serious_count': data['serious_count'],
                'serious_percentage': (data['serious_count'] / data['count']) * 100,
                'mild_count': data['severity_counts']['Mild'],
                'moderate_count': data['severity_counts']['Moderate'],
                'severe_count': data['severity_counts']['Severe'],
                'life_threatening_count': data['severity_counts']['Life-threatening'],
                'associated_drugs': ', '.join(data['drugs']),
                'associated_targets': ', '.join(data['targets'])
            }
            ae_summary.append(summary)
        
        with open(os.path.join(self.output_dir, 'adverse_events_analysis.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=ae_summary[0].keys())
            writer.writeheader()
            writer.writerows(ae_summary)
        
        # 5. Export toxicity profile analysis
        profile_analysis = defaultdict(lambda: {
            'trials': 0,
            'drugs': set(),
            'targets': set(),
            'hepatotoxicity_rates': [],
            'cardiotoxicity_rates': [],
            'neurotoxicity_rates': [],
            'immunotoxicity_rates': [],
            'cytokine_release_rates': [],
            'infusion_reaction_rates': [],
            'safety_scores': []
        })
        
        for trial in self.trials_data:
            profile = trial['toxicity_profile']
            profile_analysis[profile]['trials'] += 1
            profile_analysis[profile]['drugs'].add(trial['intervention_name'])
            profile_analysis[profile]['targets'].add(trial['target'])
            
            toxicity = next((t for t in self.toxicity_data if t['nct_id'] == trial['nct_id']), None)
            if toxicity:
                profile_analysis[profile]['hepatotoxicity_rates'].append(float(toxicity['hepatotoxicity_rate']))
                profile_analysis[profile]['cardiotoxicity_rates'].append(float(toxicity['cardiotoxicity_rate']))
                profile_analysis[profile]['neurotoxicity_rates'].append(float(toxicity['neurotoxicity_rate']))
                profile_analysis[profile]['immunotoxicity_rates'].append(float(toxicity['immunotoxicity_rate']))
                profile_analysis[profile]['cytokine_release_rates'].append(float(toxicity['cytokine_release_rate']))
                profile_analysis[profile]['infusion_reaction_rates'].append(float(toxicity['infusion_reaction_rate']))
                profile_analysis[profile]['safety_scores'].append(float(toxicity['overall_safety_score']))
        
        profile_summary = []
        for profile, data in profile_analysis.items():
            if data['trials'] > 0:
                summary = {
                    'toxicity_profile': profile,
                    'trial_count': data['trials'],
                    'drugs': ', '.join(data['drugs']),
                    'targets': ', '.join(data['targets']),
                    'avg_hepatotoxicity': sum(data['hepatotoxicity_rates']) / len(data['hepatotoxicity_rates']),
                    'avg_cardiotoxicity': sum(data['cardiotoxicity_rates']) / len(data['cardiotoxicity_rates']),
                    'avg_neurotoxicity': sum(data['neurotoxicity_rates']) / len(data['neurotoxicity_rates']),
                    'avg_immunotoxicity': sum(data['immunotoxicity_rates']) / len(data['immunotoxicity_rates']),
                    'avg_cytokine_release': sum(data['cytokine_release_rates']) / len(data['cytokine_release_rates']),
                    'avg_infusion_reaction': sum(data['infusion_reaction_rates']) / len(data['infusion_reaction_rates']),
                    'avg_safety_score': sum(data['safety_scores']) / len(data['safety_scores'])
                }
                profile_summary.append(summary)
        
        with open(os.path.join(self.output_dir, 'toxicity_profile_analysis.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=profile_summary[0].keys())
            writer.writeheader()
            writer.writerows(profile_summary)
        
        print(f"Exported comprehensive CSV data to {self.output_dir}/")
    
    def generate_creative_plots(self):
        """Generate creative ASCII art plots and visualizations"""
        print("Generating creative visualizations...")
        
        # 1. Toxicity Profile Distribution - Pie Chart
        self.create_toxicity_pie_chart()
        
        # 2. Target Safety Radar Chart
        self.create_target_radar_chart()
        
        # 3. Drug Safety Heatmap
        self.create_drug_safety_heatmap()
        
        # 4. Adverse Events Tree
        self.create_adverse_events_tree()
        
        # 5. Safety Score Distribution
        self.create_safety_score_distribution()
        
        # 6. Toxicity Risk Matrix
        self.create_toxicity_risk_matrix()
        
        # 7. Clinical Timeline
        self.create_clinical_timeline()
        
        # 8. Summary Dashboard
        self.create_summary_dashboard()
    
    def create_toxicity_pie_chart(self):
        """Create ASCII pie chart of toxicity profiles"""
        print("\n" + "="*60)
        print("TOXICITY PROFILE DISTRIBUTION")
        print("="*60)
        
        profile_counts = Counter(trial['toxicity_profile'] for trial in self.trials_data)
        total = len(self.trials_data)
        
        # Create pie chart
        chart_width = 40
        for profile, count in profile_counts.most_common():
            percentage = (count / total) * 100
            bar_length = int((percentage / 100) * chart_width)
            bar = "█" * bar_length
            print(f"{profile:20} {bar} {percentage:5.1f}% ({count:3d} trials)")
        
        print(f"\nTotal Trials: {total}")
    
    def create_target_radar_chart(self):
        """Create ASCII radar chart for target safety profiles"""
        print("\n" + "="*60)
        print("TARGET SAFETY RADAR CHART")
        print("="*60)
        
        # Calculate average rates by target
        target_rates = defaultdict(lambda: defaultdict(list))
        for trial in self.trials_data:
            target = trial['target']
            toxicity = next((t for t in self.toxicity_data if t['nct_id'] == trial['nct_id']), None)
            if toxicity:
                target_rates[target]['hepatotoxicity'].append(float(toxicity['hepatotoxicity_rate']))
                target_rates[target]['cardiotoxicity'].append(float(toxicity['cardiotoxicity_rate']))
                target_rates[target]['neurotoxicity'].append(float(toxicity['neurotoxicity_rate']))
                target_rates[target]['immunotoxicity'].append(float(toxicity['immunotoxicity_rate']))
                target_rates[target]['cytokine_release'].append(float(toxicity['cytokine_release_rate']))
                target_rates[target]['infusion_reaction'].append(float(toxicity['infusion_reaction_rate']))
        
        # Display radar chart for top targets
        top_targets = sorted(target_rates.items(), key=lambda x: len(x[1]['hepatotoxicity']), reverse=True)[:5]
        
        for target, rates in top_targets:
            print(f"\n{target} Target Safety Profile:")
            print("-" * 40)
            
            avg_rates = {}
            for toxicity_type, rate_list in rates.items():
                avg_rates[toxicity_type] = sum(rate_list) / len(rate_list)
            
            # Create radar visualization
            max_rate = max(avg_rates.values())
            chart_width = 30
            
            for toxicity_type, rate in avg_rates.items():
                bar_length = int((rate / max_rate) * chart_width)
                bar = "█" * bar_length
                print(f"{toxicity_type:15} {bar} {rate:.3f}")
    
    def create_drug_safety_heatmap(self):
        """Create ASCII heatmap of drug safety scores"""
        print("\n" + "="*60)
        print("DRUG SAFETY HEATMAP")
        print("="*60)
        
        # Calculate average safety scores by drug
        drug_scores = defaultdict(list)
        for trial in self.trials_data:
            drug = trial['intervention_name']
            toxicity = next((t for t in self.toxicity_data if t['nct_id'] == trial['nct_id']), None)
            if toxicity:
                drug_scores[drug].append(float(toxicity['overall_safety_score']))
        
        # Create heatmap
        print("Safety Score Heatmap (Higher = Safer):")
        print("-" * 50)
        
        for drug, scores in sorted(drug_scores.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
            avg_score = sum(scores) / len(scores)
            trial_count = len(scores)
            
            # Create color-coded bar
            if avg_score >= 0.9:
                color = "🟢"  # Green for high safety
            elif avg_score >= 0.8:
                color = "🟡"  # Yellow for medium safety
            else:
                color = "🔴"  # Red for low safety
            
            bar_length = int(avg_score * 20)
            bar = "█" * bar_length
            print(f"{drug:15} {color} {bar} {avg_score:.3f} ({trial_count:2d} trials)")
    
    def create_adverse_events_tree(self):
        """Create ASCII tree of adverse events"""
        print("\n" + "="*60)
        print("ADVERSE EVENTS TREE")
        print("="*60)
        
        # Group adverse events by severity
        severity_groups = defaultdict(list)
        for ae in self.adverse_events_data:
            severity_groups[ae['severity']].append(ae['adverse_event'])
        
        # Create tree structure
        print("Adverse Events by Severity:")
        print("🌳 Root: All Adverse Events")
        
        for severity, events in severity_groups.items():
            event_counts = Counter(events)
            print(f"  ├─ {severity}:")
            
            for event, count in event_counts.most_common(5):
                print(f"  │  ├─ {event}: {count} occurrences")
            
            if len(event_counts) > 5:
                print(f"  │  └─ ... and {len(event_counts) - 5} more events")
    
    def create_safety_score_distribution(self):
        """Create ASCII histogram of safety scores"""
        print("\n" + "="*60)
        print("SAFETY SCORE DISTRIBUTION")
        print("="*60)
        
        # Collect all safety scores
        safety_scores = []
        for toxicity in self.toxicity_data:
            safety_scores.append(float(toxicity['overall_safety_score']))
        
        # Create histogram
        bins = [0.6, 0.7, 0.8, 0.9, 1.0]
        bin_counts = [0] * (len(bins) - 1)
        
        for score in safety_scores:
            for i in range(len(bins) - 1):
                if bins[i] <= score < bins[i + 1]:
                    bin_counts[i] += 1
                    break
        
        max_count = max(bin_counts)
        chart_height = 10
        
        print("Safety Score Distribution:")
        print("-" * 40)
        
        for i in range(chart_height, 0, -1):
            line = f"{i/chart_height*max_count:6.0f} |"
            for count in bin_counts:
                if count >= (i/chart_height * max_count):
                    line += " ██"
                else:
                    line += "   "
            print(line)
        
        print("      " + "-" * (len(bins) - 1) * 4)
        print("      ", end="")
        for i in range(len(bins) - 1):
            print(f"{bins[i]:.1f}-{bins[i+1]:.1f} ", end="")
        print()
    
    def create_toxicity_risk_matrix(self):
        """Create ASCII risk matrix"""
        print("\n" + "="*60)
        print("TOXICITY RISK MATRIX")
        print("="*60)
        
        # Calculate risk levels for each target
        target_risks = {}
        for trial in self.trials_data:
            target = trial['target']
            if target not in target_risks:
                target_risks[target] = {
                    'cardiotoxicity': [],
                    'hepatotoxicity': [],
                    'neurotoxicity': [],
                    'immunotoxicity': []
                }
            
            toxicity = next((t for t in self.toxicity_data if t['nct_id'] == trial['nct_id']), None)
            if toxicity:
                target_risks[target]['cardiotoxicity'].append(float(toxicity['cardiotoxicity_rate']))
                target_risks[target]['hepatotoxicity'].append(float(toxicity['hepatotoxicity_rate']))
                target_risks[target]['neurotoxicity'].append(float(toxicity['neurotoxicity_rate']))
                target_risks[target]['immunotoxicity'].append(float(toxicity['immunotoxicity_rate']))
        
        # Create risk matrix
        print("Risk Matrix (Cardiotoxicity vs Hepatotoxicity):")
        print("-" * 50)
        print("High Cardio | 🔴 🔴 🔴 🔴 🔴")
        print("            | 🔴 🔴 🔴 🔴 🟡")
        print("            | 🔴 🔴 🔴 🟡 🟢")
        print("            | 🔴 🔴 🟡 🟢 🟢")
        print("Low Cardio  | 🔴 🟡 🟢 🟢 🟢")
        print("            +-----------------")
        print("            Low Hepatotoxicity")
        print("            High Hepatotoxicity")
        
        print("\nTarget Positions:")
        for target, risks in target_risks.items():
            if risks['cardiotoxicity'] and risks['hepatotoxicity']:
                avg_cardio = sum(risks['cardiotoxicity']) / len(risks['cardiotoxicity'])
                avg_hepat = sum(risks['hepatotoxicity']) / len(risks['hepatotoxicity'])
                
                if avg_cardio > 0.2 and avg_hepat > 0.1:
                    risk_level = "🔴 High Risk"
                elif avg_cardio > 0.1 or avg_hepat > 0.05:
                    risk_level = "🟡 Medium Risk"
                else:
                    risk_level = "🟢 Low Risk"
                
                print(f"{target:12} | Cardio: {avg_cardio:.3f}, Hepat: {avg_hepat:.3f} | {risk_level}")
    
    def create_clinical_timeline(self):
        """Create ASCII timeline of clinical development"""
        print("\n" + "="*60)
        print("CLINICAL DEVELOPMENT TIMELINE")
        print("="*60)
        
        # Group trials by phase
        phase_counts = Counter(trial['phase'] for trial in self.trials_data)
        
        print("Clinical Trial Phases:")
        print("-" * 30)
        
        phases = ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']
        for phase in phases:
            count = phase_counts.get(phase, 0)
            percentage = (count / len(self.trials_data)) * 100
            
            # Create timeline bar
            bar_length = int(percentage / 5)
            bar = "█" * bar_length
            
            print(f"{phase:8} | {bar} {count:3d} trials ({percentage:5.1f}%)")
        
        print("\nDevelopment Pipeline:")
        print("Phase 1 → Phase 2 → Phase 3 → Phase 4")
        print("Safety   Efficacy  Confirm  Monitor")
    
    def create_summary_dashboard(self):
        """Create ASCII summary dashboard"""
        print("\n" + "="*60)
        print("ANTIBODY TOXICITY ANALYSIS DASHBOARD")
        print("="*60)
        
        # Calculate key metrics
        total_trials = len(self.trials_data)
        total_events = len(self.adverse_events_data)
        unique_drugs = len(set(trial['intervention_name'] for trial in self.trials_data))
        unique_targets = len(set(trial['target'] for trial in self.trials_data))
        
        # Calculate average safety score
        safety_scores = [float(t['overall_safety_score']) for t in self.toxicity_data]
        avg_safety = sum(safety_scores) / len(safety_scores)
        
        # Calculate most common adverse event
        event_counts = Counter(ae['adverse_event'] for ae in self.adverse_events_data)
        most_common_event = event_counts.most_common(1)[0]
        
        # Calculate highest risk target
        target_risks = defaultdict(list)
        for trial in self.trials_data:
            target = trial['target']
            toxicity = next((t for t in self.toxicity_data if t['nct_id'] == trial['nct_id']), None)
            if toxicity:
                total_risk = (float(toxicity['hepatotoxicity_rate']) + 
                            float(toxicity['cardiotoxicity_rate']) + 
                            float(toxicity['neurotoxicity_rate']) + 
                            float(toxicity['immunotoxicity_rate']))
                target_risks[target].append(total_risk)
        
        highest_risk_target = max(target_risks.items(), key=lambda x: sum(x[1])/len(x[1]))
        
        # Create dashboard
        print("📊 KEY METRICS:")
        print(f"   Total Trials: {total_trials}")
        print(f"   Adverse Events: {total_events}")
        print(f"   Unique Drugs: {unique_drugs}")
        print(f"   Molecular Targets: {unique_targets}")
        print(f"   Average Safety Score: {avg_safety:.3f}")
        
        print("\n🚨 SAFETY ALERTS:")
        print(f"   Most Common AE: {most_common_event[0]} ({most_common_event[1]} occurrences)")
        print(f"   Highest Risk Target: {highest_risk_target[0]} (avg risk: {sum(highest_risk_target[1])/len(highest_risk_target[1]):.3f})")
        
        print("\n🎯 CLINICAL RECOMMENDATIONS:")
        print("   • Monitor infusion reactions (most common)")
        print("   • Cardiac monitoring for HER2-targeting drugs")
        print("   • Immune monitoring for checkpoint inhibitors")
        print("   • Premedication for high-risk drugs")
        
        print("\n📈 NEXT STEPS:")
        print("   • Review detailed CSV exports")
        print("   • Analyze specific drug profiles")
        print("   • Develop monitoring protocols")
        print("   • Consider real-world evidence integration")
    
    def export_all_data(self):
        """Export all data and generate visualizations"""
        print("Starting comprehensive data export and visualization...")
        
        # Load data
        self.load_analysis_data()
        
        # Export CSV data
        self.export_comprehensive_csv_data()
        
        # Generate creative plots
        self.generate_creative_plots()
        
        # Create summary file
        self.create_export_summary()
        
        print(f"\n✅ All data exported to {self.output_dir}/")
        print("📊 Creative visualizations generated")
        print("📋 Summary report created")
    
    def create_export_summary(self):
        """Create a summary of all exported data"""
        summary = f"""
# Antibody Therapeutics Toxicity Analysis - Data Export Summary
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Exported CSV Files

### 1. trials_summary.csv
- Complete trial information with toxicity profiles
- Columns: nct_id, drug, target, indication, toxicity_profile, phase, enrollment, status, all toxicity rates, safety score
- Rows: {len(self.trials_data)}

### 2. target_analysis.csv
- Molecular target-specific toxicity analysis
- Columns: target, trial_count, average rates for all toxicity types, safety score
- Rows: {len(set(trial['target'] for trial in self.trials_data))}

### 3. drug_analysis.csv
- Drug-specific toxicity analysis
- Columns: drug, trial_count, targets, toxicity_profiles, average rates, safety score
- Rows: {len(set(trial['intervention_name'] for trial in self.trials_data))}

### 4. adverse_events_analysis.csv
- Comprehensive adverse events analysis
- Columns: adverse_event, total_count, serious_count, severity breakdown, associated drugs/targets
- Rows: {len(set(ae['adverse_event'] for ae in self.adverse_events_data))}

### 5. toxicity_profile_analysis.csv
- Toxicity profile-specific analysis
- Columns: toxicity_profile, trial_count, drugs, targets, average rates, safety score
- Rows: {len(set(trial['toxicity_profile'] for trial in self.trials_data))}

## Key Insights

### Toxicity Profile Distribution
{self.get_toxicity_profile_summary()}

### Target Safety Rankings
{self.get_target_safety_summary()}

### Drug Safety Rankings
{self.get_drug_safety_summary()}

### Most Common Adverse Events
{self.get_adverse_events_summary()}

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
"""
        
        with open(os.path.join(self.output_dir, 'EXPORT_SUMMARY.md'), 'w') as f:
            f.write(summary)
    
    def get_toxicity_profile_summary(self):
        """Get summary of toxicity profiles"""
        profile_counts = Counter(trial['toxicity_profile'] for trial in self.trials_data)
        summary = ""
        for profile, count in profile_counts.most_common():
            percentage = (count / len(self.trials_data)) * 100
            summary += f"- {profile}: {count} trials ({percentage:.1f}%)\n"
        return summary
    
    def get_target_safety_summary(self):
        """Get summary of target safety"""
        target_scores = defaultdict(list)
        for trial in self.trials_data:
            target = trial['target']
            toxicity = next((t for t in self.toxicity_data if t['nct_id'] == trial['nct_id']), None)
            if toxicity:
                target_scores[target].append(float(toxicity['overall_safety_score']))
        
        avg_scores = {target: sum(scores)/len(scores) for target, scores in target_scores.items()}
        sorted_targets = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        
        summary = ""
        for target, score in sorted_targets[:5]:
            summary += f"- {target}: {score:.3f} safety score\n"
        return summary
    
    def get_drug_safety_summary(self):
        """Get summary of drug safety"""
        drug_scores = defaultdict(list)
        for trial in self.trials_data:
            drug = trial['intervention_name']
            toxicity = next((t for t in self.toxicity_data if t['nct_id'] == trial['nct_id']), None)
            if toxicity:
                drug_scores[drug].append(float(toxicity['overall_safety_score']))
        
        avg_scores = {drug: sum(scores)/len(scores) for drug, scores in drug_scores.items()}
        sorted_drugs = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        
        summary = ""
        for drug, score in sorted_drugs[:5]:
            summary += f"- {drug}: {score:.3f} safety score\n"
        return summary
    
    def get_adverse_events_summary(self):
        """Get summary of adverse events"""
        event_counts = Counter(ae['adverse_event'] for ae in self.adverse_events_data)
        summary = ""
        for event, count in event_counts.most_common(5):
            summary += f"- {event}: {count} occurrences\n"
        return summary

def main():
    """Main function"""
    print("Antibody Therapeutics Toxicity Analysis - Data Export and Visualization")
    print("=" * 80)
    
    exporter = DataExporterAndVisualizer()
    exporter.export_all_data()
    
    print("\n🎉 Export and visualization completed successfully!")
    print("📁 Check the 'exported_data' directory for all CSV files and summary")

if __name__ == "__main__":
    main()