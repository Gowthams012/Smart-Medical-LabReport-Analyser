"""
Smart Patient-Based PDF Segregation System
Automatically identifies patients from PDFs and organizes them into individual vaults
Uses AI for intelligent name matching and deduplication
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ExtractionAgent'))

from pdf_extraction import AdvancedPDFExtractor
from data_structuring import CSVToStructuredJSON

# Import AI capabilities
try:
    from google import genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️  Warning: google-genai not installed. Using fallback matching.")


class Config:
    """Configuration for Patient Vault System"""
    API_KEY = os.getenv('GEMINI_API_KEY')
    MODELS = [
        'gemini-2.5-flash',
        'gemini-flash-latest',
        'gemini-2.0-flash-lite',
        'gemini-2.5-flash-lite'
    ]
    SIMILARITY_THRESHOLD = 0.85  # 85% similarity for name matching
    VAULT_BASE_DIR = "PatientVaults"
    DEBUG = False


class PatientIdentifier:
    """
    AI-powered patient identification and name matching
    Handles variations like:
    - "John Smith" vs "Smith, John"
    - "Dr. John A. Smith" vs "John Smith"
    - "JOHN SMITH" vs "john smith"
    """
    
    def __init__(self):
        """Initialize the AI client if available"""
        self.client = None
        if AI_AVAILABLE and Config.API_KEY:
            try:
                self.client = genai.Client(api_key=Config.API_KEY)
            except Exception as e:
                print(f"⚠️  AI client initialization failed: {e}")
    
    def normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        if not name:
            return ""
        
        # Convert to lowercase, remove extra spaces
        name = name.lower().strip()
        
        # Remove titles and prefixes
        titles = ['dr', 'dr.', 'mr', 'mr.', 'mrs', 'mrs.', 'ms', 'ms.', 'prof', 'prof.']
        words = name.split()
        filtered_words = [w for w in words if w.replace('.', '') not in titles]
        
        # Remove special characters
        name = ' '.join(filtered_words)
        name = ''.join(c for c in name if c.isalnum() or c.isspace())
        
        return ' '.join(name.split())  # Remove extra spaces
    
    def extract_core_name(self, name: str) -> str:
        """Extract first and last name only"""
        normalized = self.normalize_name(name)
        
        # Handle "LastName, FirstName" format
        if ',' in normalized:
            parts = normalized.split(',')
            if len(parts) == 2:
                # Reverse order: "smith, john" -> "john smith"
                last_name = parts[0].strip()
                first_name = parts[1].strip()
                normalized = f"{first_name} {last_name}"
        
        words = normalized.split()
        
        if len(words) == 0:
            return ""
        elif len(words) == 1:
            return words[0]
        elif len(words) == 2:
            return normalized
        else:
            # Take first and last word (common pattern)
            return f"{words[0]} {words[-1]}"
    
    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity score between two names"""
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        # Direct match
        if norm1 == norm2:
            return 1.0
        
        # Extract core names (handles "LastName, FirstName" format)
        core1 = self.extract_core_name(name1)
        core2 = self.extract_core_name(name2)
        
        if core1 == core2 and core1:
            return 0.95
        
        # Check if names are reversed (word order)
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        # If same words, just different order
        if words1 == words2 and len(words1) > 0:
            return 0.90
        
        # Use sequence matcher
        ratio = SequenceMatcher(None, norm1, norm2).ratio()
        
        return ratio
    
    def use_ai_matching(self, name1: str, name2: str) -> Tuple[bool, float, str]:
        """
        Use AI to determine if two names refer to the same person
        Returns: (is_match, confidence, explanation)
        """
        if not self.client:
            # Fallback to rule-based
            similarity = self.calculate_similarity(name1, name2)
            is_match = similarity >= Config.SIMILARITY_THRESHOLD
            return is_match, similarity, "Rule-based matching"
        
        try:
            prompt = f"""You are a medical records expert. Determine if these two patient names refer to the SAME person:

Name 1: "{name1}"
Name 2: "{name2}"

Consider:
- Name order variations (John Smith vs Smith, John)
- Middle initials or names
- Titles (Dr., Mr., Mrs.)
- Spelling variations
- Case differences

Respond in this EXACT JSON format:
{{
    "is_match": true/false,
    "confidence": 0.0-1.0,
    "explanation": "brief reason"
}}"""

            response = self.client.models.generate_content(
                model=Config.MODELS[0],
                contents=prompt
            )
            
            # Parse AI response
            response_text = response.text.strip()
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return (
                    result.get('is_match', False),
                    float(result.get('confidence', 0.0)),
                    result.get('explanation', 'AI analysis')
                )
            
        except Exception as e:
            if Config.DEBUG:
                print(f"AI matching failed: {e}")
        
        # Fallback to rule-based
        similarity = self.calculate_similarity(name1, name2)
        is_match = similarity >= Config.SIMILARITY_THRESHOLD
        return is_match, similarity, "Fallback matching"
    
    def find_matching_patient(self, 
                            new_name: str, 
                            existing_patients: List[Dict]) -> Optional[Dict]:
        """
        Find if the new patient matches any existing patient
        Returns matching patient info or None
        """
        best_match = None
        best_score = 0.0
        
        for patient in existing_patients:
            existing_name = patient.get('canonical_name', '')
            
            if Config.API_KEY and AI_AVAILABLE:
                is_match, confidence, explanation = self.use_ai_matching(
                    new_name, existing_name
                )
                if is_match and confidence > best_score:
                    best_match = patient
                    best_score = confidence
            else:
                similarity = self.calculate_similarity(new_name, existing_name)
                if similarity >= Config.SIMILARITY_THRESHOLD and similarity > best_score:
                    best_match = patient
                    best_score = similarity
        
        if best_match and best_score >= Config.SIMILARITY_THRESHOLD:
            return best_match
        
        return None


class PatientVault:
    """
    Manages individual patient's vault
    Stores all reports chronologically
    """
    
    def __init__(self, vault_dir: str, patient_info: Dict):
        """Initialize patient vault"""
        self.vault_dir = vault_dir
        self.patient_info = patient_info
        
        # Create directory
        os.makedirs(self.vault_dir, exist_ok=True)
    

    
    def get_all_reports(self) -> List[str]:
        """Get list of all reports in vault"""
        if not os.path.exists(self.vault_dir):
            return []
        
        reports = []
        for file in os.listdir(self.vault_dir):
            if file.endswith('.pdf'):
                reports.append(os.path.join(self.vault_dir, file))
        
        return sorted(reports)
    
    def add_report(self, pdf_path: str, json_data: Dict = None) -> str:
        """
        Add a new report to the vault
        Returns the PDF path
        """
        # Copy PDF directly to patient folder
        pdf_dest = os.path.join(self.vault_dir, os.path.basename(pdf_path))
        shutil.copy2(pdf_path, pdf_dest)
        
        return pdf_dest


class SmartVaultManager:
    """
    Main manager for the Smart Patient Vault system
    Orchestrates PDF processing and patient identification
    """
    
    def __init__(self, vault_base_dir: str = None):
        """Initialize the vault manager"""
        self.vault_base_dir = vault_base_dir or Config.VAULT_BASE_DIR
        self.identifier = PatientIdentifier()
        self.vaults = {}  # patient_id -> PatientVault
        
        os.makedirs(self.vault_base_dir, exist_ok=True)
        
        # Load existing vaults
        self._load_existing_vaults()
    
    def _load_existing_vaults(self):
        """Load all existing patient vaults"""
        if not os.path.exists(self.vault_base_dir):
            return
        
        for patient_dir in os.listdir(self.vault_base_dir):
            vault_path = os.path.join(self.vault_base_dir, patient_dir)
            if os.path.isdir(vault_path):
                metadata_path = os.path.join(vault_path, "patient_metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        patient_id = patient_dir
                        self.vaults[patient_id] = PatientVault(vault_path, metadata)
    
    def get_existing_patients(self) -> List[Dict]:
        """Get list of all existing patients"""
        patients = []
        for patient_id, vault in self.vaults.items():
            with open(vault.metadata_file, 'r') as f:
                metadata = json.load(f)
                metadata['patient_id'] = patient_id
                patients.append(metadata)
        return patients
    
    def _generate_patient_id(self, name: str) -> str:
        """Generate a unique patient ID from name"""
        # Normalize name for ID
        normalized = self.identifier.normalize_name(name)
        # Replace spaces with underscores
        patient_id = normalized.replace(' ', '_')
        
        # Ensure uniqueness
        base_id = patient_id
        counter = 1
        while patient_id in self.vaults:
            patient_id = f"{base_id}_{counter}"
            counter += 1
        
        return patient_id
    
    def extract_patient_info(self, pdf_path: str) -> Dict:
        """
        Extract patient information from PDF
        Returns patient info dictionary
        """
        print(f"\n📄 Extracting patient info from PDF...")
        
        # Create temporary directory for extraction
        temp_dir = os.path.join(self.vault_base_dir, ".temp_extraction")
        csv_dir = os.path.join(temp_dir, "csv")
        json_dir = os.path.join(temp_dir, "json")
        
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)
        
        try:
            # Extract PDF to CSV
            extractor = AdvancedPDFExtractor(pdf_path)
            csv_files = extractor.extract_to_csv(
                output_dir=csv_dir,
                separate_tables=True
            )
            
            # Convert to JSON
            converter = CSVToStructuredJSON(csv_dir)
            pdf_name = Path(pdf_path).stem
            medical_json_path = os.path.join(json_dir, f"{pdf_name}_medical_report.json")
            medical_data = converter.create_medical_report_json(medical_json_path)
            
            # Extract patient information
            patient_info = medical_data.get('patient', {})
            demographics = patient_info.get('demographics', {})
            
            # Get patient name
            patient_name = demographics.get('name', 'Unknown Patient')
            
            # Prepare patient info
            result = {
                'canonical_name': patient_name,
                'name_variations': [patient_name],
                'demographics': demographics,
                'created_at': datetime.now().isoformat(),
                'medical_data': medical_data
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error extracting patient info: {e}")
            raise
        
        finally:
            # Cleanup temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def process_pdf(self, pdf_path: str, patient_hint: str = None) -> Dict:
        """
        Main method to process a PDF and assign it to the correct patient vault
        
        Args:
            pdf_path: Path to the PDF file
            patient_hint: Optional hint about patient name (for manual override)
        
        Returns:
            Dictionary with processing results
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"\n{'='*70}")
        print(f"🔍 SMART PATIENT VAULT SYSTEM")
        print(f"{'='*70}")
        print(f"📄 Processing: {os.path.basename(pdf_path)}")
        
        # Extract patient information
        patient_info = self.extract_patient_info(pdf_path)
        patient_name = patient_info['canonical_name']
        
        print(f"✅ Extracted patient: {patient_name}")
        
        # Use hint if provided
        if patient_hint:
            patient_name = patient_hint
            patient_info['canonical_name'] = patient_hint
            print(f"   Using hint: {patient_hint}")
        
        # Find matching patient
        existing_patients = self.get_existing_patients()
        matched_patient = self.identifier.find_matching_patient(
            patient_name, existing_patients
        )
        
        if matched_patient:
            # Existing patient found
            patient_id = matched_patient['patient_id']
            print(f"\n👤 Matched existing patient: {matched_patient['canonical_name']}")
            print(f"   Patient ID: {patient_id}")
            print(f"   Existing reports: {matched_patient.get('report_count', 0)}")
            
            # Update name variations
            vault = self.vaults[patient_id]
            metadata_path = vault.metadata_file
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            if patient_name not in metadata.get('name_variations', []):
                metadata['name_variations'].append(patient_name)
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
        else:
            # New patient
            patient_id = self._generate_patient_id(patient_name)
            vault_dir = os.path.join(self.vault_base_dir, patient_id)
            
            print(f"\n🆕 New patient detected")
            print(f"   Patient ID: {patient_id}")
            print(f"   Creating vault: {vault_dir}")
            
            vault = PatientVault(vault_dir, patient_info)
            self.vaults[patient_id] = vault
        
        # Add report to vault
        print(f"\n💾 Adding report to vault...")
        report_path = vault.add_report(pdf_path, patient_info.get('medical_data'))
        
        print(f"✅ Report saved: {report_path}")
        
        # Summary
        print(f"\n{'='*70}")
        print(f"✅ PROCESSING COMPLETE")
        print(f"{'='*70}")
        print(f"Patient: {patient_name}")
        print(f"Vault: {vault.vault_dir}")
        print(f"Total Reports: {len(vault.get_all_reports())}")
        print(f"{'='*70}\n")
        
        return {
            'status': 'success',
            'patient_id': patient_id,
            'patient_name': patient_name,
            'vault_dir': vault.vault_dir,
            'report_path': report_path,
            'is_new_patient': matched_patient is None,
            'total_reports': len(vault.get_all_reports())
        }
    
    def process_multiple_pdfs(self, pdf_paths: List[str]) -> List[Dict]:
        """
        Process multiple PDFs at once
        Automatically segregates by patient
        """
        results = []
        
        print(f"\n{'='*70}")
        print(f"📦 BATCH PROCESSING: {len(pdf_paths)} PDFs")
        print(f"{'='*70}\n")
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            print(f"\n[{i}/{len(pdf_paths)}] Processing {os.path.basename(pdf_path)}...")
            try:
                result = self.process_pdf(pdf_path)
                results.append(result)
            except Exception as e:
                print(f"❌ Failed: {e}")
                results.append({
                    'status': 'failed',
                    'pdf_path': pdf_path,
                    'error': str(e)
                })
        
        # Display summary
        self.display_vault_summary()
        
        return results
    
    def display_vault_summary(self):
        """Display summary of all patient vaults"""
        print(f"\n{'='*70}")
        print(f"📊 PATIENT VAULT SUMMARY")
        print(f"{'='*70}\n")
        
        patients = self.get_existing_patients()
        
        if not patients:
            print("No patients in vault system yet.\n")
            return
        
        for patient in patients:
            print(f"👤 {patient['canonical_name']}")
            print(f"   ID: {patient['patient_id']}")
            print(f"   Reports: {patient.get('report_count', 0)}")
            print(f"   Path: {patient['vault_path']}")
            
            demo = patient.get('demographics', {})
            if demo.get('age'):
                print(f"   Age: {demo['age']} {demo.get('age_unit', '')}")
            if demo.get('gender'):
                print(f"   Gender: {demo['gender']}")
            
            print()
        
        print(f"Total Patients: {len(patients)}")
        print(f"{'='*70}\n")


def main():
    """Main entry point for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Smart Patient-Based PDF Segregation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process single PDF
    python VaultAgent.py report1.pdf
  
    # Process multiple PDFs
    python VaultAgent.py report1.pdf report2.pdf report3.pdf
  
    # Process with patient hint
    python VaultAgent.py report1.pdf --hint "John Smith"
  
    # Show vault summary
    python VaultAgent.py --summary
        """
    )
    
    parser.add_argument('pdfs', nargs='*', help='PDF files to process')
    parser.add_argument('--hint', type=str, help='Patient name hint for manual override')
    parser.add_argument('--summary', action='store_true', help='Display vault summary')
    parser.add_argument('--vault-dir', type=str, help='Custom vault directory')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.debug:
        Config.DEBUG = True
    
    # Initialize vault manager
    manager = SmartVaultManager(vault_base_dir=args.vault_dir)
    
    if args.summary:
        manager.display_vault_summary()
        return
    
    if not args.pdfs:
        parser.print_help()
        print("\n⚠️  No PDF files provided. Use --summary to view existing vaults.")
        return
    
    # Process PDFs
    if len(args.pdfs) == 1:
        manager.process_pdf(args.pdfs[0], patient_hint=args.hint)
    else:
        if args.hint:
            print("⚠️  Warning: --hint ignored for batch processing")
        manager.process_multiple_pdfs(args.pdfs)


if __name__ == "__main__":
    main()
