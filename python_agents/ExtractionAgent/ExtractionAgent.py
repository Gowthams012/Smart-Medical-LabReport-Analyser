"""
Perfect Pipeline - Smart Medical Report Analyser
Complete end-to-end pipeline: PDF → CSV → JSON
Efficient, robust, and production-ready
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add paths for imports
sys.path.insert(0, os.path.dirname(__file__))

from pdf_extraction import AdvancedPDFExtractor
from data_structuring import CSVToStructuredJSON


class SmartMedicalReportPipeline:
    """
    Complete pipeline for medical report processing
    PDF → CSV → Structured JSON
    """
    
    def __init__(self, base_output_dir: str = "pipeline_output"):
        """Initialize pipeline with output directory"""
        self.base_output_dir = base_output_dir
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def process_single_pdf(self, 
                          pdf_path: str,
                          output_name: str = None,
                          keep_csv: bool = False) -> Dict[str, any]:
        """
        Process a single PDF through the complete pipeline
        
        Args:
            pdf_path: Path to PDF file
            output_name: Optional custom output name
            keep_csv: Whether to keep intermediate CSV files (default: False)
            
        Returns:
            Dictionary with results and paths
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        pdf_name = Path(pdf_path).stem
        if output_name:
            pdf_name = output_name
        
        # Create output directories
        session_dir = os.path.join(self.base_output_dir, self.session_id, pdf_name)
        csv_dir = os.path.join(session_dir, "csv")
        json_dir = os.path.join(session_dir, "json")
        
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(json_dir, exist_ok=True)
        
        results = {
            'pdf_path': pdf_path,
            'pdf_name': pdf_name,
            'session_id': self.session_id,
            'status': 'success',
            'csv_dir': csv_dir,
            'json_dir': json_dir,
            'csv_files': [],
            'json_files': [],
            'patient_info': {},
            'test_count': 0,
            'pages': 0,
            'error': None
        }
        
        try:
            # STEP 1: Extract PDF to CSV
            print(f"\n{'='*70}")
            print(f"Processing: {pdf_name}")
            print(f"{'='*70}")
            print(f"\n[1/3] 📄 Extracting PDF to CSV...")
            
            extractor = AdvancedPDFExtractor(pdf_path)
            csv_files = extractor.extract_to_csv(
                output_dir=csv_dir,
                separate_tables=True
            )
            
            results['csv_files'] = list(csv_files.values())
            results['pages'] = len([f for f in csv_files.keys() if 'text' in f])
            
            print(f"      ✅ Created {len(csv_files)} CSV files")
            print(f"      📊 Pages extracted: {results['pages']}")
            
            # STEP 2: Convert CSV to JSON
            print(f"\n[2/3] 🔄 Converting CSV to Structured JSON...")
            
            converter = CSVToStructuredJSON(csv_dir)
            
            # Medical report JSON
            medical_json_path = os.path.join(json_dir, f"{pdf_name}_medical_report.json")
            medical_data = converter.create_medical_report_json(medical_json_path)
            results['json_files'].append(medical_json_path)
            
            # Complete structured JSON
            complete_json_path = os.path.join(json_dir, f"{pdf_name}_complete_data.json")
            complete_data = converter.convert_all_to_json(complete_json_path)
            results['json_files'].append(complete_json_path)
            
            # Extract summary information
            results['patient_info'] = medical_data.get('patient', {})
            results['test_count'] = len(medical_data.get('test_results', []))
            
            print(f"      ✅ Created {len(results['json_files'])} JSON files")
            print(f"      🧪 Test results: {results['test_count']}")
            
            # STEP 3: Cleanup (if requested)
            if not keep_csv:
                print(f"\n[3/3] 🧹 Cleaning up CSV files...")
                shutil.rmtree(csv_dir)
                results['csv_dir'] = None
                results['csv_files'] = []
                print(f"      ✅ CSV files cleaned up")
            else:
                print(f"\n[3/3] 💾 Keeping CSV files in: {csv_dir}")
            
            # Display summary
            print(f"\n{'='*70}")
            print(f"✅ PIPELINE COMPLETED SUCCESSFULLY")
            print(f"{'='*70}")
            
            demo = results['patient_info'].get('demographics', {})
            print(f"\n📋 Patient: {demo.get('name', 'N/A')}")
            print(f"   Age/Gender: {demo.get('age', 'N/A')} {demo.get('age_unit', '').lower() if demo.get('age_unit') else ''} / {demo.get('gender', 'N/A')}")
            
            print(f"\n📂 Output Location:")
            print(f"   Session: {session_dir}")
            print(f"   JSON files: {json_dir}")
            
            print(f"\n📄 Generated Files:")
            for json_file in results['json_files']:
                print(f"   ✓ {os.path.basename(json_file)}")
            
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = str(e)
            print(f"\n❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
        
        return results
    
    def process_batch(self,
                     pdf_list: List[str],
                     keep_csv: bool = False,
                     stop_on_error: bool = False) -> Dict[str, any]:
        """
        Process multiple PDFs in batch
        
        Args:
            pdf_list: List of PDF file paths
            keep_csv: Whether to keep intermediate CSV files
            stop_on_error: Whether to stop processing on first error
            
        Returns:
            Dictionary with batch results
        """
        print(f"\n{'='*70}")
        print(f"BATCH PROCESSING - {len(pdf_list)} PDF FILES")
        print(f"{'='*70}")
        print(f"Session ID: {self.session_id}")
        print(f"Output Directory: {self.base_output_dir}/{self.session_id}")
        
        batch_results = {
            'session_id': self.session_id,
            'total_files': len(pdf_list),
            'successful': 0,
            'failed': 0,
            'results': [],
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }
        
        for i, pdf_path in enumerate(pdf_list, 1):
            print(f"\n{'='*70}")
            print(f"[{i}/{len(pdf_list)}] Processing: {os.path.basename(pdf_path)}")
            print(f"{'='*70}")
            
            try:
                result = self.process_single_pdf(pdf_path, keep_csv=keep_csv)
                batch_results['results'].append(result)
                
                if result['status'] == 'success':
                    batch_results['successful'] += 1
                else:
                    batch_results['failed'] += 1
                    if stop_on_error:
                        print(f"\n⚠️  Stopping batch processing due to error")
                        break
                        
            except Exception as e:
                batch_results['failed'] += 1
                batch_results['results'].append({
                    'pdf_path': pdf_path,
                    'status': 'failed',
                    'error': str(e)
                })
                print(f"\n❌ Failed to process {pdf_path}: {e}")
                
                if stop_on_error:
                    print(f"\n⚠️  Stopping batch processing due to error")
                    break
        
        batch_results['end_time'] = datetime.now().isoformat()
        
        # Save batch summary
        summary_path = os.path.join(self.base_output_dir, self.session_id, "batch_summary.json")
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(batch_results, f, indent=2, ensure_ascii=False)
        
        # Display batch summary
        print(f"\n{'='*70}")
        print(f"BATCH PROCESSING COMPLETE")
        print(f"{'='*70}")
        print(f"\n📊 Summary:")
        print(f"   Total files: {batch_results['total_files']}")
        print(f"   Successful: {batch_results['successful']}")
        print(f"   Failed: {batch_results['failed']}")
        print(f"\n📄 Batch summary saved: {summary_path}")
        
        return batch_results
    
    def process_folder(self,
                      folder_path: str,
                      pattern: str = "*.pdf",
                      keep_csv: bool = False) -> Dict[str, any]:
        """
        Process all PDFs in a folder
        
        Args:
            folder_path: Path to folder containing PDFs
            pattern: File pattern to match (default: *.pdf)
            keep_csv: Whether to keep intermediate CSV files
            
        Returns:
            Dictionary with batch results
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        # Find all PDF files
        pdf_files = list(Path(folder_path).glob(pattern))
        
        if not pdf_files:
            print(f"⚠️  No PDF files found in {folder_path}")
            return {'status': 'no_files', 'folder': folder_path}
        
        print(f"\n📁 Found {len(pdf_files)} PDF files in: {folder_path}")
        
        # Process batch
        return self.process_batch([str(f) for f in pdf_files], keep_csv=keep_csv)


def quick_process(pdf_path: str, output_dir: str = "quick_output") -> Dict:
    """
    Quick convenience function to process a single PDF
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory (default: quick_output)
        
    Returns:
        Dictionary with results
    """
    pipeline = SmartMedicalPipeline(base_output_dir=output_dir)
    return pipeline.process_single_pdf(pdf_path, keep_csv=False)


def batch_process(pdf_folder: str, output_dir: str = "batch_output") -> Dict:
    """
    Quick convenience function to process all PDFs in a folder
    
    Args:
        pdf_folder: Path to folder containing PDFs
        output_dir: Output directory (default: batch_output)
        
    Returns:
        Dictionary with batch results
    """
    pipeline = SmartMedicalPipeline(base_output_dir=output_dir)
    return pipeline.process_folder(pdf_folder, keep_csv=False)


# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Smart Medical Report Analyser - Complete Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single PDF
  python smart_pipeline.py --pdf "path/to/report.pdf"
  
  # Process multiple PDFs
  python smart_pipeline.py --pdf "report1.pdf" "report2.pdf" "report3.pdf"
  
  # Process entire folder
  python smart_pipeline.py --folder "path/to/pdfs"
  
  # Keep CSV files
  python smart_pipeline.py --pdf "report.pdf" --keep-csv
  
  # Custom output directory
  python smart_pipeline.py --pdf "report.pdf" --output "my_output"
        """
    )
    
    parser.add_argument('--pdf', nargs='+', help='PDF file(s) to process')
    parser.add_argument('--folder', help='Folder containing PDF files')
    parser.add_argument('--output', default='pipeline_output', help='Output directory (default: pipeline_output)')
    parser.add_argument('--keep-csv', action='store_true', help='Keep intermediate CSV files')
    parser.add_argument('--stop-on-error', action='store_true', help='Stop batch processing on first error')
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = SmartMedicalPipeline(base_output_dir=args.output)
    
    # Process based on arguments
    if args.folder:
        # Process entire folder
        results = pipeline.process_folder(args.folder, keep_csv=args.keep_csv)
        
    elif args.pdf:
        # Process one or more PDFs
        if len(args.pdf) == 1:
            # Single PDF
            results = pipeline.process_single_pdf(args.pdf[0], keep_csv=args.keep_csv)
        else:
            # Multiple PDFs
            results = pipeline.process_batch(args.pdf, keep_csv=args.keep_csv, 
                                           stop_on_error=args.stop_on_error)
    else:
        # No input provided - show help
        parser.print_help()
        print("\n" + "="*70)
        print("No input provided. Use --pdf or --folder to specify input.")
        print("="*70)
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print("✅ PIPELINE EXECUTION COMPLETE")
    print(f"{'='*70}\n")
