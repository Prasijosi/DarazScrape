#!/usr/bin/env python3
"""
Daraz Nepal Product Scraper
Backward compatibility launcher
"""

import sys
from main import main

if __name__ == "__main__":
    # Check for legacy --api flag
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        # Remove the --api flag and add it back in the correct format
        sys.argv = [sys.argv[0], "--api"] + sys.argv[2:]
    
    main()
        