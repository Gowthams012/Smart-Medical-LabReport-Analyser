/**
 * Test Script - Verify Backend Integration
 * =========================================
 * Quick test to ensure all components work together
 */

const agentService = require('./services/agentService');
const path = require('path');

async function testAgentIntegration() {
    console.log('🧪 Testing Agent Integration\n');
    console.log('=' .repeat(80));
    
    // Find a sample PDF in data/pdfs
    const pdfDir = path.join(__dirname, '../data/pdfs');
    const fs = require('fs');
    
    if (!fs.existsSync(pdfDir)) {
        console.log('❌ data/pdfs directory not found');
        console.log('   Please create it and add a sample medical report PDF');
        return;
    }
    
    const pdfs = fs.readdirSync(pdfDir).filter(f => f.endsWith('.pdf'));
    
    if (pdfs.length === 0) {
        console.log('❌ No PDF files found in data/pdfs');
        console.log('   Please add a sample medical report PDF for testing');
        return;
    }
    
    const pdfPath = path.join(pdfDir, pdfs[0]);
    console.log(`\n📄 Testing with: ${pdfs[0]}\n`);
    
    try {
        // Test complete pipeline
        const result = await agentService.processComplete(pdfPath);
        
        console.log('\n' + '='.repeat(80));
        console.log('✅ INTEGRATION TEST SUCCESSFUL');
        console.log('='.repeat(80));
        console.log('\nResults:');
        console.log(`   Patient: ${result.patientName}`);
        console.log(`   Tests Found: ${result.metadata.testCount}`);
        console.log(`   Summary Length: ${result.summary.length} chars`);
        console.log(`   Recommendations Length: ${result.recommendations.length} chars`);
        console.log(`\n   Output Files:`);
        console.log(`   - JSON: ${result.metadata.jsonPath}`);
        console.log(`   - Vault: ${result.vaultPath}`);
        console.log('\n✅ All agents working correctly!\n');
        
    } catch (error) {
        console.error('\n' + '='.repeat(80));
        console.error('❌ INTEGRATION TEST FAILED');
        console.error('='.repeat(80));
        console.error(`\nError: ${error.message}\n`);
        process.exit(1);
    }
}

// Run if called directly
if (require.main === module) {
    testAgentIntegration()
        .then(() => process.exit(0))
        .catch(err => {
            console.error('Test failed:', err);
            process.exit(1);
        });
}

module.exports = testAgentIntegration;
