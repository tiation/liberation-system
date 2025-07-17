#!/usr/bin/env node

/**
 * 🚀 Liberation System Integration Test Suite
 * 
 * Enterprise-grade integration testing with dark neon theme console output
 * Tests all major components and their interactions
 * 
 * @author Tiation
 * @version 1.0.0
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const { performance } = require('perf_hooks');

class IntegrationTestRunner {
    constructor() {
        this.tests = [];
        this.results = [];
        this.startTime = null;
        this.endTime = null;
        this.colors = {
            reset: '\x1b[0m',
            bright: '\x1b[1m',
            dim: '\x1b[2m',
            
            // Dark neon theme colors
            cyan: '\x1b[96m',
            magenta: '\x1b[95m',
            yellow: '\x1b[93m',
            green: '\x1b[92m',
            red: '\x1b[91m',
            blue: '\x1b[94m',
            
            // Backgrounds
            bgBlack: '\x1b[40m',
            bgCyan: '\x1b[106m',
            bgMagenta: '\x1b[105m'
        };
        
        this.setupTests();
    }

    setupTests() {
        this.tests = [
            {
                name: 'Frontend Build & Type Check',
                command: 'npm run build && npm run type-check',
                timeout: 120000,
                critical: true
            },
            {
                name: 'Unit Tests',
                command: 'npm test -- --coverage --watchAll=false',
                timeout: 60000,
                critical: true
            },
            {
                name: 'Lint & Format Check',
                command: 'npm run lint && npm run format',
                timeout: 30000,
                critical: false
            },
            {
                name: 'E2E Tests',
                command: 'npm run e2e',
                timeout: 180000,
                critical: true
            },
            {
                name: 'Performance Analysis',
                command: 'npm run analyze',
                timeout: 90000,
                critical: false
            },
            {
                name: 'Python Integration Tests',
                command: 'python3 test_integration.py',
                timeout: 120000,
                critical: true
            }
        ];
    }

    log(message, color = 'cyan', style = '') {
        const colorCode = this.colors[color] || this.colors.cyan;
        const styleCode = this.colors[style] || '';
        const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
        
        console.log(`${styleCode}${colorCode}[${timestamp}] ${message}${this.colors.reset}`);
    }

    logHeader(title) {
        const line = '═'.repeat(60);
        const padding = ' '.repeat(Math.max(0, 60 - title.length - 2));
        
        console.log(`\n${this.colors.bright}${this.colors.cyan}╔${line}╗${this.colors.reset}`);
        console.log(`${this.colors.bright}${this.colors.cyan}║ ${title}${padding}║${this.colors.reset}`);
        console.log(`${this.colors.bright}${this.colors.cyan}╚${line}╝${this.colors.reset}\n`);
    }

    logSuccess(message) {
        this.log(`✅ ${message}`, 'green', 'bright');
    }

    logError(message) {
        this.log(`❌ ${message}`, 'red', 'bright');
    }

    logWarning(message) {
        this.log(`⚠️  ${message}`, 'yellow', 'bright');
    }

    logInfo(message) {
        this.log(`ℹ️  ${message}`, 'blue');
    }

    async runCommand(command, timeout = 30000) {
        return new Promise((resolve, reject) => {
            const startTime = performance.now();
            
            this.log(`Executing: ${command}`, 'magenta');
            
            const child = spawn(command, { 
                shell: true,
                stdio: ['pipe', 'pipe', 'pipe'],
                cwd: process.cwd()
            });

            let stdout = '';
            let stderr = '';

            child.stdout.on('data', (data) => {
                stdout += data.toString();
                // Show real-time output for important commands
                if (command.includes('test') || command.includes('build')) {
                    process.stdout.write(data);
                }
            });

            child.stderr.on('data', (data) => {
                stderr += data.toString();
                // Show errors in real-time
                process.stderr.write(data);
            });

            const timeoutId = setTimeout(() => {
                child.kill('SIGTERM');
                reject(new Error(`Command timed out after ${timeout}ms`));
            }, timeout);

            child.on('close', (code) => {
                clearTimeout(timeoutId);
                const endTime = performance.now();
                const duration = Math.round(endTime - startTime);
                
                if (code === 0) {
                    resolve({ stdout, stderr, duration, success: true });
                } else {
                    reject(new Error(`Command failed with exit code ${code}\nStdout: ${stdout}\nStderr: ${stderr}`));
                }
            });

            child.on('error', (error) => {
                clearTimeout(timeoutId);
                reject(error);
            });
        });
    }

    async runTest(test) {
        const testStart = performance.now();
        
        try {
            this.log(`🧪 Starting: ${test.name}`, 'cyan', 'bright');
            
            const result = await this.runCommand(test.command, test.timeout);
            const testEnd = performance.now();
            const duration = Math.round(testEnd - testStart);
            
            this.logSuccess(`${test.name} completed in ${duration}ms`);
            
            return {
                name: test.name,
                success: true,
                duration: duration,
                output: result.stdout,
                critical: test.critical
            };
            
        } catch (error) {
            const testEnd = performance.now();
            const duration = Math.round(testEnd - testStart);
            
            this.logError(`${test.name} failed after ${duration}ms: ${error.message}`);
            
            return {
                name: test.name,
                success: false,
                duration: duration,
                error: error.message,
                critical: test.critical
            };
        }
    }

    async runAllTests() {
        this.logHeader('🚀 LIBERATION SYSTEM INTEGRATION TESTS');
        
        this.logInfo('Testing enterprise-grade liberation system components...');
        this.logInfo(`Total tests to run: ${this.tests.length}`);
        
        this.startTime = performance.now();
        
        // Run tests sequentially to avoid resource conflicts
        for (const test of this.tests) {
            const result = await this.runTest(test);
            this.results.push(result);
            
            // Add a small delay between tests
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        this.endTime = performance.now();
        
        this.generateReport();
    }

    generateReport() {
        const totalDuration = Math.round(this.endTime - this.startTime);
        const passed = this.results.filter(r => r.success).length;
        const failed = this.results.filter(r => !r.success).length;
        const criticalFailed = this.results.filter(r => !r.success && r.critical).length;
        
        this.logHeader('📊 INTEGRATION TEST RESULTS');
        
        // Summary statistics
        this.log(`Total Tests: ${this.results.length}`, 'cyan');
        this.log(`Passed: ${passed}`, 'green');
        this.log(`Failed: ${failed}`, failed > 0 ? 'red' : 'green');
        this.log(`Critical Failures: ${criticalFailed}`, criticalFailed > 0 ? 'red' : 'green');
        this.log(`Total Duration: ${totalDuration}ms`, 'blue');
        this.log(`Success Rate: ${((passed / this.results.length) * 100).toFixed(1)}%`, 'magenta');
        
        console.log('\n' + this.colors.cyan + '─'.repeat(60) + this.colors.reset);
        
        // Detailed results
        this.results.forEach(result => {
            const status = result.success ? '✅' : '❌';
            const criticalBadge = result.critical ? '[CRITICAL]' : '[OPTIONAL]';
            const color = result.success ? 'green' : 'red';
            
            this.log(`${status} ${result.name} ${criticalBadge} - ${result.duration}ms`, color);
            
            if (!result.success && result.error) {
                this.log(`   Error: ${result.error.split('\n')[0]}`, 'red', 'dim');
            }
        });
        
        // Generate detailed report file
        this.generateDetailedReport();
        
        // Final status
        console.log('\n' + this.colors.bright + this.colors.cyan + '═'.repeat(60) + this.colors.reset);
        
        if (criticalFailed === 0) {
            this.logSuccess('🎉 ALL CRITICAL TESTS PASSED! Liberation System is ready for deployment.');
        } else {
            this.logError(`💥 ${criticalFailed} critical test(s) failed! System not ready for deployment.`);
        }
        
        console.log(this.colors.bright + this.colors.cyan + '═'.repeat(60) + this.colors.reset + '\n');
        
        // Exit with appropriate code
        process.exit(criticalFailed > 0 ? 1 : 0);
    }

    generateDetailedReport() {
        const reportPath = path.join(process.cwd(), 'integration-test-report.json');
        
        const report = {
            timestamp: new Date().toISOString(),
            summary: {
                total: this.results.length,
                passed: this.results.filter(r => r.success).length,
                failed: this.results.filter(r => !r.success).length,
                criticalFailed: this.results.filter(r => !r.success && r.critical).length,
                totalDuration: Math.round(this.endTime - this.startTime),
                successRate: ((this.results.filter(r => r.success).length / this.results.length) * 100).toFixed(1)
            },
            results: this.results.map(result => ({
                name: result.name,
                success: result.success,
                duration: result.duration,
                critical: result.critical,
                error: result.error || null,
                hasOutput: !!result.output
            })),
            environment: {
                node: process.version,
                platform: process.platform,
                arch: process.arch,
                cwd: process.cwd()
            }
        };
        
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        this.logInfo(`Detailed report saved to: ${reportPath}`);
    }

    async checkPrerequisites() {
        this.logHeader('🔍 CHECKING PREREQUISITES');
        
        const checks = [
            { name: 'Node.js', command: 'node --version' },
            { name: 'npm', command: 'npm --version' },
            { name: 'Python', command: 'python3 --version' },
            { name: 'Git', command: 'git --version' }
        ];
        
        for (const check of checks) {
            try {
                const result = await this.runCommand(check.command, 5000);
                this.logSuccess(`${check.name}: ${result.stdout.trim()}`);
            } catch (error) {
                this.logWarning(`${check.name}: Not found or failed`);
            }
        }
        
        // Check if package.json exists
        if (fs.existsSync('package.json')) {
            this.logSuccess('package.json found');
        } else {
            this.logError('package.json not found - make sure you are in the project root');
            process.exit(1);
        }
        
        // Check if Python integration test exists
        if (fs.existsSync('test_integration.py')) {
            this.logSuccess('Python integration test found');
        } else {
            this.logWarning('Python integration test not found - skipping Python tests');
            this.tests = this.tests.filter(t => t.name !== 'Python Integration Tests');
        }
    }
}

// Main execution
async function main() {
    const runner = new IntegrationTestRunner();
    
    try {
        await runner.checkPrerequisites();
        await runner.runAllTests();
    } catch (error) {
        runner.logError(`Integration test runner failed: ${error.message}`);
        process.exit(1);
    }
}

// Handle process signals
process.on('SIGINT', () => {
    console.log('\n🛑 Integration tests interrupted by user');
    process.exit(130);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Integration tests terminated');
    process.exit(143);
});

// Run if called directly
if (require.main === module) {
    main();
}

module.exports = { IntegrationTestRunner };
