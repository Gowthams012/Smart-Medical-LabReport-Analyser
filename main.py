"""
Integrated Workflow Test for Smart Medical Analyser
Complete Pipeline: PDF Upload → Extraction → Summary/Recommendations → Patient Vault

This demonstrates the full workflow:
1. User uploads PDF lab report
2. System extracts data (text, tables, JSON)
3. Generate clinical summary and recommendations
4. Segregate into patient-specific folders automatically
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add module paths
PROJECT_ROOT = Path(__file__).resolve().parent
AGENT_ROOT = PROJECT_ROOT / "python_agents"

for agent_dir in ("ExtractionAgent", "InsightAgent", "VaultAgent"):
    sys.path.insert(0, str(AGENT_ROOT / agent_dir))

from ExtractionAgent import SmartMedicalReportPipeline
from VaultAgent import SmartVaultManager

# Try to import Clinical Insight modules
try:
    import InsightAgent.Summary as SummaryModule
    import InsightAgent.Recommendation as RecommendationModule
    CLINICAL_AVAILABLE = True
except ImportError:
    CLINICAL_AVAILABLE = False
    print("⚠️  Clinical Insight modules not fully available")


def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_step(step_num, title):
    """Print step header"""
    print(f"\n{'─'*80}")
    print(f"  STEP {step_num}: {title}")
    print(f"{'─'*80}\n")


class IntegratedWorkflow:
    """
    Complete integrated workflow manager
    Orchestrates PDF → Extraction → Analysis → Vault Storage
    """
    
    def __init__(self, output_dir="integrated_output"):
        """Initialize workflow components"""
        self.output_dir = output_dir
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize components
        self.pipeline = SmartMedicalReportPipeline(base_output_dir=os.path.join(output_dir, "extractions"))
        self.vault_manager = SmartVaultManager(vault_base_dir=os.path.join(output_dir, "PatientVaults"))
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"✅ Initialized Integrated Workflow")
        print(f"   Session ID: {self.session_id}")
        print(f"   Output Directory: {self.output_dir}")
    
    def process_single_pdf(self, pdf_path: str, generate_insights: bool = True):
        """
        Process a single PDF through the complete workflow
        
        Args:
            pdf_path: Path to PDF file
            generate_insights: Generate summary and recommendations
        
        Returns:
            Dictionary with all processing results
        """
        print_header("🏥 INTEGRATED MEDICAL REPORT WORKFLOW")
        
        if not os.path.exists(pdf_path):
            print(f"❌ Error: PDF file not found: {pdf_path}")
            return None
        
        print(f"📄 Processing: {os.path.basename(pdf_path)}")
        
        results = {
            'pdf_path': pdf_path,
            'pdf_name': Path(pdf_path).stem,
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        # ─────────────────────────────────────────────────────────────
        # STEP 1: PDF EXTRACTION
        # ─────────────────────────────────────────────────────────────
        print_step(1, "PDF Extraction & Data Structuring")
        
        try:
            extraction_result = self.pipeline.process_single_pdf(
                pdf_path=pdf_path,
                keep_csv=False  # Clean up intermediate CSVs
            )
            
            results['extraction'] = extraction_result
            
            print(f"✅ Extraction complete")
            print(f"   Pages: {extraction_result.get('pages', 0)}")
            print(f"   Tests: {extraction_result.get('test_count', 0)}")
            print(f"   JSON files: {len(extraction_result.get('json_files', []))}")
            
            # Get medical report JSON path
            medical_json = None
            for json_file in extraction_result.get('json_files', []):
                if 'medical_report' in json_file:
                    medical_json = json_file
                    break
            
            if not medical_json:
                print("⚠️  Warning: Medical report JSON not found")
                results['status'] = 'partial'
            else:
                results['medical_json'] = medical_json
                
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
            return results
        
        # ─────────────────────────────────────────────────────────────
        # STEP 2: CLINICAL INSIGHTS (Summary & Recommendations)
        # ─────────────────────────────────────────────────────────────
        if generate_insights and CLINICAL_AVAILABLE and medical_json:
            print_step(2, "Clinical Insights Generation")
            
            try:
                # Generate Summary
                print("   Generating clinical summary...")
                summary_output = SummaryModule.main(medical_json)
                if summary_output:
                    results['summary'] = {
                        'status': 'success',
                        'output_file': summary_output
                    }
                    print(f"   ✅ Summary generated: {summary_output}")
                else:
                    print(f"   ⚠️  Summary generation failed")
                
                # Generate Recommendations
                print("   Generating medical recommendations...")
                rec_output = RecommendationModule.main(medical_json)
                if rec_output:
                    results['recommendations'] = {
                        'status': 'success',
                        'output_file': rec_output
                    }
                    print(f"   ✅ Recommendations generated: {rec_output}")
                else:
                    print(f"   ⚠️  Recommendations generation failed")
                    
            except Exception as e:
                print(f"   ⚠️  Clinical insights error: {e}")
                results['insights_error'] = str(e)
        
        # ─────────────────────────────────────────────────────────────
        # STEP 3: PATIENT VAULT SEGREGATION
        # ─────────────────────────────────────────────────────────────
        print_step(3, "Patient Vault Segregation")
        
        try:
            # Process PDF - vault stores only the original PDF
            vault_result = self.vault_manager.process_pdf(pdf_path)
            results['vault'] = vault_result
            
            print(f"✅ Vault assignment complete")
            print(f"   Patient: {vault_result.get('patient_name')}")
            print(f"   Vault: {vault_result.get('vault_dir')}")
            print(f"   New Patient: {vault_result.get('is_new_patient')}")
            print(f"   Total Reports: {vault_result.get('total_reports')}")
            print(f"   📄 Stored: Original PDF only")
            
        except Exception as e:
            print(f"❌ Vault segregation failed: {e}")
            results['vault_error'] = str(e)
        
        # ─────────────────────────────────────────────────────────────
        # FINAL SUMMARY
        # ─────────────────────────────────────────────────────────────
        print_header("✅ WORKFLOW COMPLETE")
        
        print(f"📄 PDF: {results['pdf_name']}")
        
        if results.get('extraction'):
            patient_info = results['extraction'].get('patient_info', {})
            demo = patient_info.get('demographics', {})
            print(f"👤 Patient: {demo.get('name', 'N/A')}")
            print(f"   Age/Gender: {demo.get('age', 'N/A')} / {demo.get('gender', 'N/A')}")
        
        print(f"\n📊 Processing Results:")
        print(f"   ✓ Extraction: {'Success' if results.get('extraction') else 'Failed'}")
        print(f"   ✓ Summary: {'Generated' if results.get('summary') else 'Skipped/Failed'}")
        print(f"   ✓ Recommendations: {'Generated' if results.get('recommendations') else 'Skipped/Failed'}")
        print(f"   ✓ Vault Storage: {'Success' if results.get('vault') else 'Failed'}")
        
        if results.get('vault'):
            print(f"\n📁 Patient Vault: {results['vault'].get('vault_dir')}")
        
        print(f"\n⏱️  Session: {self.session_id}")
        print("="*80 + "\n")
        
        return results
    
    def process_multiple_pdfs(self, pdf_paths: list, generate_insights: bool = True):
        """
        Process multiple PDFs with automatic patient segregation
        
        Args:
            pdf_paths: List of PDF file paths
            generate_insights: Generate summary and recommendations for each
        
        Returns:
            List of processing results
        """
        print_header("🏥 BATCH PROCESSING WORKFLOW")
        print(f"📦 Processing {len(pdf_paths)} PDF(s)\n")
        
        results = []
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            print(f"\n{'='*80}")
            print(f"  [{i}/{len(pdf_paths)}] {os.path.basename(pdf_path)}")
            print(f"{'='*80}\n")
            
            try:
                result = self.process_single_pdf(pdf_path, generate_insights)
                results.append(result)
            except Exception as e:
                print(f"❌ Error processing {pdf_path}: {e}")
                results.append({
                    'pdf_path': pdf_path,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # Display final summary
        self._display_batch_summary(results)
        
        return results
    
    def _display_batch_summary(self, results):
        """Display summary of batch processing"""
        print_header("📊 BATCH PROCESSING SUMMARY")
        
        success_count = sum(1 for r in results if r and r.get('status') == 'success')
        total = len(results)
        
        print(f"Total PDFs: {total}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total - success_count}")
        
        # Patient vault summary
        print(f"\n👥 Patient Vaults Created:")
        patients = self.vault_manager.get_existing_patients()
        for patient in patients:
            print(f"   - {patient['canonical_name']}: {patient['report_count']} report(s)")
        
        print(f"\n📁 Output Location: {self.output_dir}")
        print("="*80 + "\n")
    
    def get_vault_summary(self):
        """Display current vault status"""
        self.vault_manager.display_vault_summary()


def demo_workflow():
    """Demonstration of the integrated workflow"""
    print_header("🎬 INTEGRATED WORKFLOW DEMONSTRATION")
    
    # Initialize workflow
    workflow = IntegratedWorkflow(output_dir="integrated_output")
    
    # Check for sample PDFs
    sample_locations = [
        "demo_data",
        "data",
        "Extraction/pipeline_output"
    ]
    
    sample_pdfs = []
    for location in sample_locations:
        if os.path.exists(location):
            for root, dirs, files in os.walk(location):
                for file in files:
                    if file.endswith('.pdf'):
                        sample_pdfs.append(os.path.join(root, file))
                        if len(sample_pdfs) >= 3:  # Limit to 3 samples
                            break
                if len(sample_pdfs) >= 3:
                    break
    
    if sample_pdfs:
        print(f"Found {len(sample_pdfs)} sample PDF(s):")
        for pdf in sample_pdfs:
            print(f"   - {os.path.basename(pdf)}")
        
        # Process first PDF in detail
        print("\n" + "="*80)
        print("  Processing first PDF with full workflow...")
        print("="*80)
        
        result = workflow.process_single_pdf(
            sample_pdfs[0],
            generate_insights=True
        )
        
        # If multiple PDFs, process them in batch
        if len(sample_pdfs) > 1:
            print("\n\nProcessing remaining PDFs...")
            workflow.process_multiple_pdfs(sample_pdfs[1:], generate_insights=False)
        
        # Show vault summary
        workflow.get_vault_summary()
        
    else:
        print("⚠️  No sample PDFs found in demo_data, data, or Extraction/pipeline_output")
        print("\nTo test the workflow:")
        print("1. Place PDF files in 'demo_data' folder")
        print("2. Run: python test_integrated_workflow.py")
        print("\nOr use the API:")
        print("""
from test_integrated_workflow import IntegratedWorkflow

workflow = IntegratedWorkflow()
result = workflow.process_single_pdf('path/to/report.pdf')
        """)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Integrated Medical Report Workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single PDF
  python test_integrated_workflow.py report.pdf
  
  # Process multiple PDFs
  python test_integrated_workflow.py report1.pdf report2.pdf report3.pdf
  
  # Skip clinical insights
  python test_integrated_workflow.py report.pdf --no-insights
  
  # Run demo with sample data
  python test_integrated_workflow.py --demo
        """
    )
    
    parser.add_argument('pdfs', nargs='*', help='PDF files to process')
    parser.add_argument('--demo', action='store_true', help='Run demo with sample data')
    parser.add_argument('--no-insights', action='store_true', help='Skip summary/recommendations')
    parser.add_argument('--output-dir', type=str, default='integrated_output', 
                       help='Output directory')
    
    args = parser.parse_args()
    
    if args.demo or not args.pdfs:
        demo_workflow()
    else:
        workflow = IntegratedWorkflow(output_dir=args.output_dir)
        
        if len(args.pdfs) == 1:
            workflow.process_single_pdf(
                args.pdfs[0],
                generate_insights=not args.no_insights
            )
        else:
            workflow.process_multiple_pdfs(
                args.pdfs,
                generate_insights=not args.no_insights
            )


if __name__ == "__main__":
    main()
