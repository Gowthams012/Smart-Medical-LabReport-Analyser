/**
 * Agent Service - Python Agent Integration
 * =========================================
 * Correct workflow:
 * 1. ExtractionAgent: PDF → JSON (medical data)
 * 2. InsightAgent: JSON → Summary + Recommendations
 * 3. VaultAgent: PDF → Patient segregation
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;
const fsSync = require('fs');

class AgentService {
    constructor() {
        this.projectRoot = path.join(__dirname, '../..');
        this.pythonCmd = 'python';
    }

    /**
     * Run Python script and capture output
     */
    _runPythonScript(scriptPath, args = [], options = {}) {
        return new Promise((resolve, reject) => {
            const python = spawn(this.pythonCmd, [scriptPath, ...args], {
                cwd: options.cwd || this.projectRoot,
                env: { 
                    ...process.env, 
                    PYTHONUNBUFFERED: '1',
                    PYTHONIOENCODING: 'utf-8',  // Fix Windows encoding issues
                    GOOGLE_GEMINI_API_KEY: process.env.GOOGLE_GEMINI_API_KEY  // Pass API key to Python
                }
            });

            let stdout = '';
            let stderr = '';

            python.stdout.on('data', (data) => {
                const output = data.toString();
                stdout += output;
                if (options.verbose) console.log(output);
            });

            python.stderr.on('data', (data) => {
                const output = data.toString();
                stderr += output;
                if (options.verbose) console.error(output);
            });

            python.on('close', (code) => {
                if (code !== 0) {
                    reject(new Error(`Python script failed: ${stderr || stdout}`));
                } else {
                    resolve(stdout);
                }
            });

            python.on('error', (err) => {
                reject(new Error(`Failed to start Python: ${err.message}`));
            });
        });
    }

    /**
     * Run inline Python code
     */
    _runPythonCode(code, options = {}) {
        return this._runPythonScript('-c', [code], options);
    }

    /**
     * VaultAgent - Identify patient and segregate PDF
     * Uses SmartVaultManager to process and store PDF by patient name
     */
    async processWithVaultAgent(pdfPath) {
        try {
            console.log('🔍 VaultAgent: Identifying patient and segregating...');
            
            const code = `
import sys
import os

# Change to project root so relative paths work
os.chdir('${this.projectRoot.replace(/\\/g, '/')}')

sys.path.insert(0, '${this.projectRoot.replace(/\\/g, '/')}/ValutAgent')
from ValutAgent import SmartVaultManager
import json

try:
    vault = SmartVaultManager('integrated_output/PatientVaults')
    result = vault.process_pdf('${pdfPath.replace(/\\/g, '/')}')
    print(f"OUTPUT_JSON:{json.dumps(result)}")
except Exception as e:
    import traceback
    print(f"ERROR:{traceback.format_exc()}")
`;

            const output = await this._runPythonCode(code, { verbose: true });
            
            // Parse output
            if (output.includes('ERROR:')) {
                const error = output.split('ERROR:')[1].trim();
                throw new Error(error);
            }
            
            if (!output.includes('OUTPUT_JSON:')) {
                throw new Error('No JSON data returned from VaultAgent');
            }
            
            const jsonLine = output.split('OUTPUT_JSON:')[1].trim().split('\n')[0];
            const result = JSON.parse(jsonLine);
            
            console.log(`✅ Patient identified: ${result.patient_name}`);
            console.log(`   Vault: ${result.vault_dir}`);
            console.log(`   New patient: ${result.is_new_patient}`);
            
            return result;
        } catch (error) {
            console.error('❌ VaultAgent error:', error.message);
            throw new Error(`Patient identification failed: ${error.message}`);
        }
    }

    /**
     * ExtractionAgent - Extract medical data from PDF
     * Uses SmartMedicalReportPipeline.process_single_pdf()
     * Returns JSON path which contains all extracted medical data
     */
    async extractData(pdfPath) {
        try {
            console.log('🔬 ExtractionAgent: Extracting medical data...');
            
            const code = `
import sys
import os

# Change to project root so relative paths work
os.chdir('${this.projectRoot.replace(/\\/g, '/')}')

sys.path.insert(0, '${this.projectRoot.replace(/\\/g, '/')}/ExtractionAgent')
from ExtractionAgent import SmartMedicalReportPipeline
import json

try:
    pipeline = SmartMedicalReportPipeline(base_output_dir='integrated_output/extractions')
    result = pipeline.process_single_pdf('${pdfPath.replace(/\\/g, '/')}', keep_csv=False)
    
    output_data = {
        'json_dir': result['json_dir'],
        'medical_json': result['json_files'][0] if result['json_files'] else None,
        'patient_info': result.get('patient_info', {}),
        'test_count': result.get('test_count', 0)
    }
    print(f"OUTPUT_JSON:{json.dumps(output_data)}")
except Exception as e:
    import traceback
    print(f"ERROR:{traceback.format_exc()}")
`;

            const output = await this._runPythonCode(code, { verbose: true });
            
            // Parse output
            if (output.includes('ERROR:')) {
                const error = output.split('ERROR:')[1].trim();
                throw new Error(error);
            }
            
            if (!output.includes('OUTPUT_JSON:')) {
                throw new Error('No JSON data returned from ExtractionAgent');
            }
            
            const jsonLine = output.split('OUTPUT_JSON:')[1].trim().split('\n')[0];
            const result = JSON.parse(jsonLine);
            
            // Read the medical report JSON file
            if (!result.medical_json) {
                throw new Error('No medical JSON generated');
            }
            
            const jsonPath = path.join(this.projectRoot, result.medical_json);
            if (!fsSync.existsSync(jsonPath)) {
                throw new Error(`JSON file not found: ${jsonPath}`);
            }
            
            const extractedData = JSON.parse(await fs.readFile(jsonPath, 'utf-8'));
            
            console.log('✅ Data extraction complete');
            console.log(`   Tests found: ${result.test_count}`);
            console.log(`   Patient: ${result.patient_info.name || 'Unknown'}`);
            console.log(`   JSON: ${result.medical_json}`);
            
            return {
                data: extractedData,
                jsonPath: result.medical_json,
                patientInfo: result.patient_info,
                testCount: result.test_count
            };
        } catch (error) {
            console.error('❌ ExtractionAgent error:', error.message);
            throw new Error(`Data extraction failed: ${error.message}`);
        }
    }

    /**
     * SummaryAgent - Generate clinical summary
     * Calls Summary.py with JSON file path
     * Takes JSON file path as input (not JSON data)
     * Calls Summary.main() which returns output file path
     */
    async generateSummary(jsonFilePath) {
        try {
            console.log('📝 SummaryAgent: Generating clinical summary...');
            
            // Convert to absolute path
            const absoluteJsonPath = path.isAbsolute(jsonFilePath) 
                ? jsonFilePath 
                : path.join(this.projectRoot, jsonFilePath);
            
            const code = `
import sys
import os

# Change to project root so relative paths work
os.chdir('${this.projectRoot.replace(/\\/g, '/')}')

sys.path.insert(0, '${this.projectRoot.replace(/\\/g, '/')}/InsightAgent')
import Summary

try:
    output_file = Summary.main('${absoluteJsonPath.replace(/\\/g, '/')}')
    if output_file:
        # Convert to absolute path
        if not os.path.isabs(output_file):
            output_file = os.path.abspath(output_file)
        print(f"OUTPUT_FILE:{output_file}")
    else:
        print("ERROR:Summary generation returned None")
except Exception as e:
    import traceback
    print(f"ERROR:{traceback.format_exc()}")
`;

            const output = await this._runPythonCode(code, { verbose: true });
            
            // Parse output
            if (output.includes('ERROR:')) {
                const error = output.split('ERROR:')[1].trim();
                throw new Error(error);
            }
            
            if (!output.includes('OUTPUT_FILE:')) {
                throw new Error('No output file path returned from Summary agent');
            }
            
            const outputFilePath = output.split('OUTPUT_FILE:')[1].trim().split('\n')[0];
            
            if (!fsSync.existsSync(outputFilePath)) {
                throw new Error(`Summary file not found at: ${outputFilePath}`);
            }
            
            const summary = await fs.readFile(outputFilePath, 'utf-8');
            
            console.log('✅ Summary generated');
            console.log(`   File: ${path.relative(this.projectRoot, outputFilePath)}`);
            
            return {
                text: summary,
                filePath: outputFilePath
            };
        } catch (error) {
            console.error('❌ SummaryAgent error:', error.message);
            throw new Error(`Summary generation failed: ${error.message}`);
        }
    }

    /**
     * RecommendationAgent - Generate medical recommendations
     * Takes JSON file path as input (not JSON data)
     * Calls Recommendation.main() which returns output file path
     */
    async generateRecommendations(jsonFilePath) {
        try {
            console.log('💊 RecommendationAgent: Generating recommendations...');
            
            // Convert to absolute path
            const absoluteJsonPath = path.isAbsolute(jsonFilePath) 
                ? jsonFilePath 
                : path.join(this.projectRoot, jsonFilePath);
            
            const code = `
import sys
import os

# Change to project root so relative paths work
os.chdir('${this.projectRoot.replace(/\\/g, '/')}')

sys.path.insert(0, '${this.projectRoot.replace(/\\/g, '/')}/InsightAgent')
import Recommendation

try:
    output_file = Recommendation.main('${absoluteJsonPath.replace(/\\/g, '/')}')
    if output_file:
        # Convert to absolute path
        if not os.path.isabs(output_file):
            output_file = os.path.abspath(output_file)
        print(f"OUTPUT_FILE:{output_file}")
    else:
        print("ERROR:Recommendation generation returned None")
except Exception as e:
    import traceback
    print(f"ERROR:{traceback.format_exc()}")
`;

            const output = await this._runPythonCode(code, { verbose: true });
            
            // Parse output
            if (output.includes('ERROR:')) {
                const error = output.split('ERROR:')[1].trim();
                throw new Error(error);
            }
            
            if (!output.includes('OUTPUT_FILE:')) {
                throw new Error('No output file path returned from Recommendation agent');
            }
            
            const outputFilePath = output.split('OUTPUT_FILE:')[1].trim().split('\n')[0];
            
            if (!outputFilePath || !fsSync.existsSync(outputFilePath)) {
                throw new Error(`Recommendation file not found: ${outputFilePath}`);
            }
            
            const recommendations = await fs.readFile(outputFilePath, 'utf-8');
            
            console.log('✅ Recommendations generated');
            console.log(`   File: ${path.relative(this.projectRoot, outputFilePath)}`);
            
            return {
                text: recommendations,
                filePath: outputFilePath
            };
        } catch (error) {
            console.error('❌ RecommendationAgent error:', error.message);
            throw new Error(`Recommendation generation failed: ${error.message}`);
        }
    }

    /**
     * Process complete workflow
     * Correct flow:
     * 1. Extract data (ExtractionAgent) - PDF → JSON
     * 2. Generate insights (InsightAgent) - JSON → Summary + Recommendations
     * 3. Segregate by patient (VaultAgent) - PDF → PatientVault
     */
    async processComplete(pdfPath) {
        console.log('\n🚀 Starting complete processing pipeline...');
        console.log(`   PDF: ${pdfPath}\n`);

        try {
            // Step 1: Extract medical data from PDF
            const extractionResult = await this.extractData(pdfPath);
            
            // Step 2: Generate insights in parallel using the JSON file path
            console.log('\n⚡ Running Summary & Recommendation agents in parallel...');
            const [summaryResult, recommendationResult] = await Promise.all([
                this.generateSummary(extractionResult.jsonPath),
                this.generateRecommendations(extractionResult.jsonPath)
            ]);
            
            // Step 3: Segregate PDF into patient vault
            const vaultResult = await this.processWithVaultAgent(pdfPath);
            
            console.log('\n✅ Complete pipeline finished successfully!\n');
            
            return {
                patientName: vaultResult.patient_name || extractionResult.patientInfo.name,
                vaultPath: vaultResult.vault_dir,
                extractedData: extractionResult.data,
                jsonPath: extractionResult.jsonPath,
                testCount: extractionResult.testCount,
                summary: summaryResult.text,
                summaryFile: summaryResult.filePath,
                recommendations: recommendationResult.text,
                recommendationsFile: recommendationResult.filePath,
                isNewPatient: vaultResult.is_new_patient,
                totalReports: vaultResult.total_reports || 1,
                metadata: extractionResult.metadata,
                status: 'success'
            };
        } catch (error) {
            console.error('\n❌ Pipeline failed:', error.message);
            throw error;
        }
    }
}

module.exports = new AgentService();
