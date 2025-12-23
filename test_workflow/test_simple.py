"""Simple test to verify the workflow"""
print("Starting test...")

import sys
print(f"Python: {sys.executable}")

# Test shared module
print("Loading shared module...")
from shared import TEST_DIR, print_info, OPENAI_API_KEY
print(f"TEST_DIR: {TEST_DIR}")
print(f"API Key present: {bool(OPENAI_API_KEY)}")

# Check input file
input_file = TEST_DIR / 'input.md'
print(f"Input file exists: {input_file.exists()}")
if input_file.exists():
    content = input_file.read_text()
    print(f"Input content preview: {content[:100]}...")

print("Test complete!")








