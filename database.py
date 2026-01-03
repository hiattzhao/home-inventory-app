"""
Database module for Home Inventory Application.
Handles SQLite database operations and item management.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple


class Database:
    """Manages SQLite database operations for inventory items."""
    
    def __init__(self, db_path: str = "inventory.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """Create database tables if they don't exist."""
        # Create items table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                value REAL NOT NULL,
                purchase_date TEXT,
                notes TEXT,
                photo_path TEXT,
                created_at TEXT NOT NULL,
                location TEXT
            )
        """)
        
        # Check if location column exists, add if not (for existing databases)
        self.cursor.execute("PRAGMA table_info(items)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'location' not in columns:
            self.cursor.execute("ALTER TABLE items ADD COLUMN location TEXT")
        
        # Create photos table for multiple photos per item
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                caption TEXT,
                display_order INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
            )
        """)
        
        # Create locations table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        
        # Populate default locations if empty
        self.cursor.execute("SELECT COUNT(*) FROM locations")
        if self.cursor.fetchone()[0] == 0:
            default_locations = [
                'Living Room', 'Kitchen', 'Bedroom', 'Bathroom', 
                'Garage', 'Basement', 'Attic', 'Office'
            ]
            for loc in default_locations:
                self.cursor.execute("INSERT INTO locations (name) VALUES (?)", (loc,))
        
        self.conn.commit()
        
        # Create categories table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        
        # Insert default categories if table is empty
        self.cursor.execute("SELECT COUNT(*) FROM categories")
        if self.cursor.fetchone()[0] == 0:
            default_categories = [
                "Electronics",
                "Furniture",
                "Tools",
                "Kitchen",
                "Clothing",
                "Books",
                "Sports",
                "Other"
            ]
            for category in default_categories:
                self.cursor.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    (category,)
                )
        
        self.conn.commit()
    
    def add_item(self, name: str, category: str, value: float,
                 purchase_date: str, notes: str = "", photo_path: str = "", location: str = "") -> int:
        """
        Add a new item to the database.
        
        Args:
            name: Item name
            category: Item category
            value: Item value
            purchase_date: Purchase date (YYYY-MM-DD format)
            notes: Additional notes
            photo_path: Path to item photo
            
        Returns:
            ID of the newly created item
        """
        created_at = datetime.now().isoformat()
        
        self.cursor.execute("""
            INSERT INTO items (name, category, value, purchase_date, notes, photo_path, created_at, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category, value, purchase_date, notes, photo_path, created_at, location))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_item(self, item_id: int, name: str, category: str, value: float,
                    purchase_date: str, notes: str = "", photo_path: str = "", location: str = "") -> bool:
        """
        Update an existing item.
        
        Args:
            item_id: ID of the item to update
            name: Item name
            category: Item category
            value: Item value
            purchase_date: Purchase date (YYYY-MM-DD format)
            notes: Additional notes
            photo_path: Path to item photo
            
        Returns:
            True if update was successful, False otherwise
        """
        self.cursor.execute("""
            UPDATE items
            SET name = ?, category = ?, value = ?, purchase_date = ?,
                notes = ?, photo_path = ?, location = ?
            WHERE id = ?
        """, (name, category, value, purchase_date, notes, photo_path, location, item_id))
        
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_item(self, item_id: int) -> bool:
        """
        Delete an item from the database.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        self.cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_item(self, item_id: int) -> Optional[Tuple]:
        """
        Get a single item by ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            Tuple containing item data or None if not found
        """
        self.cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        return self.cursor.fetchone()
    
    def get_all_items(self) -> List[Tuple]:
        """
        Get all items from the database.
        
        Returns:
            List of tuples containing item data
        """
        self.cursor.execute("SELECT * FROM items ORDER BY created_at DESC")
        return self.cursor.fetchall()
    
    def search_items(self, name: str = "", category: str = "",
                     min_value: float = None, max_value: float = None,
                     start_date: str = "", end_date: str = "", location: str = "") -> List[Tuple]:
        """
        Search and filter items based on criteria.
        
        Args:
            name: Search by name (partial match)
            category: Filter by category
            min_value: Minimum value filter
            max_value: Maximum value filter
            start_date: Start date for purchase date range
            end_date: End date for purchase date range
            
        Returns:
            List of tuples containing matching item data
        """
        query = "SELECT * FROM items WHERE 1=1"
        params = []
        
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        
        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
        
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        
        if min_value is not None:
            query += " AND value >= ?"
            params.append(min_value)
        
        if max_value is not None:
            query += " AND value <= ?"
            params.append(max_value)
        
        if start_date:
            query += " AND purchase_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND purchase_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY created_at DESC"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def get_categories(self) -> List[str]:
        """
        Get all categories.
        
        Returns:
            List of category names
        """
        self.cursor.execute("SELECT name FROM categories ORDER BY name")
        return [row[0] for row in self.cursor.fetchall()]
    
    def add_category(self, category_name: str) -> bool:
        """
        Add a new category to the database.
        
        Args:
            category_name: Name of the category to add
            
        Returns:
            True if category was added, False if it already exists
        """
        try:
            self.cursor.execute(
                "INSERT INTO categories (name) VALUES (?)",
                (category_name,)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Category already exists (UNIQUE constraint)
            return False
    
    def delete_category(self, category_name: str) -> bool:
        """
        Delete a category.
        
        Note: Default categories cannot be deleted.
        
        Args:
            category_name: Name of category to delete
            
        Returns:
            True if deleted, False if could not be deleted (e.g. default)
        """
        # List of default categories that shouldn't be deleted
        default_categories = [
            'Electronics', 'Furniture', 'Clothing', 'Books', 
            'Appliances', 'Tools', 'Collectibles', 'Other'
        ]
        
        if category_name in default_categories:
            return False
            
        self.cursor.execute("DELETE FROM categories WHERE name = ?", (category_name,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_locations(self) -> List[str]:
        """
        Get all locations.
        
        Returns:
            List of location names
        """
        self.cursor.execute("SELECT name FROM locations ORDER BY name")
        return [row[0] for row in self.cursor.fetchall()]

    def add_location(self, location_name: str) -> bool:
        """
        Add a new location.
        
        Args:
            location_name: Name of new location
            
        Returns:
            True if successful, False if location already exists
        """
        try:
            self.cursor.execute(
                "INSERT INTO locations (name) VALUES (?)",
                (location_name,)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_location(self, location_name: str) -> bool:
        """
        Delete a location.
        
        Note: Default locations cannot be deleted.
        
        Args:
            location_name: Name of location to delete
            
        Returns:
            True if deleted, False if default
        """
        default_locations = [
            'Living Room', 'Kitchen', 'Bedroom', 'Bathroom', 
            'Garage', 'Basement', 'Attic', 'Office'
        ]
        
        if location_name in default_locations:
            return False
            
        self.cursor.execute("DELETE FROM locations WHERE name = ?", (location_name,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def add_photo(self, item_id: int, photo_path: str, caption: str = "", display_order: int = 0) -> int:
        """
        Add a photo to an item.
        
        Args:
            item_id: ID of the item
            photo_path: Path to the photo file
            caption: Optional caption for the photo
            display_order: Order for displaying photos (0 = first)
            
        Returns:
            ID of the newly created photo record
        """
        created_at = datetime.now().isoformat()
        
        self.cursor.execute("""
            INSERT INTO photos (item_id, photo_path, caption, display_order, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (item_id, photo_path, caption, display_order, created_at))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_item_photos(self, item_id: int) -> List[Tuple]:
        """
        Get all photos for an item.
        
        Args:
            item_id: ID of the item
            
        Returns:
            List of tuples containing photo data (id, item_id, photo_path, caption, display_order, created_at)
        """
        self.cursor.execute("""
            SELECT * FROM photos 
            WHERE item_id = ? 
            ORDER BY display_order, created_at
        """, (item_id,))
        return self.cursor.fetchall()
    
    def delete_photo(self, photo_id: int) -> bool:
        """
        Delete a photo.
        
        Args:
            photo_id: ID of the photo to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        self.cursor.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def update_photo_order(self, photo_id: int, display_order: int) -> bool:
        """
        Update the display order of a photo.
        
        Args:
            photo_id: ID of the photo
            display_order: New display order
            
        Returns:
            True if update was successful, False otherwise
        """
        self.cursor.execute("""
            UPDATE photos SET display_order = ? WHERE id = ?
        """, (display_order, photo_id))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
