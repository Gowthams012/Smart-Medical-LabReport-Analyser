"""
Integration Test Suite for Smart Medical Pipeline
Tests all components to ensure everything works correctly
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from smart_pipeline import SmartMedicalPipeline, quick_process, batch_process


class PipelineTestSuite:
    """Test suite for the medical pipeline"""
    
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        result = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append((test_name, passed, message))
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        
        print(f"{result} | {test_name}")
        if message:
            print(f"       {message}")
    
    def test_imports(self):
        """Test 1: Check all imports work"""
        try:
            from pdf_extraction.text_extraction import AdvancedPDFExtractor
            from data_structuring.ConvertrawDataStrutured import CSVToStructuredJSON
            self.log_test("Import Test", True, "All modules imported successfully")
            return True
        except Exception as e:
            self.log_test("Import Test", False, f"Import error: {e}")
            return False
    
    def test_pdf_exists(self):
        """Test 2: Check sample PDF exists"""
        pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdfs", "Mr. Harish R - M - 20 Yrs.pdf")
        exists = os.path.exists(pdf_path)
        
        if exists:
            self.log_test("PDF Existence Test", True, f"Found: {pdf_path}")
        else:
            self.log_test("PDF Existence Test", False, f"Missing: {pdf_path}")
        
        return exists
    
    def test_single_processing(self):
        """Test 3: Single PDF processing"""
        try:
            pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdfs", "Mr. Harish R - M - 20 Yrs.pdf")
            result = quick_process(
                pdf_path=pdf_path,
                output_dir="test_output"
            )
            
            if result['status'] == 'success':
                # Validate output
                checks = [
                    (len(result['json_files']) == 2, "2 JSON files created"),
                    (result['test_count'] > 0, f"{result['test_count']} tests extracted"),
                    (os.path.exists(result['json_dir']), "Output directory exists"),
                ]
                
                all_passed = all(check[0] for check in checks)
                details = ", ".join(check[1] for check in checks if check[0])
                
                self.log_test("Single Processing Test", all_passed, details)
                return all_passed
            else:
                self.log_test("Single Processing Test", False, f"Processing failed: {result.get('error')}")
                return False
                
        except Exception as e:
            self.log_test("Single Processing Test", False, f"Exception: {e}")
            return False
    
    def test_json_structure(self):
        """Test 4: Validate JSON structure"""
        try:
            # Load the medical report JSON
            json_path = Path("test_output").rglob("*_medical_report.json")
            json_file = next(json_path, None)
            
            if not json_file:
                self.log_test("JSON Structure Test", False, "No JSON file found")
                return False
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check required fields
            required_fields = [
                ('report_type' in data, "report_type field"),
                ('patient' in data, "patient field"),
                ('test_results' in data, "test_results field"),
                ('metadata' in data, "metadata field"),
            ]
            
            # Check patient structure
            if 'patient' in data:
                required_fields.extend([
                    ('demographics' in data['patient'], "patient.demographics"),
                    ('name' in data['patient'].get('demographics', {}), "patient name"),
                ])
            
            # Check test results
            if 'test_results' in data and len(data['test_results']) > 0:
                test = data['test_results'][0]
                required_fields.extend([
                    ('test_name' in test, "test.test_name"),
                    ('result_value' in test, "test.result_value"),
                    ('reference_range' in test, "test.reference_range"),
                ])
            
            all_passed = all(field[0] for field in required_fields)
            passed_count = sum(1 for field in required_fields if field[0])
            
            self.log_test(
                "JSON Structure Test", 
                all_passed, 
                f"{passed_count}/{len(required_fields)} fields validated"
            )
            return all_passed
            
        except Exception as e:
            self.log_test("JSON Structure Test", False, f"Exception: {e}")
            return False
    
    def test_patient_data(self):
        """Test 5: Validate patient data extraction"""
        try:
            json_path = Path("test_output").rglob("*_medical_report.json")
            json_file = next(json_path, None)
            
            if not json_file:
                self.log_test("Patient Data Test", False, "No JSON file found")
                return False
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            patient = data.get('patient', {})
            demographics = patient.get('demographics', {})
            
            # Check specific values for the test PDF
            checks = [
                (demographics.get('name') == "Mr. Harish R", "Name: Mr. Harish R"),
                (demographics.get('age') == 20, "Age: 20"),
                (demographics.get('gender') == "Male", "Gender: Male"),
            ]
            
            all_passed = all(check[0] for check in checks)
            details = ", ".join(check[1] for check in checks if check[0])
            
            self.log_test("Patient Data Test", all_passed, details)
            return all_passed
            
        except Exception as e:
            self.log_test("Patient Data Test", False, f"Exception: {e}")
            return False
    
    def test_test_results(self):
        """Test 6: Validate test results extraction"""
        try:
            json_path = Path("test_output").rglob("*_medical_report.json")
            json_file = next(json_path, None)
            
            if not json_file:
                self.log_test("Test Results Test", False, "No JSON file found")
                return False
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            test_results = data.get('test_results', [])
            
            if not test_results:
                self.log_test("Test Results Test", False, "No test results found")
                return False
            
            # Validate first test result structure
            first_test = test_results[0]
            checks = [
                ('test_name' in first_test and first_test['test_name'], "Test name present"),
                ('result_value' in first_test, "Result value present"),
                ('unit' in first_test, "Unit present"),
                ('reference_range' in first_test, "Reference range present"),
                (isinstance(first_test.get('result_value'), (int, float)), "Numeric result"),
            ]
            
            # Check for abnormal flag detection
            abnormal_tests = [t for t in test_results if t.get('abnormal')]
            checks.append((True, f"{len(test_results)} tests, {len(abnormal_tests)} abnormal"))
            
            all_passed = all(check[0] for check in checks)
            details = ", ".join(check[1] for check in checks if check[0])
            
            self.log_test("Test Results Test", all_passed, details)
            return all_passed
            
        except Exception as e:
            self.log_test("Test Results Test", False, f"Exception: {e}")
            return False
    
    def test_cleanup(self):
        """Test 7: Verify cleanup functionality"""
        try:
            # Process with CSV cleanup (default)
            pdf_path = os.path.join(os.path.dirname(__file__), "..", "pdfs", "Mr. Harish R - M - 20 Yrs.pdf")
            result = quick_process(
                pdf_path=pdf_path,
                output_dir="cleanup_test"
            )
            
            if result['status'] == 'success':
                # Check that CSV dir is None (cleaned up)
                csv_cleaned = result['csv_dir'] is None
                json_exists = os.path.exists(result['json_dir'])
                
                all_passed = csv_cleaned and json_exists
                details = "CSV cleaned, JSON preserved" if all_passed else "Cleanup issue"
                
                self.log_test("Cleanup Test", all_passed, details)
                return all_passed
            else:
                self.log_test("Cleanup Test", False, "Processing failed")
                return False
                
        except Exception as e:
            self.log_test("Cleanup Test", False, f"Exception: {e}")
            return False
    
    def test_error_handling(self):
        """Test 8: Error handling for invalid input"""
        try:
            pipeline = SmartMedicalPipeline(base_output_dir="error_test")
            
            # Try processing non-existent file
            result = pipeline.process_single_pdf("nonexistent.pdf")
            
            # Should return error status
            error_handled = result['status'] == 'failed' and result['error'] is not None
            
            self.log_test("Error Handling Test", error_handled, "Invalid input handled correctly")
            return error_handled
            
        except FileNotFoundError:
            # Exception is also acceptable
            self.log_test("Error Handling Test", True, "FileNotFoundError raised correctly")
            return True
        except Exception as e:
            self.log_test("Error Handling Test", False, f"Unexpected exception: {e}")
            return False
    
    def cleanup_test_outputs(self):
        """Clean up test output directories"""
        import shutil
        test_dirs = ["test_output", "cleanup_test", "error_test"]
        
        for dir_name in test_dirs:
            if os.path.exists(dir_name):
                try:
                    shutil.rmtree(dir_name)
                except Exception as e:
                    print(f"⚠️  Could not remove {dir_name}: {e}")
    
    def run_all_tests(self, cleanup=True):
        """Run all tests and display summary"""
        print("\n" + "="*70)
        print("🧪 SMART MEDICAL PIPELINE - TEST SUITE")
        print("="*70 + "\n")
        
        # Run tests in order
        tests = [
            self.test_imports,
            self.test_pdf_exists,
            self.test_single_processing,
            self.test_json_structure,
            self.test_patient_data,
            self.test_test_results,
            self.test_cleanup,
            self.test_error_handling,
        ]
        
        for test in tests:
            test()
            print()
        
        # Display summary
        print("="*70)
        print(f"📊 TEST SUMMARY")
        print("="*70)
        print(f"   Total Tests: {self.passed + self.failed}")
        print(f"   Passed: {self.passed} ✅")
        print(f"   Failed: {self.failed} ❌")
        print(f"   Success Rate: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print("="*70)
        
        # Cleanup
        if cleanup:
            print("\n🧹 Cleaning up test directories...")
            self.cleanup_test_outputs()
            print("✅ Cleanup complete")
        
        # Final verdict
        print("\n" + "="*70)
        if self.failed == 0:
            print("🎉 ALL TESTS PASSED - PIPELINE READY FOR PRODUCTION!")
        else:
            print(f"⚠️  {self.failed} TEST(S) FAILED - REVIEW REQUIRED")
        print("="*70 + "\n")
        
        return self.failed == 0


def main():
    """Main test execution"""
    suite = PipelineTestSuite()
    
    try:
        all_passed = suite.run_all_tests(cleanup=True)
        sys.exit(0 if all_passed else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
