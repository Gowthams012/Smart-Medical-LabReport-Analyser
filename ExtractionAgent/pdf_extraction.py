"""
Advanced PDF to Text/CSV Extractor
Handles tables, boxes, spacing, and layout preservation
"""

import pdfplumber
import pandas as pd
import os
import re
from typing import List, Dict, Optional
from pathlib import Path


class AdvancedPDFExtractor:
    """
    PDF extractor with advanced features:
    - Table detection and extraction
    - Layout preservation
    - Box/rectangle detection
    - Proper spacing handling
    - CSV output with structured data
    """
    
    def __init__(self, pdf_path: str):
        """Initialize the extractor with PDF path"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        self.pdf_path = pdf_path
        self.pdf_name = Path(pdf_path).stem
        
    def extract_text_with_layout(self, page) -> str:
        """Extract text while preserving layout and spacing"""
        try:
            # Extract text with layout preservation
            text = page.extract_text(layout=True)
            if text:
                return text.strip()
            return ""
        except Exception as e:
            print(f"Warning: Layout extraction failed - {e}")
            return page.extract_text() or ""
    
    def extract_tables_from_page(self, page) -> List[pd.DataFrame]:
        """Extract all tables from a page"""
        tables = []
        try:
            page_tables = page.extract_tables()
            for table_data in page_tables:
                if table_data and len(table_data) > 0:
                    # Convert to DataFrame
                    headers = table_data[0] if table_data[0] else None
                    
                    # Handle duplicate column names
                    if headers:
                        seen = {}
                        unique_headers = []
                        for col in headers:
                            col_str = str(col) if col is not None else 'Column'
                            if col_str in seen:
                                seen[col_str] += 1
                                unique_headers.append(f"{col_str}_{seen[col_str]}")
                            else:
                                seen[col_str] = 0
                                unique_headers.append(col_str)
                        df = pd.DataFrame(table_data[1:], columns=unique_headers)
                    else:
                        df = pd.DataFrame(table_data[1:])
                    
                    # Clean empty columns and rows
                    df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
                    if not df.empty:
                        tables.append(df)
        except Exception as e:
            print(f"Warning: Table extraction failed - {e}")
        return tables
    
    def detect_boxes_and_rectangles(self, page) -> List[Dict]:
        """Detect boxes and rectangles in the page"""
        rectangles = []
        try:
            # Get all rectangles/boxes
            rects = page.rects
            for rect in rects:
                rectangles.append({
                    'x0': rect['x0'],
                    'y0': rect['y0'],
                    'x1': rect['x1'],
                    'y1': rect['y1'],
                    'width': rect['width'],
                    'height': rect['height']
                })
        except Exception as e:
            print(f"Warning: Rectangle detection failed - {e}")
        return rectangles
    
    def extract_all_text(self) -> Dict[str, any]:
        """
        Extract all content from PDF
        Returns a dictionary with pages, text, tables, and metadata
        """
        result = {
            'pdf_name': self.pdf_name,
            'total_pages': 0,
            'pages': []
        }
        
        with pdfplumber.open(self.pdf_path) as pdf:
            result['total_pages'] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, start=1):
                page_data = {
                    'page_number': page_num,
                    'text': '',
                    'tables': [],
                    'rectangles': [],
                    'word_count': 0
                }
                
                # Extract text with layout
                text = self.extract_text_with_layout(page)
                page_data['text'] = text
                page_data['word_count'] = len(text.split()) if text else 0
                
                # Extract tables
                tables = self.extract_tables_from_page(page)
                page_data['tables'] = tables
                page_data['table_count'] = len(tables)
                
                # Detect rectangles/boxes
                rectangles = self.detect_boxes_and_rectangles(page)
                page_data['rectangles'] = rectangles
                page_data['box_count'] = len(rectangles)
                
                result['pages'].append(page_data)
        
        return result
    
    def extract_to_csv(self, output_dir: str = None, 
                      separate_tables: bool = True) -> Dict[str, str]:
        """
        Extract PDF content and save to CSV files
        
        Args:
            output_dir: Directory to save CSV files (default: same as PDF)
            separate_tables: If True, save each table as separate CSV
            
        Returns:
            Dictionary with paths to created CSV files
        """
        if output_dir is None:
            output_dir = os.path.dirname(self.pdf_path)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract all content
        content = self.extract_all_text()
        output_files = {}
        
        # 1. Create main text CSV (page-by-page)
        text_data = []
        for page in content['pages']:
            text_data.append({
                'page_number': page['page_number'],
                'text_content': page['text'],
                'word_count': page['word_count'],
                'table_count': page['table_count'],
                'box_count': page['box_count']
            })
        
        text_df = pd.DataFrame(text_data)
        text_csv_path = os.path.join(output_dir, f"{self.pdf_name}_text.csv")
        text_df.to_csv(text_csv_path, index=False, encoding='utf-8-sig')
        output_files['text_csv'] = text_csv_path
        print(f"✅ Text CSV saved: {text_csv_path}")
        
        # 2. Extract and save all tables
        all_tables = []
        table_count = 0
        
        for page in content['pages']:
            for table_idx, table_df in enumerate(page['tables']):
                table_count += 1
                
                # Add metadata columns
                table_df.insert(0, 'pdf_name', self.pdf_name)
                table_df.insert(1, 'page_number', page['page_number'])
                table_df.insert(2, 'table_number', table_idx + 1)
                
                if separate_tables:
                    # Save each table separately
                    table_csv_path = os.path.join(
                        output_dir, 
                        f"{self.pdf_name}_table_p{page['page_number']}_t{table_idx + 1}.csv"
                    )
                    table_df.to_csv(table_csv_path, index=False, encoding='utf-8-sig')
                    output_files[f'table_{table_count}'] = table_csv_path
                    print(f"✅ Table CSV saved: {table_csv_path}")
                
                all_tables.append(table_df)
        
        # 3. Save combined tables CSV
        if all_tables:
            combined_tables_df = pd.concat(all_tables, ignore_index=True)
            combined_csv_path = os.path.join(output_dir, f"{self.pdf_name}_all_tables.csv")
            combined_tables_df.to_csv(combined_csv_path, index=False, encoding='utf-8-sig')
            output_files['all_tables_csv'] = combined_csv_path
            print(f"✅ Combined tables CSV saved: {combined_csv_path}")
        
        # 4. Save boxes/rectangles information
        boxes_data = []
        for page in content['pages']:
            for rect in page['rectangles']:
                boxes_data.append({
                    'page_number': page['page_number'],
                    'x0': rect['x0'],
                    'y0': rect['y0'],
                    'x1': rect['x1'],
                    'y1': rect['y1'],
                    'width': rect['width'],
                    'height': rect['height']
                })
        
        if boxes_data:
            boxes_df = pd.DataFrame(boxes_data)
            boxes_csv_path = os.path.join(output_dir, f"{self.pdf_name}_boxes.csv")
            boxes_df.to_csv(boxes_csv_path, index=False, encoding='utf-8-sig')
            output_files['boxes_csv'] = boxes_csv_path
            print(f"✅ Boxes CSV saved: {boxes_csv_path}")
        
        # 5. Create summary CSV
        summary_data = {
            'pdf_name': [self.pdf_name],
            'total_pages': [content['total_pages']],
            'total_tables': [table_count],
            'total_boxes': [len(boxes_data)],
            'total_words': [sum(page['word_count'] for page in content['pages'])]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_csv_path = os.path.join(output_dir, f"{self.pdf_name}_summary.csv")
        summary_df.to_csv(summary_csv_path, index=False, encoding='utf-8-sig')
        output_files['summary_csv'] = summary_csv_path
        print(f"✅ Summary CSV saved: {summary_csv_path}")
        
        return output_files


def extract_pdf_to_csv(pdf_path: str, output_dir: str = None, 
                       separate_tables: bool = True) -> Dict[str, str]:
    """
    Convenience function to extract PDF content to CSV files
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory for CSV files
        separate_tables: Whether to save tables separately
        
    Returns:
        Dictionary with paths to created files
    """
    extractor = AdvancedPDFExtractor(pdf_path)
    return extractor.extract_to_csv(output_dir, separate_tables)


# -------------------- MAIN EXECUTION --------------------
if __name__ == "__main__":
    # Example usage
    pdf_path = "C:\\Users\\slgow\\Documents\\Projects\\Smart-Medical-Analyser\\Extraction\\pdfs\python Pipeline/smart_pipeline.py --pdf \Mr. Harish R - M - 20 Yrs.pdf"
    output_dir = "C:/Users/slgow/Documents/Projects/Smart-Medical-Analyser/Extraction/output"
    
    try:
        print(f"🔍 Processing PDF: {pdf_path}")
        print("=" * 60)
        
        # Create extractor
        extractor = AdvancedPDFExtractor(pdf_path)
        
        # Extract to CSV
        output_files = extractor.extract_to_csv(
            output_dir=output_dir,
            separate_tables=True
        )
        
        print("=" * 60)
        print(f"✅ Extraction completed successfully!")
        print(f"📂 Output directory: {output_dir}")
        print(f"📄 Total files created: {len(output_files)}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please update the pdf_path variable with a valid PDF file path")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
