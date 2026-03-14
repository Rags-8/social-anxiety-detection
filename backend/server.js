const { spawn } = require('child_process');

/**
 * Social Anxiety Backend Wrapper
 * This script allows running the Python FastAPI backend using 'node server.js'
 */

console.log('\x1b[36m%s\x1b[0m', 'Starting Social Anxiety Backend...');
console.log('\x1b[33m%s\x1b[0m', 'Running at this portal: http://localhost:8001');

// Execute the Python command with -u for unbuffered output
const port = process.env.PORT || '8001';
const pythonProcess = spawn('python', ['-u', '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', port, '--reload'], {
    shell: true
});

let dbConnectedShown = false;

// Stream stdout
pythonProcess.stdout.on('data', (data) => {
    const output = data.toString();
    process.stdout.write(output);

    // Check for database initialization message from Python
    if (output.includes('Database initialized successfully') && !dbConnectedShown) {
        console.log('\x1b[32m%s\x1b[0m', 'Status: Connected to database');
        dbConnectedShown = true;
    }
});

// Stream stderr (Uvicorn often sends logs here)
pythonProcess.stderr.on('data', (data) => {
    const output = data.toString();
    process.stderr.write(output);

    // Fallback: If startup is complete, assume DB is connected (since init_db is in startup_event)
    if (output.includes('Application startup complete') && !dbConnectedShown) {
        console.log('\x1b[32m%s\x1b[0m', 'Status: Connected to database');
        dbConnectedShown = true;
    }

    // Some logs might contain the database message in stderr depending on environment
    if (output.includes('Database initialized successfully') && !dbConnectedShown) {
        console.log('\x1b[32m%s\x1b[0m', 'Status: Connected to database');
        dbConnectedShown = true;
    }
});

pythonProcess.on('close', (code) => {
    if (code !== 0 && code !== null) {
        console.log('\x1b[31m%s\x1b[0m', `Backend process exited with code ${code}`);
        console.log('Ensure Python and required dependencies are installed.');
    }
});

pythonProcess.on('error', (err) => {
    console.error('\x1b[31m%s\x1b[0m', 'Failed to start Python backend:');
    console.error(err);
    console.log('\nPlease ensure Python is in your PATH and dependencies are installed via:');
    console.log('pip install -r requirements.txt');
});
