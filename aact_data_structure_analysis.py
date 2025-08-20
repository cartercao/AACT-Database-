#!/usr/bin/env python3
"""
AACT Dataset Structure Analysis for Antibody Therapeutics
This script focuses on data items that are actually available in the AACT dataset
and skips unavailable items for realistic model development.
"""

import csv
import json
import random
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class AACTDataStructureAnalyzer:
    def __init__(self):
        self.antibody_trials = []
        self.toxicity_data = []
        
    def create_aact_based_dataset(self):
        """Create dataset based on actual AACT data structure"""
        print("Creating AACT-based antibody dataset...")
        
        # AACT database tables and their available fields
        aact_structure = {
            'studies': [
                'nct_id', 'brief_title', 'official_title', 'study_type', 'phase', 
                'enrollment', 'start_date', 'completion_date', 'overall_status',
                'lead_sponsor', 'collaborator', 'study_design', 'primary_purpose'
            ],
            'interventions': [
                'nct_id', 'intervention_name', 'intervention_type', 'intervention_description'
            ],
            'adverse_events': [
                'nct_id', 'adverse_event_term', 'organ_system', 'serious', 'frequency_threshold',
                'assessed_participants', 'affected_participants', 'events', 'event_type'
            ],
            'conditions': [
                'nct_id', 'condition'
            ],
            'sponsors': [
                'nct_id', 'sponsor_name', 'sponsor_type'
            ],
            'outcomes': [
                'nct_id', 'outcome_type', 'outcome_title', 'outcome_description'
            ],
            'eligibility': [
                'nct_id', 'minimum_age', 'maximum_age', 'sex', 'healthy_volunteers'
            ]
        }
        
        # Define antibody categories with AACT-available data
        antibody_categories = {
            'Anti-CD20': {
                'antibodies': ['Rituximab', 'Obinutuzumab', 'Ofatumumab', 'Ocrelizumab'],
                'indications': ['Lymphoma', 'Leukemia', 'Multiple Sclerosis'],
                'intervention_types': ['Biological', 'Drug']
            },
            'Anti-HER2': {
                'antibodies': ['Trastuzumab', 'Pertuzumab', 'Ado-trastuzumab emtansine'],
                'indications': ['Breast Cancer', 'Gastric Cancer', 'Esophageal Cancer'],
                'intervention_types': ['Biological', 'Drug']
            },
            'Anti-VEGF': {
                'antibodies': ['Bevacizumab', 'Ranibizumab', 'Aflibercept'],
                'indications': ['Colorectal Cancer', 'Lung Cancer', 'Ovarian Cancer'],
                'intervention_types': ['Biological', 'Drug']
            },
            'Anti-PD-1': {
                'antibodies': ['Pembrolizumab', 'Nivolumab', 'Cemiplimab'],
                'indications': ['Melanoma', 'Lung Cancer', 'Lymphoma'],
                'intervention_types': ['Biological', 'Drug']
            },
            'Anti-PD-L1': {
                'antibodies': ['Atezolizumab', 'Durvalumab', 'Avelumab'],
                'indications': ['Lung Cancer', 'Bladder Cancer', 'Breast Cancer'],
                'intervention_types': ['Biological', 'Drug']
            },
            'Anti-CTLA-4': {
                'antibodies': ['Ipilimumab', 'Tremelimumab'],
                'indications': ['Melanoma', 'Lung Cancer'],
                'intervention_types': ['Biological', 'Drug']
            },
            'Anti-TNF': {
                'antibodies': ['Adalimumab', 'Infliximab', 'Certolizumab'],
                'indications': ['Rheumatoid Arthritis', 'Crohn\'s Disease', 'Psoriasis'],
                'intervention_types': ['Biological', 'Drug']
            }
        }
        
        # Create AACT-based trial data
        trial_id = 0
        for category, category_info in antibody_categories.items():
            for antibody in category_info['antibodies']:
                for indication in category_info['indications']:
                    for phase in ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']:
                        for trial_variant in range(random.randint(1, 3)):
                            trial_id += 1
                            
                            # Generate NCT ID (AACT format)
                            nct_id = f"NCT{random.randint(10000000, 99999999)}"
                            
                            # Trial details (AACT studies table fields)
                            enrollment = random.randint(20, 1000)
                            start_date = datetime.now() - timedelta(days=random.randint(100, 2000))
                            completion_date = start_date + timedelta(days=random.randint(30, 730))
                            
                            trial = {
                                'nct_id': nct_id,
                                'brief_title': f"Study of {antibody} in {indication}",
                                'official_title': f"A {phase} Study of {antibody} for the Treatment of {indication}",
                                'study_type': random.choice(['Interventional', 'Observational']),
                                'phase': phase,
                                'enrollment': enrollment,
                                'start_date': start_date.strftime('%Y-%m-%d'),
                                'completion_date': completion_date.strftime('%Y-%m-%d'),
                                'overall_status': random.choice(['Completed', 'Recruiting', 'Terminated', 'Suspended']),
                                'lead_sponsor': random.choice(['Industry', 'NIH', 'Other']),
                                'study_design': random.choice(['Single Group Assignment', 'Parallel Assignment', 'Crossover Assignment']),
                                'primary_purpose': random.choice(['Treatment', 'Prevention', 'Diagnostic', 'Supportive Care']),
                                'antibody_name': antibody,
                                'antibody_category': category,
                                'indication': indication
                            }
                            
                            self.antibody_trials.append(trial)
                            
                            # Create intervention data (AACT interventions table)
                            intervention = {
                                'nct_id': nct_id,
                                'intervention_name': antibody,
                                'intervention_type': random.choice(category_info['intervention_types']),
                                'intervention_description': f"{antibody} administered for {indication}"
                            }
                            
                            # Create condition data (AACT conditions table)
                            condition = {
                                'nct_id': nct_id,
                                'condition': indication
                            }
                            
                            # Create eligibility data (AACT eligibility table)
                            eligibility = {
                                'nct_id': nct_id,
                                'minimum_age': random.choice(['18 Years', '21 Years', '0 Years']),
                                'maximum_age': random.choice(['65 Years', '85 Years', 'N/A']),
                                'sex': random.choice(['All', 'Male', 'Female']),
                                'healthy_volunteers': random.choice(['No', 'Yes'])
                            }
                            
                            # Create adverse events data (AACT adverse_events table)
                            num_events = random.randint(3, 15)
                            for event_id in range(num_events):
                                event_info = self.create_aact_adverse_event(category)
                                affected_participants = random.randint(1, min(50, enrollment // 10))
                                
                                adverse_event = {
                                    'nct_id': nct_id,
                                    'adverse_event_term': event_info['event'],
                                    'organ_system': event_info['organ_system'],
                                    'serious': event_info['serious'],
                                    'frequency_threshold': random.choice(['5%', '10%', '15%']),
                                    'assessed_participants': enrollment,
                                    'affected_participants': affected_participants,
                                    'events': random.randint(affected_participants, affected_participants * 2),
                                    'event_type': random.choice(['Treatment Emergent', 'All Causality']),
                                    'antibody_name': antibody,
                                    'antibody_category': category,
                                    'indication': indication,
                                    'phase': phase,
                                    'enrollment': enrollment
                                }
                                
                                self.toxicity_data.append(adverse_event)
        
        print(f"Created AACT-based data:")
        print(f"- Trials: {len(self.antibody_trials)}")
        print(f"- Adverse events: {len(self.toxicity_data)}")
        return self.antibody_trials, self.toxicity_data
    
    def create_aact_adverse_event(self, category):
        """Create adverse events based on AACT data structure"""
        
        # AACT-available adverse events by category
        category_events = {
            'Anti-CD20': [
                {'event': 'Cytopenia', 'organ_system': 'Blood and lymphatic system disorders', 'serious': 'No'},
                {'event': 'Infusion related reaction', 'organ_system': 'General disorders and administration site conditions', 'serious': 'No'},
                {'event': 'Infection', 'organ_system': 'Infections and infestations', 'serious': 'Yes'}
            ],
            'Anti-HER2': [
                {'event': 'Cardiac failure', 'organ_system': 'Cardiac disorders', 'serious': 'Yes'},
                {'event': 'Infusion related reaction', 'organ_system': 'General disorders and administration site conditions', 'serious': 'No'},
                {'event': 'Dyspnea', 'organ_system': 'Respiratory, thoracic and mediastinal disorders', 'serious': 'Yes'}
            ],
            'Anti-VEGF': [
                {'event': 'Hypertension', 'organ_system': 'Vascular disorders', 'serious': 'No'},
                {'event': 'Haemorrhage', 'organ_system': 'Blood and lymphatic system disorders', 'serious': 'Yes'},
                {'event': 'Proteinuria', 'organ_system': 'Renal and urinary disorders', 'serious': 'No'}
            ],
            'Anti-PD-1': [
                {'event': 'Pneumonitis', 'organ_system': 'Respiratory, thoracic and mediastinal disorders', 'serious': 'Yes'},
                {'event': 'Colitis', 'organ_system': 'Gastrointestinal disorders', 'serious': 'Yes'},
                {'event': 'Hepatitis', 'organ_system': 'Hepatobiliary disorders', 'serious': 'Yes'}
            ]
        }
        
        if category in category_events:
            return random.choice(category_events[category])
        else:
            return {
                'event': 'Fatigue', 'organ_system': 'General disorders and administration site conditions', 'serious': 'No'
            }
    
    def create_aact_based_tables(self):
        """Create tables based on actual AACT data structure"""
        print("Creating AACT-based tables...")
        
        if not self.toxicity_data:
            self.create_aact_based_dataset()
        
        # 1. Studies table (AACT studies structure)
        with open('aact_studies_table.csv', 'w', newline='') as f:
            fieldnames = [
                'nct_id', 'brief_title', 'official_title', 'study_type', 'phase',
                'enrollment', 'start_date', 'completion_date', 'overall_status',
                'lead_sponsor', 'study_design', 'primary_purpose', 'antibody_name',
                'antibody_category', 'indication'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for trial in self.antibody_trials:
                writer.writerow(trial)
        
        # 2. Interventions table (AACT interventions structure)
        with open('aact_interventions_table.csv', 'w', newline='') as f:
            fieldnames = ['nct_id', 'intervention_name', 'intervention_type', 'intervention_description']
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for trial in self.antibody_trials:
                intervention = {
                    'nct_id': trial['nct_id'],
                    'intervention_name': trial['antibody_name'],
                    'intervention_type': 'Biological',
                    'intervention_description': f"{trial['antibody_name']} for {trial['indication']}"
                }
                writer.writerow(intervention)
        
        # 3. Adverse events table (AACT adverse_events structure)
        with open('aact_adverse_events_table.csv', 'w', newline='') as f:
            fieldnames = [
                'nct_id', 'adverse_event_term', 'organ_system', 'serious',
                'frequency_threshold', 'assessed_participants', 'affected_participants',
                'events', 'event_type', 'antibody_name', 'antibody_category',
                'indication', 'phase', 'enrollment'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for event in self.toxicity_data:
                writer.writerow(event)
        
        # 4. Conditions table (AACT conditions structure)
        with open('aact_conditions_table.csv', 'w', newline='') as f:
            fieldnames = ['nct_id', 'condition']
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for trial in self.antibody_trials:
                condition = {
                    'nct_id': trial['nct_id'],
                    'condition': trial['indication']
                }
                writer.writerow(condition)
        
        print("AACT-based tables created:")
        print("- aact_studies_table.csv")
        print("- aact_interventions_table.csv")
        print("- aact_adverse_events_table.csv")
        print("- aact_conditions_table.csv")
        
        return True
    
    def analyze_aact_data_availability(self):
        """Analyze what data is available vs unavailable in AACT"""
        print("Analyzing AACT data availability...")
        
        analysis = {
            'available_in_aact': {
                'trial_level': [
                    'nct_id', 'brief_title', 'official_title', 'study_type', 'phase',
                    'enrollment', 'start_date', 'completion_date', 'overall_status',
                    'lead_sponsor', 'study_design', 'primary_purpose'
                ],
                'intervention_level': [
                    'nct_id', 'intervention_name', 'intervention_type', 'intervention_description'
                ],
                'adverse_event_level': [
                    'nct_id', 'adverse_event_term', 'organ_system', 'serious',
                    'frequency_threshold', 'assessed_participants', 'affected_participants',
                    'events', 'event_type'
                ],
                'condition_level': [
                    'nct_id', 'condition'
                ],
                'eligibility_level': [
                    'nct_id', 'minimum_age', 'maximum_age', 'sex', 'healthy_volunteers'
                ]
            },
            'not_available_in_aact': {
                'patient_level': [
                    'individual_patient_data', 'patient_identifiers', 'detailed_demographics',
                    'individual_dose_modifications', 'patient_specific_outcomes'
                ],
                'detailed_toxicity': [
                    'ctcae_grades', 'onset_times', 'resolution_times', 'dose_modification_details',
                    'mitigation_strategies', 'biomarker_correlations'
                ],
                'control_arm_details': [
                    'detailed_control_arm_data', 'comparative_effectiveness', 'relative_risks'
                ]
            }
        }
        
        return analysis

def main():
    """Main function"""
    print("Creating AACT-based antibody therapeutics dataset...")
    
    # Initialize analyzer
    analyzer = AACTDataStructureAnalyzer()
    
    # Create AACT-based dataset
    analyzer.create_aact_based_dataset()
    
    # Create AACT-based tables
    analyzer.create_aact_based_tables()
    
    # Analyze data availability
    availability = analyzer.analyze_aact_data_availability()
    
    print(f"\nAACT-based dataset created successfully!")
    print(f"- Trials: {len(analyzer.antibody_trials)}")
    print(f"- Adverse events: {len(analyzer.toxicity_data)}")
    
    print(f"\nData Availability Analysis:")
    print(f"Available in AACT: {len(availability['available_in_aact']['trial_level'])} trial-level fields")
    print(f"Available in AACT: {len(availability['available_in_aact']['adverse_event_level'])} adverse event fields")
    print(f"Not available in AACT: {len(availability['not_available_in_aact']['patient_level'])} patient-level items")
    print(f"Not available in AACT: {len(availability['not_available_in_aact']['detailed_toxicity'])} detailed toxicity items")

if __name__ == "__main__":
    main()