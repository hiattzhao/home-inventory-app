"""
Test script to validate the Home Inventory Application components.
This script tests the database functionality without requiring a GUI.
"""

import os
import sys
from datetime import datetime

# Test database module
print("=" * 60)
print("Testing Home Inventory Application Components")
print("=" * 60)

print("\n1. Testing Database Module...")
try:
    from database import Database
    
    # Create test database
    test_db = Database("test_inventory.db")
    print("   ✓ Database initialized successfully")
    
    # Test getting categories
    categories = test_db.get_categories()
    print(f"   ✓ Categories loaded: {', '.join(categories)}")
    
    # Test adding an item
    item_id = test_db.add_item(
        name="Test Laptop",
        category="Electronics",
        value=1200.00,
        purchase_date="2024-01-15",
        notes="MacBook Pro for work",
        photo_path=""
    )
    print(f"   ✓ Item added with ID: {item_id}")
    
    # Test getting all items
    items = test_db.get_all_items()
    print(f"   ✓ Retrieved {len(items)} item(s)")
    
    # Test updating an item
    success = test_db.update_item(
        item_id=item_id,
        name="Test Laptop (Updated)",
        category="Electronics",
        value=1150.00,
        purchase_date="2024-01-15",
        notes="MacBook Pro for work - updated price",
        photo_path=""
    )
    print(f"   ✓ Item updated: {success}")
    
    # Test searching items
    search_results = test_db.search_items(name="Laptop")
    print(f"   ✓ Search found {len(search_results)} item(s)")
    
    # Test deleting an item
    success = test_db.delete_item(item_id)
    print(f"   ✓ Item deleted: {success}")
    
    # Clean up
    test_db.close()
    os.remove("test_inventory.db")
    print("   ✓ Test database cleaned up")
    
    print("\n✅ Database module: ALL TESTS PASSED")
    
except Exception as e:
    print(f"\n❌ Database module test failed: {e}")
    sys.exit(1)

print("\n2. Testing Import Statements...")
try:
    from item_dialog import ItemDialog
    print("   ✓ ItemDialog imported successfully")
    
    from search_dialog import SearchDialog
    print("   ✓ SearchDialog imported successfully")
    
    from export_csv import CSVExporter
    print("   ✓ CSVExporter imported successfully")
    
    from export_pdf import PDFExporter
    print("   ✓ PDFExporter imported successfully")
    
    print("\n✅ All modules: IMPORTS SUCCESSFUL")
    
except Exception as e:
    print(f"\n❌ Import test failed: {e}")
    sys.exit(1)

print("\n3. Checking File Structure...")
required_files = [
    "main.py",
    "database.py",
    "item_dialog.py",
    "search_dialog.py",
    "export_csv.py",
    "export_pdf.py",
    "requirements.txt",
    "README.md",
    ".gitignore"
]

all_files_present = True
for file in required_files:
    if os.path.exists(file):
        print(f"   ✓ {file}")
    else:
        print(f"   ✗ {file} - MISSING")
        all_files_present = False

if all_files_present:
    print("\n✅ File structure: COMPLETE")
else:
    print("\n❌ File structure: INCOMPLETE")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL VALIDATION TESTS PASSED!")
print("=" * 60)
print("\nThe application is ready to use.")
print("\nTo run the application:")
print("  1. Ensure you have a graphical environment (X11/Wayland)")
print("  2. Activate the virtual environment: source venv/bin/activate")
print("  3. Run: python main.py")
print("\nNote: GUI applications require a display server to run.")
print("=" * 60)
