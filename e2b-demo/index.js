import { Sandbox } from '@e2b/code-interpreter'

// Main async function to run our code
async function main() {
try {
    // Initialize a new sandbox instance
    console.log('Creating sandbox...')
    const sandbox = await Sandbox.create()
    
    // Run some basic Python code
    console.log('Running code examples...')
    
    // Example 1: Basic variable assignment and math
    const result1 = await sandbox.runCode(`
    x = 10
    y = 5
    print(f"Sum: {x + y}")
    `)
    console.log('Example 1 output:', result1.text)
    
    // Example 2: Using Python libraries
    const result2 = await sandbox.runCode(`
    import numpy as np
    array = np.array([1, 2, 3, 4, 5])
    mean = np.mean(array)
    print(f"Mean value: {mean}")
    `)
    console.log('Example 2 output:', result2.text)
    
    // Example 3: Accessing previous variables
    const result3 = await sandbox.runCode(`
    print(f"x is still accessible: {x}")
    `)
    console.log('Example 3 output:', result3.text)
    
    // Clean up: Always close the sandbox when done
    await sandbox.close()
    console.log('Sandbox closed successfully')
    
} catch (error) {
    console.error('An error occurred:', error.message)
    // Ensure sandbox is closed even if an error occurs
    if (sandbox) {
    await sandbox.close()
    }
    process.exit(1)
}
}

// Run the main function
main()

