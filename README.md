# Home Inventory Manager

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

## Exporting for macOS with py2app

On macOS, you can package the app as a standalone application bundle with py2app.

1. **Install py2app** (inside the same virtual environment if you use one):

   ```bash
   pip install py2app
   ```

2. **Build the app** from the project directory:

   ```bash
   python3 setup.py py2app
   ```

3. **Find the exported application** in the project folder:
   - The build output will be created in the `dist/` directory
   - The app bundle will appear as `dist/Home Inventory Manager.app`

4. **Run the packaged app** by opening the `.app` bundle in Finder, or from Terminal:
   ```bash
   open dist/"Home Inventory Manager.app"
   ```

> The project already includes a setup script that uses the app entry point in `main.py` and the icon file `icon.icns`.

## Exporting for Linux with pyinstaller

On Linux, you can package the app as a standalone executable with PyInstaller.

1. **Install PyInstaller** (inside the same virtual environment if you use one):

   ```bash
   pip install pyinstaller
   ```

2. **Build the executable** from the project directory:

   ```bash
   pyinstaller --onefile main.py
   ```

3. **Find the exported executable** in the project folder:
   - The build output will be created in the `dist/` directory
   - The executable will appear as `dist/main`

4. **Run the packaged app** from Terminal:
   ```bash
   ./dist/main
   ```

### Move the app to a User-Specific Directory and Launch it
0. Rename main to "Home Inventory Manager" (without quotes)

1. Create a local bin directory if it doesn't exist:

   ```bash
   mkdir -p ~/.local/bin
   ```

2. Move the executable there
   ```bash
   mv "Home Inventory Manager" ~/.local/bin/"Home Inventory Manager"
   ```

3. Ensure ~/.local/bin is in your PATH by adding this line to your shell configuration file (like ~/.bashrc or ~/.zshrc):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

4. Apply the Changes

To make your terminal recognize the changes immediately without restarting it, reload your configuration file:

   ```bash
   # If using Bash
   source ~/.bashrc

   # If using Zsh
   source ~/.zshrc
   ```
5. Create the Launcher Directory and .desktop Entry 

If it doesn't already exist, create the local user directory where Linux environments store desktop shortcuts:

   ```bash
   mkdir -p ~/.local/share/applications
   
   nano ~/.local/share/applications/"Home Inventory Manager.desktop"
   ```
Paste the following configuration template inside it:

```
[Desktop Entry]
Type=Application
Name=Home Inventory Manager
Comment=A cross-platform desktop application for managing your home inventory
Exec="Home Inventory Manager"
Icon=utilities-terminal
Terminal=false
Categories=Utility;
```

6. Make Executable & Update Database (for Omarchy)

Give the desktop file proper execution rights and trigger Omarchy's menu system to re-index it immediately:

   ```bash
   chmod +x ~/.local/share/applications/"Home Inventory Manager.desktop"

   update-desktop-database ~/.local/share/applications
   ```

Now, just hit Super + Space on your keyboard, type "Home Inventory Manager", and the app will launch instantly.

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

This project is licensed under the MIT License. See [LICENSE](LICENSE).
