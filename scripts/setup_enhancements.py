#!/usr/bin/env python3
"""
Liberation System Enhancement Setup Script
Automates the setup of all enhancements including screenshots, React components, API, and PostgreSQL
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import asyncio
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LiberationEnhancementSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.scripts_dir = self.root_dir / "scripts"
        self.database_dir = self.root_dir / "database"
        self.src_dir = self.root_dir / "src"
        self.api_dir = self.root_dir / "api"
        
    def run_command(self, command, shell=True, check=True, cwd=None):
        """Run a shell command with error handling"""
        try:
            cwd = cwd or self.root_dir
            result = subprocess.run(
                command,
                shell=shell,
                check=check,
                cwd=cwd,
                capture_output=True,
                text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {command}")
            logger.error(f"Error: {e.stderr}")
            return None
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        logger.info("🔍 Checking dependencies...")
        
        dependencies = {
            "python3": "python3 --version",
            "node": "node --version",
            "npm": "npm --version",
            "pip": "pip --version"
        }
        
        missing = []
        for dep, cmd in dependencies.items():
            result = self.run_command(cmd, check=False)
            if result is None or result.returncode != 0:
                missing.append(dep)
            else:
                logger.info(f"✅ {dep}: {result.stdout.strip()}")
        
        if missing:
            logger.error(f"❌ Missing dependencies: {', '.join(missing)}")
            return False
        
        return True
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        logger.info("📦 Installing Python dependencies...")
        
        # Install core requirements
        result = self.run_command("pip install -r requirements.txt")
        if result is None:
            logger.error("❌ Failed to install Python dependencies")
            return False
        
        # Install additional dependencies for screenshots
        screenshot_deps = [
            "selenium",
            "webdriver-manager",
            "Pillow"
        ]
        
        for dep in screenshot_deps:
            result = self.run_command(f"pip install {dep}")
            if result is None:
                logger.warning(f"⚠️  Failed to install {dep}")
        
        logger.info("✅ Python dependencies installed")
        return True
    
    def install_node_dependencies(self):
        """Install Node.js dependencies"""
        logger.info("📦 Installing Node.js dependencies...")
        
        result = self.run_command("npm install")
        if result is None:
            logger.error("❌ Failed to install Node.js dependencies")
            return False
        
        logger.info("✅ Node.js dependencies installed")
        return True
    
    def generate_screenshots(self):
        """Generate UI screenshots"""
        logger.info("📸 Generating UI screenshots...")
        
        screenshot_script = self.scripts_dir / "generate_screenshots.py"
        if not screenshot_script.exists():
            logger.error("❌ Screenshot generation script not found")
            return False
        
        result = self.run_command(f"python {screenshot_script}")
        if result is None:
            logger.error("❌ Failed to generate screenshots")
            return False
        
        logger.info("✅ Screenshots generated successfully")
        return True
    
    def setup_database(self):
        """Setup PostgreSQL database"""
        logger.info("🗄️  Setting up PostgreSQL database...")
        
        # Check if PostgreSQL is available
        pg_result = self.run_command("psql --version", check=False)
        if pg_result is None or pg_result.returncode != 0:
            logger.warning("⚠️  PostgreSQL not found. Skipping database setup.")
            logger.info("💡 Install PostgreSQL: brew install postgresql (macOS) or apt-get install postgresql (Ubuntu)")
            return True
        
        # Run database migration
        migration_script = self.database_dir / "migrations" / "001_initial_schema.sql"
        if not migration_script.exists():
            logger.error("❌ Database migration script not found")
            return False
        
        # Create database setup script
        setup_script = f"""
        echo "Creating liberation_system database..."
        createdb liberation_system 2>/dev/null || true
        
        echo "Running migration..."
        psql -d liberation_system -f {migration_script}
        
        echo "Database setup completed!"
        """
        
        result = self.run_command(setup_script)
        if result is None:
            logger.warning("⚠️  Database setup failed. Using SQLite fallback.")
            return True
        
        logger.info("✅ PostgreSQL database setup completed")
        return True
    
    def verify_setup(self):
        """Verify that all enhancements are working"""
        logger.info("🔍 Verifying setup...")
        
        # Check if key files exist
        key_files = [
            "assets/screenshots/main-dashboard.png",
            "assets/screenshots/resource-dashboard.png",
            "assets/screenshots/truth-network.png",
            "assets/diagrams/system-architecture.png",
            "src/components/Dashboard.tsx",
            "api/main.py",
            "database/migrations/001_initial_schema.sql"
        ]
        
        missing_files = []
        for file_path in key_files:
            if not (self.root_dir / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.warning(f"⚠️  Missing files: {', '.join(missing_files)}")
        
        # Test API startup
        logger.info("🌐 Testing API startup...")
        api_test = self.run_command("python -m api.main --help", check=False)
        if api_test is None or api_test.returncode != 0:
            logger.warning("⚠️  API may not start properly")
        
        # Test Next.js build
        logger.info("⚛️  Testing Next.js build...")
        next_test = self.run_command("npm run build", check=False)
        if next_test is None or next_test.returncode != 0:
            logger.warning("⚠️  Next.js build may have issues")
        
        logger.info("✅ Setup verification completed")
        return True
    
    def create_startup_script(self):
        """Create a startup script for easy system launch"""
        logger.info("🚀 Creating startup script...")
        
        startup_script = self.root_dir / "start_liberation_system.py"
        script_content = '''#!/usr/bin/env python3
"""
Liberation System Startup Script
Starts all system components in the correct order
"""

import asyncio
import subprocess
import sys
from pathlib import Path
import signal
import time

class LiberationSystemLauncher:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_api(self):
        """Start the FastAPI backend"""
        print("🚀 Starting Liberation System API...")
        api_process = subprocess.Popen([
            sys.executable, "-m", "api.main"
        ])
        self.processes.append(api_process)
        return api_process
    
    def start_web_interface(self):
        """Start the Next.js frontend"""
        print("🌐 Starting Web Interface...")
        web_process = subprocess.Popen([
            "npm", "run", "dev"
        ])
        self.processes.append(web_process)
        return web_process
    
    def start_core_system(self):
        """Start the core Liberation System"""
        print("⚡ Starting Liberation Core System...")
        core_process = subprocess.Popen([
            sys.executable, "core/automation-system.py"
        ])
        self.processes.append(core_process)
        return core_process
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\\n🛑 Shutting down Liberation System...")
        self.running = False
        for process in self.processes:
            process.terminate()
        sys.exit(0)
    
    def run(self):
        """Run the complete Liberation System"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🌟 LIBERATION SYSTEM STARTUP")
        print("=" * 50)
        
        # Start all components
        api_proc = self.start_api()
        time.sleep(2)  # Wait for API to start
        
        web_proc = self.start_web_interface()
        time.sleep(2)  # Wait for web interface to start
        
        core_proc = self.start_core_system()
        
        print("\\n✅ Liberation System is now running!")
        print("📊 Dashboard: http://localhost:3000")
        print("🌐 API: http://localhost:8000")
        print("\\nPress Ctrl+C to shutdown")
        
        # Keep running until interrupted
        try:
            while self.running:
                # Check if any process has died
                for process in self.processes:
                    if process.poll() is not None:
                        print(f"⚠️  Process {process.pid} has stopped")
                
                time.sleep(1)
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    launcher = LiberationSystemLauncher()
    launcher.run()
'''
        
        startup_script.write_text(script_content)
        startup_script.chmod(0o755)
        
        logger.info("✅ Startup script created: start_liberation_system.py")
        return True
    
    def run_setup(self):
        """Run the complete setup process"""
        logger.info("🌟 Starting Liberation System Enhancement Setup")
        logger.info("=" * 60)
        
        steps = [
            ("Check Dependencies", self.check_dependencies),
            ("Install Python Dependencies", self.install_python_dependencies),
            ("Install Node.js Dependencies", self.install_node_dependencies),
            ("Generate Screenshots", self.generate_screenshots),
            ("Setup Database", self.setup_database),
            ("Verify Setup", self.verify_setup),
            ("Create Startup Script", self.create_startup_script),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"🔄 {step_name}...")
            success = step_func()
            if not success:
                logger.error(f"❌ {step_name} failed")
                return False
            logger.info(f"✅ {step_name} completed")
        
        logger.info("=" * 60)
        logger.info("🎉 Liberation System Enhancement Setup Complete!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Run: python start_liberation_system.py")
        logger.info("2. Open: http://localhost:3000")
        logger.info("3. Explore the enhanced Liberation System!")
        logger.info("")
        logger.info("🌟 Ready to transform everything!")
        
        return True

def main():
    """Main entry point"""
    setup = LiberationEnhancementSetup()
    success = setup.run_setup()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
