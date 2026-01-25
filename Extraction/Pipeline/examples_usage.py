"""
Example Usage Scripts for Smart Medical Pipeline
Demonstrates various ways to use the pipeline
"""

import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from smart_pipeline import SmartMedicalPipeline, quick_process, batch_process


# ==================== EXAMPLE 1: Quick Single File Processing ====================
def example_1_quick_single():
    """
    Simplest way to process a single PDF
    Perfect for one-off conversions
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Quick Single File Processing")
    print("="*70)
    
    # Process PDF in one line
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdfs", "Mr. Harish R - M - 20 Yrs.pdf")
    result = quick_process(
        pdf_path=pdf_path,
        output_dir="examples_output"
    )
    
    # Check result
    if result['status'] == 'success':
        print(f"✅ Success!")
        print(f"   Patient: {result['patient_info'].get('demographics', {}).get('name')}")
        print(f"   Tests: {result['test_count']}")
        print(f"   Output: {result['json_dir']}")


# ==================== EXAMPLE 2: Batch Folder Processing ====================
def example_2_batch_folder():
    """
    Process all PDFs in a folder at once
    Great for processing multiple reports
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Batch Folder Processing")
    print("="*70)
    
    # Process entire folder
    pdfs_folder = os.path.join(os.path.dirname(__file__), "..", "pdfs")
    results = batch_process(
        pdf_folder=pdfs_folder,
        output_dir="batch_output"
    )
    
    # Display summary
    print(f"\n📊 Batch Summary:")
    print(f"   Total: {results['total_files']}")
    print(f"   Success: {results['successful']}")
    print(f"   Failed: {results['failed']}")


# ==================== EXAMPLE 3: Advanced Pipeline with Options ====================
def example_3_advanced():
    """
    Advanced usage with custom options
    Full control over processing
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Advanced Pipeline")
    print("="*70)
    
    # Create pipeline with custom output
    pipeline = SmartMedicalPipeline(base_output_dir="advanced_output")
    
    # Process with custom name and keep CSV
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdfs", "Mr. Harish R - M - 20 Yrs.pdf")
    result = pipeline.process_single_pdf(
        pdf_path=pdf_path,
        output_name="patient_harish_20yrs",  # Custom naming
        keep_csv=True  # Keep intermediate CSV files
    )
    
    print(f"\n✅ Processing complete!")
    print(f"   CSV files: {result['csv_dir']}")
    print(f"   JSON files: {result['json_dir']}")


# ==================== EXAMPLE 4: Multiple Specific Files ====================
def example_4_multiple_files():
    """
    Process specific PDFs from different locations
    Useful for selective processing
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Multiple Specific Files")
    print("="*70)
    
    pipeline = SmartMedicalPipeline(base_output_dir="multi_output")
    
    # List of specific PDFs to process
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    pdf_list = [
        os.path.join(base_dir, "pdfs", "Mr. Harish R - M - 20 Yrs.pdf"),
        os.path.join(base_dir, "pdfs", "20415.pdf"),
        # Add more PDFs here
    ]
    
    # Process batch with options
    results = pipeline.process_batch(
        pdf_list=pdf_list,
        keep_csv=False,  # Clean up CSV
        stop_on_error=False  # Continue even if one fails
    )
    
    print(f"\n✅ Batch complete!")
    print(f"   Successful: {results['successful']}/{results['total_files']}")


# ==================== EXAMPLE 5: Read and Analyze Results ====================
def example_5_analyze_results():
    """
    Read JSON results and analyze data
    Extract specific information from processed reports
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Analyze Results")
    print("="*70)
    
    # Process first
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdfs", "Mr. Harish R - M - 20 Yrs.pdf")
    result = quick_process(pdf_path, "analysis_output")
    
    if result['status'] == 'success':
        # Load the medical report JSON
        json_file = result['json_files'][0]  # Medical report
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Analyze patient info
        patient = data['patient']
        print(f"\n👤 Patient Information:")
        print(f"   Name: {patient['demographics']['name']}")
        print(f"   Age: {patient['demographics']['age']} {patient['demographics']['age_unit'].lower()}")
        print(f"   Gender: {patient['demographics']['gender']}")
        
        # Analyze test results
        print(f"\n🧪 Test Results Analysis:")
        test_results = data['test_results']
        
        # Count abnormal tests
        abnormal = [t for t in test_results if t.get('abnormal')]
        print(f"   Total tests: {len(test_results)}")
        print(f"   Abnormal tests: {len(abnormal)}")
        
        # Show abnormal tests
        if abnormal:
            print(f"\n   ⚠️  Abnormal Tests:")
            for test in abnormal:
                print(f"      • {test['test_name']}: {test['result_value']} {test['unit']} ({test['flag']})")
                print(f"        Reference: {test['reference_range']['text']}")


# ==================== EXAMPLE 6: Error Handling ====================
def example_6_error_handling():
    """
    Proper error handling for robust applications
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Error Handling")
    print("="*70)
    
    pipeline = SmartMedicalPipeline()
    
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    pdf_files = [
        os.path.join(base_dir, "pdfs", "valid_file.pdf"),  # May not exist
        os.path.join(base_dir, "pdfs", "Mr. Harish R - M - 20 Yrs.pdf"),  # Valid file
        os.path.join(base_dir, "pdfs", "another_file.pdf"),  # May not exist
    ]
    
    for pdf_path in pdf_files:
        try:
            if not os.path.exists(pdf_path):
                print(f"⚠️  Skipping (not found): {pdf_path}")
                continue
            
            print(f"\n📄 Processing: {os.path.basename(pdf_path)}")
            result = pipeline.process_single_pdf(pdf_path)
            
            if result['status'] == 'success':
                print(f"   ✅ Success: {result['test_count']} tests extracted")
            else:
                print(f"   ❌ Failed: {result['error']}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            continue


# ==================== EXAMPLE 7: Custom Data Extraction ====================
def example_7_custom_extraction():
    """
    Extract specific data fields from results
    Build custom data structures
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Custom Data Extraction")
    print("="*70)
    
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdfs", "Mr. Harish R - M - 20 Yrs.pdf")
    result = quick_process(pdf_path, "custom_output")
    
    if result['status'] == 'success':
        # Load JSON
        json_file = result['json_files'][0]
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Build custom summary
        summary = {
            'patient_id': data['patient']['identifiers'].get('sample_id'),
            'patient_name': data['patient']['demographics']['name'],
            'report_date': data.get('dates', {}).get('reported_on'),
            'test_count': len(data['test_results']),
            'critical_tests': []
        }
        
        # Extract critical (abnormal) tests
        for test in data['test_results']:
            if test.get('abnormal'):
                summary['critical_tests'].append({
                    'name': test['test_name'],
                    'value': test['result_value'],
                    'unit': test['unit'],
                    'flag': test['flag']
                })
        
        # Save custom summary
        custom_file = os.path.join(result['json_dir'], 'custom_summary.json')
        with open(custom_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Custom summary created:")
        print(json.dumps(summary, indent=2))


# ==================== EXAMPLE 8: Integration with Database ====================
def example_8_database_integration():
    """
    Example of storing results in a database
    (Mock implementation - add your DB logic)
    """
    print("\n" + "="*70)
    print("EXAMPLE 8: Database Integration (Mock)")
    print("="*70)
    
    pipeline = SmartMedicalPipeline(base_output_dir="db_output")
    
    # Process PDF
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdfs", "Mr. Harish R - M - 20 Yrs.pdf")
    result = pipeline.process_single_pdf(pdf_path)
    
    if result['status'] == 'success':
        # Load data
        json_file = result['json_files'][0]
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Mock database insert
        print("\n📊 Mock Database Operations:")
        print(f"   INSERT INTO patients ...")
        print(f"      • Patient: {data['patient']['demographics']['name']}")
        
        print(f"   INSERT INTO test_results ...")
        for test in data['test_results'][:3]:  # Show first 3
            print(f"      • {test['test_name']}: {test['result_value']} {test['unit']}")
        
        print(f"   ... and {len(data['test_results']) - 3} more tests")
        print(f"\n   ✅ Database operations completed (mock)")


# ==================== MAIN MENU ====================
def main():
    """Run example demonstrations"""
    print("\n" + "="*70)
    print("🏥 Smart Medical Pipeline - Example Usage")
    print("="*70)
    
    examples = {
        '1': ('Quick Single File', example_1_quick_single),
        '2': ('Batch Folder Processing', example_2_batch_folder),
        '3': ('Advanced Pipeline', example_3_advanced),
        '4': ('Multiple Specific Files', example_4_multiple_files),
        '5': ('Analyze Results', example_5_analyze_results),
        '6': ('Error Handling', example_6_error_handling),
        '7': ('Custom Data Extraction', example_7_custom_extraction),
        '8': ('Database Integration', example_8_database_integration),
        '9': ('Run All Examples', None),
    }
    
    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Exit")
    
    choice = input("\nSelect example (0-9): ").strip()
    
    if choice == '0':
        print("\n👋 Goodbye!\n")
        return
    
    if choice == '9':
        # Run all examples
        for key in range(1, 9):
            examples[str(key)][1]()
            print("\n")
    elif choice in examples and examples[choice][1]:
        examples[choice][1]()
    else:
        print("\n❌ Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
