# Home Inventory Application

A cross-platform desktop application for managing your home inventory with categories, photos, search, and export capabilities.

## Features

- **Add/Edit/Delete Items**: Easily manage your inventory items
- **Categories**: Organize items into predefined categories (Electronics, Furniture, Tools, Kitchen, Clothing, Books, Sports, Other)
- **Custom Categories**: Create your own custom categories on the fly
- **Locations**: Track where items are stored (rooms, closets, bins, etc.)
- **Custom Locations**: Add new locations on the fly from the item dialog or via File → Configure Locations
- **Value Tracking**: Record the monetary value and purchase date of each item
- **Photo Upload**: Attach photos to your items for easy identification
- **Search & Filter**: Quickly find items by name, category, value range, or purchase date
- **Export**: Export your inventory to CSV or PDF format with embedded photos
- **Analyze**: Visualize totals by category or location (pie charts, histograms) and export charts to PDF

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:

```bash
python main.py
```

### Adding Items

1. Click the "Add Item" button in the toolbar
2. Fill in the item details (name, category, value, purchase date, notes)
3. Optionally upload a photo
4. Click "Save"

### Adding Custom Categories

1. When adding or editing an item, click the "+" button next to the category dropdown
2. Enter your custom category name
3. The new category will be saved and available for all items

Alternatively, you can type a new category name directly in the category field (which is editable).

### Editing Items

1. Select an item from the table
2. Click the "Edit Item" button
3. Modify the details
4. Click "Save"

### Deleting Items

1. Select an item from the table
2. Click the "Delete Item" button
3. Confirm the deletion

### Searching and Filtering

1. Click the "Search" button
2. Enter search criteria (name, category, value range, date range)
3. Results will update automatically
4. Click "Clear Filters" to show all items

### Exporting

- **CSV**: File → Export CSV
- **PDF**: File → Export PDF (includes photos)

### Analysis & Charts

- Open via **File → Analyze** (Ctrl+A)
- View totals by **Category** or **Location**
- Switch between **Pie Chart** and **Histogram**
- Charts auto-load on open; click **Refresh** to reload data
- Export the current chart to **PDF** via **Export as PDF**

## Technical Details

- **Framework**: PyQt6
- **Database**: SQLite
- **Image Processing**: Pillow
- **PDF Generation**: ReportLab
- **Charts**: matplotlib (pie charts, histograms)

## Requirements

- Python 3.8 or higher
- PyQt6
- Pillow
- ReportLab
- matplotlib

## License

This project is open source and available for personal use.
