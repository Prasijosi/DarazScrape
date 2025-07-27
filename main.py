#!/usr/bin/env python3
"""
Daraz Nepal Product Scraper
Main entry point for the application
"""

import sys
import argparse
from cli import run_cli
from api import run_api_server


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Daraz Nepal Product Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run in CLI mode
  python main.py --api              # Run as API server
  python main.py --help             # Show this help message
        """
    )
    
    parser.add_argument(
        '--api', 
        action='store_true',
        help='Run as FastAPI server instead of CLI mode'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for API server (default: 8000)'
    )
    
    args = parser.parse_args()
    
    if args.api:
        print("🚀 Starting Daraz Scraper API Server...")
        print(f"📡 Server will be available at: http://localhost:{args.port}")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)
        run_api_server()
    else:
        run_cli()


if __name__ == "__main__":
    main() 