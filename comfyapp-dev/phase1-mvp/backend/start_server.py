#!/usr/bin/env python3
"""
Server starter script for Flux Kontext Max App
"""
import uvicorn
import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def start_server():
    """Start the Flux server"""
    try:
        logger.info("🚀 Starting Flux Kontext Max Server...")
        port = int(os.getenv('PORT', 8003))
        logger.info(f"📱 Access your app at: http://localhost:{port}")
        logger.info("🔑 Don't forget to add your Black Forest Labs API key!")
        logger.info("⏹️  Press Ctrl+C to stop the server")
        
        from flux_main import app
        
        # Start server
        uvicorn.run(
            app, 
            host="0.0.0.0",  # Accept connections from any IP
            port=port,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()