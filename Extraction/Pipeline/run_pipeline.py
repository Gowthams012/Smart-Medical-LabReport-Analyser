"""
Quick Start Script - Smart Medical Pipeline
Interactive script for easy pipeline execution
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from smart_pipeline import SmartMedicalPipeline, quick_process, batch_process


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("🏥 SMART MEDICAL REPORT ANALYSER")
    print("="*70)
    print("Perfect Pipeline: PDF → CSV → JSON")
    print("="*70 + "\n")


def get_user_choice():
    """Get user's processing choice"""
    print("Choose processing mode:")
    print("  1. Process a single PDF file")
    print("  2. Process multiple PDF files")
    print("  3. Process entire folder")
    print("  4. Quick test with sample PDF")
    print("  5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice in ['1', '2', '3', '4', '5']:
            return choice
        print("❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")


def process_single():
    """Process a single PDF"""
    print("\n" + "-"*70)
    print("Single PDF Processing")
    print("-"*70)
    
    pdf_path = input("\nEnter PDF file path: ").strip().strip('"')
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    keep_csv = input("\nKeep CSV files? (y/n, default: n): ").strip().lower() == 'y'
    
    print(f"\n🚀 Starting pipeline...")
    
    pipeline = SmartMedicalPipeline()
    result = pipeline.process_single_pdf(pdf_path, keep_csv=keep_csv)
    
    if result['status'] == 'success':
        print(f"\n✅ Success! JSON files saved in:")
        print(f"   {result['json_dir']}")
    else:
        print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")


def process_multiple():
    """Process multiple PDFs"""
    print("\n" + "-"*70)
    print("Multiple PDF Processing")
    print("-"*70)
    
    print("\nEnter PDF file paths (one per line, empty line to finish):")
    pdf_list = []
    
    while True:
        path = input().strip().strip('"')
        if not path:
            break
        if os.path.exists(path):
            pdf_list.append(path)
            print(f"   ✓ Added: {os.path.basename(path)}")
        else:
            print(f"   ✗ File not found: {path}")
    
    if not pdf_list:
        print("❌ No valid PDF files provided.")
        return
    
    print(f"\n📊 Total files to process: {len(pdf_list)}")
    
    keep_csv = input("\nKeep CSV files? (y/n, default: n): ").strip().lower() == 'y'
    stop_on_error = input("Stop on first error? (y/n, default: n): ").strip().lower() == 'y'
    
    print(f"\n🚀 Starting batch pipeline...")
    
    pipeline = SmartMedicalPipeline()
    results = pipeline.process_batch(pdf_list, keep_csv=keep_csv, stop_on_error=stop_on_error)
    
    print(f"\n✅ Batch complete!")
    print(f"   Successful: {results['successful']}")
    print(f"   Failed: {results['failed']}")


def process_folder():
    """Process entire folder"""
    print("\n" + "-"*70)
    print("Folder Processing")
    print("-"*70)
    
    folder_path = input("\nEnter folder path: ").strip().strip('"')
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return
    
    # Count PDF files
    pdf_count = len(list(Path(folder_path).glob("*.pdf")))
    
    if pdf_count == 0:
        print(f"❌ No PDF files found in: {folder_path}")
        return
    
    print(f"\n📊 Found {pdf_count} PDF files")
    
    keep_csv = input("\nKeep CSV files? (y/n, default: n): ").strip().lower() == 'y'
    
    confirm = input(f"\nProcess all {pdf_count} files? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return
    
    print(f"\n🚀 Starting folder pipeline...")
    
    pipeline = SmartMedicalPipeline()
    results = pipeline.process_folder(folder_path, keep_csv=keep_csv)
    
    if results.get('status') != 'no_files':
        print(f"\n✅ Folder processing complete!")
        print(f"   Successful: {results['successful']}")
        print(f"   Failed: {results['failed']}")


def quick_test():
    """Quick test with sample PDF"""
    print("\n" + "-"*70)
    print("Quick Test Mode")
    print("-"*70)
    
    # Look for PDFs in common locations
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    search_paths = [
        os.path.join(base_dir, "pdfs"),
        os.path.join(base_dir, "output")
    ]
    
    sample_pdfs = []
    for path in search_paths:
        if os.path.exists(path):
            sample_pdfs.extend(list(Path(path).glob("*.pdf"))[:3])
    
    if not sample_pdfs:
        print("\n❌ No sample PDFs found in common folders.")
        print("   Searched: pdfs/, output/")
        print("\n💡 Tip: Place a PDF file in the 'pdfs' folder")
        return
    
    print("\nFound sample PDFs:")
    for i, pdf in enumerate(sample_pdfs, 1):
        print(f"  {i}. {pdf.name}")
    
    choice = input(f"\nSelect PDF (1-{len(sample_pdfs)}): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(sample_pdfs):
            pdf_path = str(sample_pdfs[idx])
            print(f"\n🚀 Processing: {sample_pdfs[idx].name}")
            result = quick_process(pdf_path, output_dir="quick_test_output")
            
            if result['status'] == 'success':
                print(f"\n✅ Test successful!")
                print(f"   Output: {result['json_dir']}")
        else:
            print("❌ Invalid selection")
    except ValueError:
        print("❌ Invalid input")


def main():
    """Main execution"""
    print_banner()
    
    while True:
        choice = get_user_choice()
        
        if choice == '1':
            process_single()
        elif choice == '2':
            process_multiple()
        elif choice == '3':
            process_folder()
        elif choice == '4':
            quick_test()
        elif choice == '5':
            print("\n👋 Goodbye!\n")
            sys.exit(0)
        
        print("\n" + "="*70)
        cont = input("\nProcess more files? (y/n): ").strip().lower()
        if cont != 'y':
            print("\n👋 Goodbye!\n")
            break
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
