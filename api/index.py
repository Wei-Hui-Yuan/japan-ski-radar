import sys
import os

# Add root directory to sys.path so server and scraper_engine can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from server import app

# Export app for Vercel Serverless Function runtime
__all__ = ["app"]
