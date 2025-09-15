# Code Block Fix Script

This script automatically converts problematic code blocks in markdown files from table format to proper markdown code blocks using Anthropic's Claude.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements_fix_script.txt
   ```

2. **Set up your API key:**
   - Copy `env_template.txt` to `.env`
   - Add your actual Anthropic API key to the `.env` file:
     ```
     ANTHROPIC_API_KEY=your_actual_api_key_here
     ```

3. **Get an Anthropic API key:**
   - Sign up at https://console.anthropic.com/
   - Create an API key in your account settings

## Usage

Run the script:
```bash
python fix_code_blocks.py
```

## What it does

The script will:
1. ✅ Create a backup of the original file with timestamp
2. 🔍 Find all problematic code blocks (table format with `| code |` and `| :---- |`)
3. 🤖 Use Claude to convert each block to proper markdown format
4. 💾 Replace the content in the original file
5. 📊 Report progress and statistics

## Example Conversion

**Before:**
```
| `pip install langchain` |
| :---- |
```

**After:**
```bash
pip install langchain
```

## Features

- **Smart language detection**: Automatically detects if code is Python, bash, JSON, etc.
- **Proper formatting**: Adds correct indentation and line breaks
- **Progress tracking**: Shows which block is being processed
- **Backup creation**: Always creates a backup before making changes
- **Error handling**: Gracefully handles API errors and continues processing
- **Rate limiting**: Includes delays to respect API limits

## Safety

- Creates timestamped backups before making any changes
- Only processes the specific problematic pattern
- Preserves all other content unchanged
- Can be run multiple times safely (won't re-process already fixed blocks)
