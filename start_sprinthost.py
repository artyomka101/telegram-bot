#!/usr/bin/env python3
"""
Startup script for SprintHost deployment
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting Telegram Bot on SprintHost...")
    
    # Check if BOT_TOKEN is set
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ Error: BOT_TOKEN environment variable is not set!")
        print("Please set BOT_TOKEN in your SprintHost environment variables.")
        sys.exit(1)
    
    print("✅ BOT_TOKEN found")
    
    # Install dependencies if needed
    try:
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                     check=True, capture_output=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Warning: Could not install dependencies: {e}")
    
    # Start the bot
    print("🤖 Starting bot...")
    try:
        from app import main as app_main
        app_main()
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
