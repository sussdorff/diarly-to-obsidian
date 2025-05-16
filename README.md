# Diarly to Obsidian Converter

This script converts Diarly journal exports to Obsidian daily notes format.

## Features

- Converts all journal entries to daily notes format (YYYY-MM-DD.md)
- Preserves metadata in YAML frontmatter
- Converts location data to Map View plugin format
- Migrates attachments to centralized folder structure
- Preserves hashtags from content
- Converts journal types to tags

## Usage

1. Export your Diarly data (should create a folder structure with journals and years)
2. Create a new or choose an existing Obsidian vault directory
3. Run the conversion script:

```bash
python3 diarly_to_obsidian.py /path/to/diarly/export /path/to/obsidian/vault
```

## Output Structure

```
ObsidianVault/
├── Daily Notes/
│   ├── 2013/
│   │   ├── 2013-03-24.md
│   │   └── ...
│   └── ...
├── Attachments/
│   ├── 2013/
│   │   ├── image1.jpeg
│   │   └── ...
│   └── ...
└── _templates/
    └── daily-note-template.md
```

## Conversions

### Metadata
- Date: Extracted from filename and folder structure
- Location: Converted to Map View plugin format
- Tags: Journal type + extracted hashtags

### Links
- `diarly://map/lat,lon` → `geo:lat,lon`
- `![](data/file.ext)` → `![[file.ext]]`

### Journal to Tag Mapping
- "Tagebuch" → `#personal`
- "Work Highlights" → `#work-highlights`
- "CST Learning Diary" → `#cst-learning-diary`
- And more...

## Requirements

- Python 3.6+
- No external dependencies (uses standard library only)

## Notes

- The script preserves all original content
- Location links are converted to work with Map View plugin
- All attachments are organized by year
- Original journal structure is preserved through tags