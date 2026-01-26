"""
CSV to Structured JSON Converter
Handles extracted CSV files and converts them to clean structured JSON
Properly manages spaces, special characters, and data formatting
"""

import pandas as pd
import json
import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime


class CSVToStructuredJSON:
    """
    Converts extracted CSV files to structured JSON format
    Handles data cleaning, formatting, and proper structure
    """
    
    def __init__(self, csv_folder: str):
        """Initialize with folder containing CSV files"""
        if not os.path.exists(csv_folder):
            raise FileNotFoundError(f"CSV folder not found: {csv_folder}")
        self.csv_folder = csv_folder
        
    def clean_text(self, text: Any) -> Optional[str]:
        """Clean text by handling spaces, special chars, and formatting"""
        if pd.isna(text) or text is None:
            return None
        
        text = str(text).strip()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing special characters
        text = text.strip('.,;:-_')
        
        return text if text else None
    
    def extract_key_value(self, text: str) -> Optional[Dict[str, str]]:
        """Extract key-value pairs from text like 'Patient Name : John Doe'"""
        if not text:
            return None
        
        # Common separators: :, -, =
        patterns = [
            r'([^:]+):\s*(.+)',
            r'([^-]+)-\s*(.+)',
            r'([^=]+)=\s*(.+)'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                key = self.clean_text(match.group(1))
                value = self.clean_text(match.group(2))
                if key and value:
                    return {key: value}
        
        return None
    
    def parse_age_gender(self, text: str) -> Dict[str, Any]:
        """Parse age and gender from text like '20 Y / Male' or '20 Years / Male'"""
        result = {'age': None, 'age_unit': None, 'gender': None}
        
        # Pattern 1: number + Years / gender
        match = re.search(r'(\d+)\s*Years?\s*/\s*(Male|Female|M|F)', text, re.IGNORECASE)
        if match:
            result['age'] = int(match.group(1))
            result['age_unit'] = 'YEARS'
            gender = match.group(2).upper()
            result['gender'] = 'Male' if gender in ['M', 'MALE'] else 'Female'
            return result
        
        # Pattern 2: number + unit (Y/M/D) / gender
        match = re.search(r'(\d+)\s*([YMD])\s*/\s*(Male|Female|M|F)', text, re.IGNORECASE)
        if match:
            result['age'] = int(match.group(1))
            result['age_unit'] = match.group(2).upper()
            gender = match.group(3).upper()
            result['gender'] = 'Male' if gender in ['M', 'MALE'] else 'Female'
        
        return result
    
    def parse_date(self, text: str) -> Optional[str]:
        """Parse various date formats and return ISO format"""
        if not text:
            return None
        
        # Common patterns
        patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2}):(\d{2})',  # DD/MM/YYYY HH:MM:SS
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return text  # Return as-is, can be converted to datetime if needed
        
        return text
    
    def parse_reference_range(self, text: str) -> Dict[str, Any]:
        """Parse reference range like '14 - 16' or '< 10' or '10-20'"""
        if not text:
            return {'min': None, 'max': None, 'text': None}
        
        result = {'min': None, 'max': None, 'text': text}
        
        # Pattern: number - number
        match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', text)
        if match:
            result['min'] = float(match.group(1))
            result['max'] = float(match.group(2))
        # Pattern: < number or > number
        elif re.search(r'[<>]\s*(\d+\.?\d*)', text):
            result['text'] = text
        
        return result
    
    def parse_medical_text_content(self, text: str) -> Dict[str, Any]:
        """Parse medical lab report text content into structured data"""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        result = {
            'patient_info': {},
            'test_results': [],
            'doctor_info': {}
        }
        
        current_test = None
        
        for i, line in enumerate(lines):
            # Extract patient information
            if 'Patient Name' in line and ':' in line:
                # Extract name - it's followed by multiple spaces before next field
                match = re.search(r'Patient Name\s*:\s*([A-Za-z][A-Za-z.\s]+?)(?:\s{5,})', line)
                if match:
                    name = self.clean_text(match.group(1))
                    if name and len(name) > 2:
                        result['patient_info']['name'] = name
            
            if 'Age/Gender' in line or 'Age / Gender' in line:
                age_gender = self.parse_age_gender(line)
                if age_gender['age']:
                    result['patient_info'].update(age_gender)
                # Also extract "Years" if present
                if 'Years' in line:
                    result['patient_info']['age_unit'] = 'YEARS'
            
            if 'Billed On' in line and ':' in line:
                match = re.search(r'Billed On\s*:\s*([\d-]+(?:\s+[\d:]+)?)', line)
                if match:
                    result['patient_info']['billed_on'] = self.clean_text(match.group(1))
            
            if 'Collected On' in line and ':' in line:
                match = re.search(r'Collected On\s*:\s*([\d-]+(?:\s+[\d:]+)?)', line)
                if match:
                    result['patient_info']['collected_on'] = self.clean_text(match.group(1))
            
            if 'Reported On' in line and ':' in line:
                match = re.search(r'Reported On\s*:\s*([\d-]+(?:\s+[\d:]+)?)', line)
                if match:
                    result['patient_info']['reported_on'] = self.clean_text(match.group(1))
            
            if 'Sample Id' in line and ':' in line:
                match = re.search(r'Sample Id\s*:\s*(.+?)(?:\s{2,}|$)', line)
                if match:
                    sid = self.clean_text(match.group(1))
                    if sid and sid.strip():
                        result['patient_info']['sample_id'] = sid
            
            if 'Referral' in line and ':' in line:
                match = re.search(r'Referral\s*:\s*(.+?)(?:\s{2,}|$)', line)
                if match:
                    result['patient_info']['referral'] = self.clean_text(match.group(1))
            
            if 'Sample Type' in line and ':' in line:
                match = re.search(r'Sample Type\s*:\s*(.+?)(?:\s{2,}|$)', line)
                if match:
                    result['patient_info']['sample_type'] = self.clean_text(match.group(1))
            
            # Extract doctor information
            if 'Dr.' in line and 'M.D' in line:
                result['doctor_info']['name'] = self.clean_text(line)
            
            if 'Reg no' in line or 'Reg No' in line:
                match = re.search(r'Reg\s+no\s*:\s*(\d+)', line, re.IGNORECASE)
                if match:
                    result['doctor_info']['registration_no'] = match.group(1)
            
            # Parse test results (format: Test Name   Value   Unit   Range   Method)
            # Look for lines with test data pattern
            if not any(skip in line.upper() for skip in ['PACKAGE', 'COMPLETE BLOOD COUNT', 'INDICES', 
                                                          'DIFFERENTIAL', 'ABSOLUTE COUNTS', 'PLATELETS',
                                                          'WHITE BLOOD', 'HAEMOGLOBIN AND RBC',
                                                          'TEST NAME', 'PATIENT NAME', 'AGE/GENDER',
                                                          'CLIENT NAME', 'REFERRAL', 'SAMPLE TYPE',
                                                          'SCAN TO', 'PRINT DATE']):
                
                # Pattern: Test Name [H/L] Value Unit Range Method
                # Split by multiple spaces (2 or more)
                parts = re.split(r'\s{2,}', line)
                
                if len(parts) >= 3:
                    # Check if second part looks like a numeric value (possibly with H/L flag)
                    test_name_part = parts[0].strip()
                    value_part = parts[1].strip() if len(parts) > 1 else ''
                    
                    # Check for test result pattern
                    value_match = re.match(r'([HLhla-z\s]*)\s*([\d.]+)', value_part)
                    
                    if value_match and test_name_part and not test_name_part.startswith('Dr.'):
                        flag = value_match.group(1).strip() if value_match.group(1) else None
                        value = value_match.group(2)
                        
                        test = {
                            'test_name': self.clean_text(test_name_part),
                            'result_value': float(value) if value else None,
                            'result_text': value
                        }
                        
                        if flag and flag.upper() in ['H', 'L', 'HIGH', 'LOW']:
                            test['flag'] = flag.upper()
                            test['abnormal'] = True
                        else:
                            test['abnormal'] = False
                        
                        # Unit
                        if len(parts) > 2:
                            test['unit'] = self.clean_text(parts[2])
                        
                        # Reference range
                        if len(parts) > 3:
                            ref_range = self.parse_reference_range(parts[3])
                            if ref_range['min'] or ref_range['max'] or ref_range['text']:
                                test['reference_range'] = ref_range
                        
                        # Method
                        if len(parts) > 4:
                            test['method'] = self.clean_text(parts[4])
                        
                        result['test_results'].append(test)
        
        return result
    
    def convert_text_csv_to_json(self, csv_path: str) -> Dict[str, Any]:
        """Convert text CSV to structured JSON with medical data parsing"""
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        pages = []
        all_patient_info = {}
        all_test_results = []
        all_doctor_info = {}
        
        for _, row in df.iterrows():
            text_content = row.get('text_content', '')
            
            # Parse medical content from text
            if text_content and isinstance(text_content, str):
                parsed = self.parse_medical_text_content(text_content)
                
                # Merge patient info (first occurrence wins)
                for key, value in parsed['patient_info'].items():
                    if value and key not in all_patient_info:
                        all_patient_info[key] = value
                
                # Collect all test results
                all_test_results.extend(parsed['test_results'])
                
                # Merge doctor info
                for key, value in parsed['doctor_info'].items():
                    if value and key not in all_doctor_info:
                        all_doctor_info[key] = value
            
            page_data = {
                'page_number': int(row['page_number']) if pd.notna(row['page_number']) else None,
                'text_content': self.clean_text(text_content),
                'word_count': int(row['word_count']) if pd.notna(row.get('word_count')) else 0,
                'table_count': int(row['table_count']) if pd.notna(row.get('table_count')) else 0,
                'box_count': int(row['box_count']) if pd.notna(row.get('box_count')) else 0
            }
            pages.append(page_data)
        
        return {
            'type': 'text_extraction',
            'total_pages': len(pages),
            'pages': pages,
            'patient_info': all_patient_info,
            'test_results': all_test_results,
            'doctor_info': all_doctor_info
        }
    
    def convert_tables_csv_to_json(self, csv_path: str) -> Dict[str, Any]:
        """Convert tables CSV to structured JSON with intelligent parsing"""
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # Group by pdf_name, page_number, table_number
        tables = []
        
        if 'pdf_name' in df.columns:
            grouped = df.groupby(['pdf_name', 'page_number', 'table_number'])
            
            for (pdf_name, page_num, table_num), group in grouped:
                table_data = {
                    'pdf_name': str(pdf_name),
                    'page_number': int(page_num),
                    'table_number': int(table_num),
                    'rows': [],
                    'structured_data': {}
                }
                
                # Process each row
                for _, row in group.iterrows():
                    row_data = {}
                    structured_info = {}
                    
                    for col in group.columns:
                        if col not in ['pdf_name', 'page_number', 'table_number']:
                            value = row[col]
                            if pd.notna(value):
                                clean_value = self.clean_text(value)
                                if clean_value:
                                    row_data[col] = clean_value
                                    
                                    # Try to extract key-value pairs
                                    kv = self.extract_key_value(clean_value)
                                    if kv:
                                        structured_info.update(kv)
                                    
                                    # Check for age/gender
                                    if 'age' in col.lower() or 'gender' in col.lower():
                                        age_gender = self.parse_age_gender(clean_value)
                                        if age_gender['age']:
                                            structured_info.update(age_gender)
                    
                    if row_data:
                        table_data['rows'].append(row_data)
                    if structured_info:
                        table_data['structured_data'].update(structured_info)
                
                # Parse medical test results if present
                table_data = self._parse_medical_tests(table_data)
                
                tables.append(table_data)
        
        return {
            'type': 'table_extraction',
            'total_tables': len(tables),
            'tables': tables
        }
    
    def _parse_medical_tests(self, table_data: Dict) -> Dict:
        """Parse medical test results from table data"""
        tests = []
        
        for row in table_data['rows']:
            # Look for test patterns in row data
            test_info = {}
            
            for key, value in row.items():
                value_str = str(value).lower()
                
                # Test name detection
                if any(indicator in key.lower() for indicator in ['test', 'parameter', 'investigation']):
                    test_info['test_name'] = self.clean_text(value)
                
                # Result detection
                elif any(indicator in key.lower() for indicator in ['result', 'value']):
                    # Try to convert to float
                    try:
                        test_info['result_value'] = float(value)
                        test_info['result_text'] = str(value)
                    except:
                        test_info['result_text'] = self.clean_text(value)
                
                # Unit detection
                elif any(indicator in key.lower() for indicator in ['unit', 'uom']):
                    test_info['unit'] = self.clean_text(value)
                
                # Reference range detection
                elif any(indicator in key.lower() for indicator in ['reference', 'range', 'normal']):
                    test_info['reference_range'] = self.parse_reference_range(value)
                
                # Method detection
                elif 'method' in key.lower():
                    test_info['method'] = self.clean_text(value)
                
                # Specimen type
                elif any(indicator in key.lower() for indicator in ['specimen', 'sample']):
                    test_info['specimen'] = self.clean_text(value)
            
            # Also check values for test-like patterns
            for key, value in row.items():
                if not test_info.get('test_name'):
                    # Check if value looks like a test name
                    if value and len(str(value)) > 3 and not str(value).replace('.', '').replace('-', '').isdigit():
                        test_info['test_name'] = self.clean_text(value)
                        break
            
            if test_info and test_info.get('test_name'):
                tests.append(test_info)
        
        if tests:
            table_data['medical_tests'] = tests
        
        return table_data
    
    def convert_boxes_csv_to_json(self, csv_path: str) -> Dict[str, Any]:
        """Convert boxes CSV to structured JSON"""
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        boxes = []
        for _, row in df.iterrows():
            box_data = {
                'page_number': int(row['page_number']) if pd.notna(row['page_number']) else None,
                'coordinates': {
                    'x0': float(row['x0']) if pd.notna(row.get('x0')) else None,
                    'y0': float(row['y0']) if pd.notna(row.get('y0')) else None,
                    'x1': float(row['x1']) if pd.notna(row.get('x1')) else None,
                    'y1': float(row['y1']) if pd.notna(row.get('y1')) else None
                },
                'dimensions': {
                    'width': float(row['width']) if pd.notna(row.get('width')) else None,
                    'height': float(row['height']) if pd.notna(row.get('height')) else None
                }
            }
            boxes.append(box_data)
        
        return {
            'type': 'box_detection',
            'total_boxes': len(boxes),
            'boxes': boxes
        }
    
    def convert_summary_csv_to_json(self, csv_path: str) -> Dict[str, Any]:
        """Convert summary CSV to structured JSON"""
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        if len(df) > 0:
            row = df.iloc[0]
            return {
                'type': 'summary',
                'pdf_name': str(row['pdf_name']) if pd.notna(row.get('pdf_name')) else None,
                'statistics': {
                    'total_pages': int(row['total_pages']) if pd.notna(row.get('total_pages')) else 0,
                    'total_tables': int(row['total_tables']) if pd.notna(row.get('total_tables')) else 0,
                    'total_boxes': int(row['total_boxes']) if pd.notna(row.get('total_boxes')) else 0,
                    'total_words': int(row['total_words']) if pd.notna(row.get('total_words')) else 0
                }
            }
        
        return {'type': 'summary', 'statistics': {}}
    
    def convert_all_to_json(self, output_file: str = None) -> Dict[str, Any]:
        """
        Convert all CSV files in folder to comprehensive structured JSON
        
        Args:
            output_file: Path to save JSON file (optional)
            
        Returns:
            Complete structured JSON data
        """
        result = {
            'extraction_info': {
                'timestamp': datetime.now().isoformat(),
                'source_folder': self.csv_folder
            },
            'data': {}
        }
        
        # Find all CSV files
        csv_files = list(Path(self.csv_folder).glob('*.csv'))
        
        for csv_file in csv_files:
            file_name = csv_file.stem  # filename without extension
            
            try:
                if 'text' in file_name.lower():
                    result['data']['text'] = self.convert_text_csv_to_json(str(csv_file))
                    
                elif 'all_tables' in file_name.lower():
                    result['data']['tables'] = self.convert_tables_csv_to_json(str(csv_file))
                    
                elif 'table_' in file_name.lower():
                    # Individual table files
                    if 'individual_tables' not in result['data']:
                        result['data']['individual_tables'] = []
                    table_data = self.convert_tables_csv_to_json(str(csv_file))
                    result['data']['individual_tables'].append({
                        'file': file_name,
                        'data': table_data
                    })
                    
                elif 'boxes' in file_name.lower() or 'box' in file_name.lower():
                    result['data']['boxes'] = self.convert_boxes_csv_to_json(str(csv_file))
                    
                elif 'summary' in file_name.lower():
                    result['data']['summary'] = self.convert_summary_csv_to_json(str(csv_file))
                    
            except Exception as e:
                print(f"⚠️  Warning: Failed to process {csv_file.name}: {e}")
        
        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Structured JSON saved: {output_file}")
        
        return result
    
    def extract_patient_info_from_text(self, text: str) -> Dict[str, Any]:
        """Extract patient information from raw text content"""
        patient_info = {
            'demographics': {},
            'identifiers': {},
            'dates': {},
            'contact': {}
        }
        
        lines = text.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # Patient Name - extract only the name part before lots of spaces
            if 'Patient Name' in line:
                match = re.search(r'Patient\s+Name\s*:\s*([A-Za-z\s\.]+?)(?:\s{5,}|\s*$)', line)
                if match:
                    patient_info['demographics']['name'] = self.clean_text(match.group(1))
            
            # Age/Gender
            if 'Age/Gender' in line or 'Age / Gender' in line:
                match = re.search(r'Age\s*/\s*Gender\s*:\s*(\d+)\s*(Years?|Yrs?|Y|Months?|M|Days?|D)\s*/\s*(Male|Female|M|F)', line, re.IGNORECASE)
                if match:
                    patient_info['demographics']['age'] = int(match.group(1))
                    patient_info['demographics']['age_unit'] = match.group(2).upper()
                    gender = match.group(3).upper()
                    patient_info['demographics']['gender'] = 'Male' if gender in ['M', 'MALE'] else 'Female'
            
            # Sample ID - look for standalone number on Sample Id line
            if 'Sample Id' in line:
                # Look for number at end of line or after Sample Id
                match = re.search(r'(\d{10,})', line)
                if match:
                    patient_info['identifiers']['sample_id'] = match.group(1)
            
            # Dates - extract only the date part
            if 'Billed On' in line:
                match = re.search(r'Billed\s+On\s*:\s*([\d\-A-Za-z\s:]+?)(?:\s{2,}[A-Z]|\s*$)', line)
                if match:
                    patient_info['dates']['billed'] = self.clean_text(match.group(1))
            
            if 'Collected On' in line:
                match = re.search(r'Collected\s+On\s*:\s*([\d\-A-Za-z\s:]+?)(?:\s{2,}[A-Z]|\s*$)', line)
                if match:
                    patient_info['dates']['collected'] = self.clean_text(match.group(1))
            
            if 'Reported On' in line:
                match = re.search(r'Reported\s+On\s*:\s*([\d\-A-Za-z\s:]+?)(?:\s{2,}[A-Z]|\s*$)', line)
                if match:
                    patient_info['dates']['reported'] = self.clean_text(match.group(1))
            
            # Referral
            if 'Referral' in line_stripped:
                match = re.search(r'Referral\s*:\s*([A-Za-z\s]+?)(?:\s{5,}|\s*$)', line)
                if match:
                    patient_info['contact']['referral'] = self.clean_text(match.group(1))
            
            # Sample Type
            if 'Sample Type' in line:
                match = re.search(r'Sample\s+Type\s*:\s*([A-Za-z\s]+?)(?:\s{5,}|\s*$)', line)
                if match:
                    patient_info['identifiers']['sample_type'] = self.clean_text(match.group(1))
        
        return patient_info
    
    def extract_patient_info(self) -> Dict[str, Any]:
        """Extract structured patient information from all sources"""
        patient_info = {
            'demographics': {},
            'identifiers': {},
            'dates': {},
            'contact': {}
        }
        
        # First extract from text files using the new parser
        text_file = list(Path(self.csv_folder).glob('*_text.csv'))
        if text_file:
            text_data = self.convert_text_csv_to_json(str(text_file[0]))
            parsed_info = text_data.get('patient_info', {})
            
            # Map the parsed data to our structure
            if parsed_info.get('name'):
                patient_info['demographics']['name'] = parsed_info['name']
            if parsed_info.get('age'):
                patient_info['demographics']['age'] = parsed_info['age']
                patient_info['demographics']['age_unit'] = parsed_info.get('age_unit')
            if parsed_info.get('gender'):
                patient_info['demographics']['gender'] = parsed_info['gender']
            
            # Identifiers
            if parsed_info.get('sample_id'):
                patient_info['identifiers']['sample_id'] = parsed_info['sample_id']
            if parsed_info.get('sample_type'):
                patient_info['identifiers']['sample_type'] = parsed_info['sample_type']
            
            # Dates
            if parsed_info.get('billed_on'):
                patient_info['dates']['billed'] = parsed_info['billed_on']
            if parsed_info.get('collected_on'):
                patient_info['dates']['collected'] = parsed_info['collected_on']
            if parsed_info.get('reported_on'):
                patient_info['dates']['reported'] = parsed_info['reported_on']
            
            # Contact
            if parsed_info.get('referral'):
                patient_info['contact']['referral'] = parsed_info['referral']
        
        # Then look for patient data in tables (only if not already set)
        tables_file = list(Path(self.csv_folder).glob('*all_tables.csv'))
        if tables_file:
            tables_data = self.convert_tables_csv_to_json(str(tables_file[0]))
            
            for table in tables_data.get('tables', []):
                structured = table.get('structured_data', {})
                
                # Demographics (only fill if not already set from text)
                if 'Patient Name' in structured and not patient_info['demographics'].get('name'):
                    patient_info['demographics']['name'] = structured['Patient Name']
                if 'age' in structured and not patient_info['demographics'].get('age'):
                    patient_info['demographics']['age'] = structured['age']
                    patient_info['demographics']['age_unit'] = structured.get('age_unit')
                if 'gender' in structured and not patient_info['demographics'].get('gender'):
                    patient_info['demographics']['gender'] = structured['gender']
                
                # Identifiers
                if 'Patient ID' in structured:
                    patient_info['identifiers']['patient_id'] = structured['Patient ID']
                if 'SID No' in structured or 'SID No.' in structured:
                    patient_info['identifiers']['sid'] = structured.get('SID No') or structured.get('SID No.')
                if 'Barcode' in structured:
                    patient_info['identifiers']['barcode'] = structured['Barcode']
                
                # Dates (only if not already set)
                if 'Registered on' in structured and not patient_info['dates'].get('registered'):
                    patient_info['dates']['registered'] = self.parse_date(structured['Registered on'])
                if 'Received on' in structured and not patient_info['dates'].get('received'):
                    patient_info['dates']['received'] = self.parse_date(structured['Received on'])
                if 'Reported on' in structured and not patient_info['dates'].get('reported'):
                    patient_info['dates']['reported'] = self.parse_date(structured['Reported on'])
                
                # Contact
                if 'Mobile No' in structured or 'Mobile No.' in structured:
                    patient_info['contact']['mobile'] = structured.get('Mobile No') or structured.get('Mobile No.')
                if 'Ref.By' in structured:
                    patient_info['contact']['referred_by'] = structured['Ref.By']
        
        return patient_info
    
    def extract_test_results_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract medical test results from raw text content"""
        tests = []
        lines = text.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Skip header lines and section titles
            if any(skip in line_stripped.upper() for skip in [
                'TEST NAME', 'VALUES', 'UNITS', 'REFERENCE RANGE', 'METHOD',
                'COMPLETE BLOOD COUNT', 'HAEMOGLOBIN', 'WHITE BLOOD CELLS',
                'ABSOLUTE COUNTS', 'PLATELETS', 'LIPID PROFILE', 'ENGINEERING COLLEGE',
                'END OF REPORT', 'PRINT DATE', 'DR.', 'M.D.', 'PHD', 'REG NO'
            ]):
                continue
            
            # Pattern 1: Test name with spaces, then value (possibly with H/L flag), then unit, then reference, then method
            # Example: "Haemoglobin (Hb)       14.8       g/dL      13.0 - 17.0  Spectrophotometer"
            # Unit: non-greedy match up to 2+ spaces or digits (start of reference)
            match = re.match(
                r'^([A-Za-z\s\(\)\-\.:]+?)\s{2,}([HL])?\s*(\d+\.?\d*)\s+([\w/%\.\-]+(?:/[\w\.]+ ?\.?mm)?)\s+([\d\.\s\-<>]+?)\s{2,}([A-Za-z].+)$',
                line_stripped
            )
            
            if match:
                test_name = self.clean_text(match.group(1))
                flag = match.group(2)
                value = match.group(3)
                unit = self.clean_text(match.group(4))
                reference = self.clean_text(match.group(5))
                method = self.clean_text(match.group(6))
                
                test = {
                    'test_name': test_name,
                    'result_value': float(value) if value else None,
                    'result_text': value,
                    'unit': unit,
                    'reference_range': self.parse_reference_range(reference),
                    'method': method
                }
                
                if flag:
                    test['flag'] = 'High' if flag == 'H' else 'Low'
                    test['abnormal'] = True
                else:
                    test['abnormal'] = False
                
                tests.append(test)
                continue
            
            # Pattern 2: Without method field
            # Example: "Glucose (Random)               101.80       mg/dL    70 - 140"
            match = re.match(
                r'^([A-Za-z\s\(\)\-\.:]+?)\s{2,}([HL])?\s*(\d+\.?\d*)\s+([\w/%\.\-]+(?:/[\w\.]+ ?\.?mm)?)\s+([\d\.\s\-<>]+)\s*$',
                line_stripped
            )
            
            if match:
                test_name = self.clean_text(match.group(1))
                flag = match.group(2)
                value = match.group(3)
                unit = self.clean_text(match.group(4))
                reference = self.clean_text(match.group(5))
                
                test = {
                    'test_name': test_name,
                    'result_value': float(value) if value else None,
                    'result_text': value,
                    'unit': unit,
                    'reference_range': self.parse_reference_range(reference)
                }
                
                if flag:
                    test['flag'] = 'High' if flag == 'H' else 'Low'
                    test['abnormal'] = True
                else:
                    test['abnormal'] = False
                
                tests.append(test)
        
        return tests
    
    def extract_test_results(self) -> List[Dict[str, Any]]:
        """Extract all medical test results"""
        all_tests = []
        
        # First try to extract from text files using the new parser
        text_file = list(Path(self.csv_folder).glob('*_text.csv'))
        if text_file:
            text_data = self.convert_text_csv_to_json(str(text_file[0]))
            # Get test results from the parsed data
            all_tests.extend(text_data.get('test_results', []))
        
        # Then look for test results in tables as backup
        tables_file = list(Path(self.csv_folder).glob('*all_tables.csv'))
        if tables_file:
            tables_data = self.convert_tables_csv_to_json(str(tables_file[0]))
            
            for table in tables_data.get('tables', []):
                tests = table.get('medical_tests', [])
                # Only add if not duplicate
                for test in tests:
                    test_name = test.get('test_name', '')
                    if test_name and not any(t.get('test_name') == test_name for t in all_tests):
                        all_tests.append(test)
        
        return all_tests
    
    def create_medical_report_json(self, output_file: str = None) -> Dict[str, Any]:
        """
        Create a complete structured medical report JSON
        Specifically designed for medical/lab reports
        """
        report = {
            'report_type': 'medical_lab_report',
            'extraction_timestamp': datetime.now().isoformat(),
            'patient': self.extract_patient_info(),
            'test_results': self.extract_test_results(),
            'metadata': {}
        }
        
        # Add doctor information from text
        text_file = list(Path(self.csv_folder).glob('*_text.csv'))
        if text_file:
            text_data = self.convert_text_csv_to_json(str(text_file[0]))
            doctor_info = text_data.get('doctor_info', {})
            if doctor_info:
                report['doctor'] = doctor_info
        
        # Add summary data
        summary_file = list(Path(self.csv_folder).glob('*summary.csv'))
        if summary_file:
            summary_data = self.convert_summary_csv_to_json(str(summary_file[0]))
            report['metadata'] = summary_data.get('statistics', {})
            report['metadata']['pdf_name'] = summary_data.get('pdf_name')
        
        # Save if output file specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Medical report JSON saved: {output_file}")
        
        return report


def convert_csv_to_json(csv_folder: str, output_file: str = None, 
                       report_type: str = 'complete') -> Dict[str, Any]:
    """
    Convenience function to convert CSV files to structured JSON
    
    Args:
        csv_folder: Folder containing CSV files
        output_file: Path to save JSON file
        report_type: 'complete' for all data, 'medical' for medical report format
        
    Returns:
        Structured JSON data
    """
    converter = CSVToStructuredJSON(csv_folder)
    
    if report_type == 'medical':
        return converter.create_medical_report_json(output_file)
    else:
        return converter.convert_all_to_json(output_file)


# -------------------- MAIN EXECUTION --------------------
if __name__ == "__main__":
    # Example usage
    csv_folder = "C:/Users/slgow/Documents/Projects/Smart-Medical-Analyser/Extraction/output"
    output_folder = "C:/Users/slgow/Documents/Projects/Smart-Medical-Analyser/Extraction/json_output"
    
    try:
        print("🔄 Converting CSV files to structured JSON...")
        print("=" * 70)
        
        converter = CSVToStructuredJSON(csv_folder)
        
        # Create complete structured JSON
        complete_json = os.path.join(output_folder, "complete_structured_data.json")
        complete_data = converter.convert_all_to_json(complete_json)
        
        # Create medical report JSON
        medical_json = os.path.join(output_folder, "medical_report.json")
        medical_data = converter.create_medical_report_json(medical_json)
        
        print("=" * 70)
        print("✅ Conversion completed successfully!")
        print(f"📂 Output folder: {output_folder}")
        print(f"📄 Files created: 2")
        print(f"\n📊 Statistics:")
        print(f"   - Tables processed: {complete_data['data'].get('tables', {}).get('total_tables', 0)}")
        print(f"   - Boxes detected: {complete_data['data'].get('boxes', {}).get('total_boxes', 0)}")
        print(f"   - Test results: {len(medical_data.get('test_results', []))}")
        
        # Display sample patient info
        patient = medical_data.get('patient', {})
        if patient.get('demographics'):
            print(f"\n👤 Patient Info:")
            demo = patient['demographics']
            if demo.get('name'):
                print(f"   - Name: {demo['name']}")
            if demo.get('age'):
                print(f"   - Age: {demo['age']} {demo.get('age_unit', '')}")
            if demo.get('gender'):
                print(f"   - Gender: {demo['gender']}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please ensure the CSV folder path is correct")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
