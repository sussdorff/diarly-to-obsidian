# Diarly to Obsidian Converter

This script converts Diarly journal exports to Obsidian daily notes format.

## Features

- Converts all journal entries to daily notes format (YYYY-MM-DD.md)
- Preserves metadata in YAML frontmatter
- Converts location data to Map View plugin format
- Migrates attachments to centralized folder structure
- Preserves hashtags from content
- Converts journal types to tags (customizable)

## Requirements

- Python 3.6+
- No external dependencies (uses standard library only)

## Usage

### Step 1: Export from Diarly

1. Open Diarly
2. Go to Menu Bar → `File` → `Export`
3. Choose **Markdown** as the export format
4. Select which journals to export
5. Save the exported zip file

The export will create a structure like:
```
Export/
├── Journal Name/
│   ├── 2023/
│   │   ├── 01-15.md
│   │   ├── 01-16.md
│   │   └── data/
│   │       └── image.jpeg
│   └── 2024/
│       ├── 03-12.md
│       └── data/
├── Another Journal/
│   └── ...
└── diarly_meta.json
```

### Step 2: Extract the Export

Extract the zip file to a folder on your computer.

### Step 3: Run the Converter

```bash
python3 diarly_to_obsidian.py /path/to/diarly/export /path/to/obsidian/vault
```

Example:
```bash
python3 diarly_to_obsidian.py ~/Downloads/Export ~/Documents/ObsidianVault
```

The script will create this structure in your Obsidian vault:
```
ObsidianVault/
├── Daily Notes/
│   ├── 2023/
│   │   ├── 2023-01-15.md
│   │   └── 2023-01-16.md
│   └── 2024/
│       └── 2024-03-12.md
├── Attachments/
│   ├── 2023/
│   │   └── image.jpeg
│   └── 2024/
└── _templates/
    └── daily-note-template.md
```

## Customization

### Journal to Tag Mapping

By default, the script converts journal names to tags. You can customize this mapping by editing the `journal_tags` dictionary in the script:

```python
# In diarly_to_obsidian.py
self.journal_tags = {
    "Journal Name": "tag-name",
    "Work Journal": "work",
    "Personal": "personal",
    # Add your custom mappings here
}
```

If a journal name isn't in the mapping, it will be converted to a tag automatically by:
- Converting to lowercase
- Replacing spaces with hyphens
- Removing special characters

### Location Links

The script converts Diarly location links to be compatible with the Obsidian Map View plugin:
- `diarly://map/lat,lon` → `geo:lat,lon`
- Location coordinates are added to YAML frontmatter as `location: lat,lon`

### Weather Information

If your entries contain weather data in the format `12 ˚C  Sunny, [Location]`:
- Weather data is extracted to YAML frontmatter
- Weather conditions are replaced with emojis in the note content
- Example: "Sunny" → ☀️, "Rainy" → 🌧️

## Notes

- The script preserves all original content
- Hashtags from Diarly are preserved and added to the tags array
- All attachments are organized by year in a central Attachments folder
- Original journal structure is preserved through tags
- A daily note template is created in `_templates/` for future use in Obsidian