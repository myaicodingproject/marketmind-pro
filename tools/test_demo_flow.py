#!/usr/bin/env python3
"""Test demo data loading and storage"""

import json
import sys
sys.path.insert(0, '/mnt/c/kiro')

# Simulate the backend flow
print("🧪 TESTING DEMO DATA FLOW\n")
print("="*70)

# Step 1: Load demo data
print("\n1️⃣ Loading demo data...")
with open('data/demo_report_avgo.json', 'r', encoding='utf-8') as f:
    demo_data = json.load(f)

print(f"   ✓ Loaded {len(demo_data)} top-level keys")
print(f"   ✓ Statistics: {demo_data.get('statistics')}")
print(f"   ✓ Quality: {demo_data.get('quality_score')}")
print(f"   ✓ Generated: {demo_data.get('generated_at')}")

# Step 2: Simulate backend modifications
print("\n2️⃣ Simulating backend modifications...")
report_id = "test-123"
demo_data['report_id'] = report_id
demo_data['ticker'] = 'AVGO'
demo_data['company_name'] = 'Broadcom Inc.'

if 'metadata' not in demo_data:
    demo_data['metadata'] = {}
demo_data['metadata']['is_demo'] = True

# Check statistics condition
if 'statistics' not in demo_data or not demo_data['statistics']:
    print("   ⚠️  Would overwrite statistics!")
    total_words = sum(len(section.get('content', '').split()) for section in demo_data.get('sections', {}).values())
    demo_data['statistics'] = {
        'total_sections': len(demo_data.get('sections', {})),
        'total_words': total_words
    }
else:
    print("   ✓ Preserving existing statistics")

if 'quality_score' not in demo_data:
    print("   ⚠️  Would set quality_score")
    demo_data['quality_score'] = 94
else:
    print("   ✓ Preserving existing quality_score")

# Step 3: Check final data
print("\n3️⃣ Final data to be stored:")
print(f"   report_id: {demo_data.get('report_id')}")
print(f"   ticker: {demo_data.get('ticker')}")
print(f"   company_name: {demo_data.get('company_name')}")
print(f"   statistics: {demo_data.get('statistics')}")
print(f"   quality_score: {demo_data.get('quality_score')}")
print(f"   generated_at: {demo_data.get('generated_at')}")
print(f"   sections: {len(demo_data.get('sections', {}))} sections")

# Step 4: Simulate what frontend receives
print("\n4️⃣ What frontend would receive:")
print(json.dumps({
    'statistics': demo_data.get('statistics'),
    'quality_score': demo_data.get('quality_score'),
    'generated_at': demo_data.get('generated_at'),
    'ticker': demo_data.get('ticker')
}, indent=2))

print("\n" + "="*70)
print("✅ Test complete!")
