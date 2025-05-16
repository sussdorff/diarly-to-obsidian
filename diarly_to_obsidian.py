#!/usr/bin/env python3
"""
Diarly to Obsidian Import Script

This script converts Diarly journal exports to Obsidian daily notes format.
It handles metadata conversion, attachment migration, and link format updates.
"""

import os
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
import argparse


class DiarlyToObsidianConverter:
    def __init__(self, source_dir, target_dir):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.metadata = self.load_metadata()
        
        # Create target directories
        self.daily_notes_dir = self.target_dir / "Daily Notes"
        self.attachments_dir = self.target_dir / "Attachments"
        self.templates_dir = self.target_dir / "_templates"
        
        # Journal name to tag mapping (customize as needed)
        self.journal_tags = {
            "Work Journal": "work",
            "Personal": "personal",
            # Add your custom mappings here
            # "Journal Name": "tag-name",
        }
        
    def journal_to_tag(self, journal_name):
        """Convert journal name to tag format"""
        if journal_name in self.journal_tags:
            return self.journal_tags[journal_name]
        
        # Auto-convert: lowercase, replace spaces with hyphens, remove special characters
        tag = journal_name.lower()
        tag = re.sub(r'[^\w\s-]', '', tag)  # Remove special characters
        tag = re.sub(r'\s+', '-', tag)      # Replace spaces with hyphens
        tag = re.sub(r'-+', '-', tag)       # Replace multiple hyphens with single
        tag = tag.strip('-')                # Remove leading/trailing hyphens
        return tag
    
    def load_metadata(self):
        """Load Diarly metadata from JSON file"""
        metadata_path = self.source_dir / "diarly_meta.json"
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_directories(self):
        """Create necessary directories in target location"""
        self.daily_notes_dir.mkdir(parents=True, exist_ok=True)
        self.attachments_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
    def create_daily_note_template(self):
        """Create a template for daily notes"""
        template_content = """---
date: {{date}}
tags: [daily-note]
---

"""
        template_path = self.templates_dir / "daily-note-template.md"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    def extract_location_from_content(self, content):
        """Extract location coordinates from diarly://map links"""
        location_pattern = r'\[([^\]]+)\]\(diarly://map/([0-9.-]+),([0-9.-]+)\)'
        match = re.search(location_pattern, content)
        if match:
            name = match.group(1)
            lat = match.group(2)
            lon = match.group(3)
            return f"{lat},{lon}", name
        return None, None
    
    def extract_weather_from_content(self, content):
        """Extract weather information from content"""
        # Pattern: temperature ˚C  weather_condition,  [location]
        weather_pattern = r'(\d+)\s*˚C\s+([^,]+),\s*\[([^\]]+)\]'
        match = re.search(weather_pattern, content)
        if match:
            temperature = match.group(1)
            condition = match.group(2).strip()
            return temperature, condition
        return None, None
    
    def get_weather_emoji(self, condition):
        """Convert weather condition to emoji"""
        condition_lower = condition.lower()
        weather_emojis = {
            'sunny': '☀️',
            'partly sunny': '🌤️',
            'mostly sunny': '🌤️',
            'clear': '☀️',
            'cloudy': '☁️',
            'mostly cloudy': '☁️',
            'partly cloudy': '⛅',
            'rain': '🌧️',
            'rainy': '🌧️',
            'shower': '🌦️',
            'showers': '🌦️',
            'thunderstorm': '⛈️',
            'storm': '⛈️',
            'fog': '🌫️',
            'foggy': '🌫️',
            'snow': '❄️',
            'snowy': '❄️',
            'windy': '💨',
            'drizzle': '🌦️',
            'mist': '🌫️',
            'haze': '🌫️',
            'overcast': '☁️'
        }
        
        for key, emoji in weather_emojis.items():
            if key in condition_lower:
                return emoji
        
        # Default emoji if no match
        return '🌡️'
    
    def extract_hashtags_from_content(self, content):
        """Extract all hashtags from content"""
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, content)
        return list(set(hashtags))  # Remove duplicates
    
    def convert_diarly_links_to_geo(self, content):
        """Convert diarly://map links to geo: format"""
        pattern = r'\[([^\]]+)\]\(diarly://map/([0-9.-]+),([0-9.-]+)\)'
        replacement = r'[\1](geo:\2,\3)'
        return re.sub(pattern, replacement, content)
    
    def update_attachment_links(self, content):
        """Update attachment links from data/file.ext to [[file.ext]]"""
        pattern = r'!\[\]\(data/([^)]+)\)'
        replacement = r'![[\1]]'
        return re.sub(pattern, replacement, content)
    
    def replace_weather_with_emoji(self, content, temperature, condition):
        """Replace weather condition text with emoji in content"""
        if temperature and condition:
            emoji = self.get_weather_emoji(condition)
            # Pattern to match weather line
            weather_pattern = rf'{temperature}\s*˚C\s+{re.escape(condition)},(\s*\[[^\]]+\]\([^)]+\))'
            replacement = rf'{temperature}°C {emoji}\1'
            return re.sub(weather_pattern, replacement, content)
        return content
    
    def get_journal_from_path(self, file_path):
        """Extract journal name from file path"""
        parts = file_path.parts
        if len(parts) >= 3:
            return parts[0]
        return "Tagebuch"  # Default
    
    def process_markdown_file(self, source_file):
        """Process a single markdown file"""
        # Read the file
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata
        relative_path = source_file.relative_to(self.source_dir)
        journal_name = self.get_journal_from_path(relative_path)
        
        # Get date from filename (MM-DD.md)
        filename = source_file.stem
        if filename == "Willkommen bei Diarly 👋":
            return  # Skip welcome file
            
        year = source_file.parent.name
        month, day = filename.split('-')
        date_str = f"{year}-{month}-{day}"
        
        # Extract location, weather, and hashtags
        location, location_name = self.extract_location_from_content(content)
        temperature, weather_condition = self.extract_weather_from_content(content)
        hashtags = self.extract_hashtags_from_content(content)
        
        # Build tags array
        tags = ["daily-note"]
        journal_tag = self.journal_to_tag(journal_name)
        if journal_tag:
            tags.append(journal_tag)
        tags.extend(hashtags)
        
        # Create YAML frontmatter
        yaml_lines = ["---"]
        yaml_lines.append(f"date: {date_str}")
        if location:
            yaml_lines.append(f"location: {location}")
        if temperature and weather_condition:
            yaml_lines.append(f"weather:")
            yaml_lines.append(f"  temperature: {temperature}")
            yaml_lines.append(f"  condition: {weather_condition}")
        yaml_lines.append(f"tags: [{', '.join(tags)}]")
        yaml_lines.append("---")
        yaml_lines.append("")
        
        # Update content
        content = self.convert_diarly_links_to_geo(content)
        content = self.update_attachment_links(content)
        content = self.replace_weather_with_emoji(content, temperature, weather_condition)
        
        # Combine frontmatter and content
        final_content = '\n'.join(yaml_lines) + content
        
        # Create year directory
        year_dir = self.daily_notes_dir / year
        year_dir.mkdir(exist_ok=True)
        
        # Write to new file
        target_file = year_dir / f"{date_str}.md"
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"Processed: {source_file} -> {target_file}")
    
    def migrate_attachments(self, source_data_dir):
        """Migrate attachments from data directory"""
        if not source_data_dir.exists():
            return
            
        year = source_data_dir.parent.name
        target_year_dir = self.attachments_dir / year
        target_year_dir.mkdir(exist_ok=True)
        
        for attachment in source_data_dir.iterdir():
            if attachment.is_file():
                target_file = target_year_dir / attachment.name
                shutil.copy2(attachment, target_file)
                print(f"Copied attachment: {attachment} -> {target_file}")
    
    def convert(self):
        """Run the conversion process"""
        print("Starting Diarly to Obsidian conversion...")
        
        # Create directories
        self.create_directories()
        self.create_daily_note_template()
        
        # Process all markdown files
        for journal_dir in self.source_dir.iterdir():
            if journal_dir.is_dir() and journal_dir.name not in ["logs", ".DS_Store"]:
                print(f"\nProcessing journal: {journal_dir.name}")
                
                for year_dir in journal_dir.iterdir():
                    if year_dir.is_dir() and year_dir.name.isdigit():
                        print(f"  Year: {year_dir.name}")
                        
                        # Process markdown files
                        for md_file in year_dir.glob("*.md"):
                            self.process_markdown_file(md_file)
                        
                        # Migrate attachments
                        data_dir = year_dir / "data"
                        if data_dir.exists():
                            self.migrate_attachments(data_dir)
        
        print("\nConversion complete!")


def main():
    parser = argparse.ArgumentParser(description="Convert Diarly export to Obsidian format")
    parser.add_argument("source", help="Source directory (Diarly export)")
    parser.add_argument("target", help="Target directory (Obsidian vault)")
    
    args = parser.parse_args()
    
    converter = DiarlyToObsidianConverter(args.source, args.target)
    converter.convert()


if __name__ == "__main__":
    main()