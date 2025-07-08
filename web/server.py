#!/usr/bin/env python3
"""
Simple HTTP Server for the Tesseract.js Web App
Run this to serve the web application locally
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def main():
    # Change to the web directory
    web_dir = Path(__file__).parent
    os.chdir(web_dir)
    
    PORT = 8080
    
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
            self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
            super().end_headers()
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("🚀 Student Composition Corrector - Web Server Starting...")
        print("=" * 60)
        print(f"📡 Server running at: http://localhost:{PORT}")
        print(f"📁 Serving from: {web_dir}")
        print("=" * 60)
        print("💡 Features:")
        print("   • Drag & drop image upload")
        print("   • Real-time OCR with Tesseract.js")
        print("   • Automatic typo detection")
        print("   • Visual annotation of errors")
        print("   • Downloadable results")
        print("=" * 60)
        print("🌐 Opening browser...")
        
        # Open browser automatically
        webbrowser.open(f'http://localhost:{PORT}')
        
        print("🎯 Ready! Upload a student composition image to get started.")
        print("⏹️  Press Ctrl+C to stop the server")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            print("👋 Thanks for using Student Composition Corrector!")

if __name__ == "__main__":
    main()
