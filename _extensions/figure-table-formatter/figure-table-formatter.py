#!/usr/bin/env python3

import json
import io
import sys
import re
import logging
import codecs

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Initialize global variables
sorted_ids = []
sorted_positions = []

# Objects dictionary and counters
objects = {
    "fig": "Figure",
    "tbl": "Table",
    "supfig": "Supplementary Figure",
    "suptbl": "Supplementary Table"
}

# Initialize counters for each object type
counters = {key: 0 for key in objects}

# Compile regex patterns for matching cross-references, tags, and placeholders
pattern_crossref = re.compile(r"@(" + "|".join(objects.keys()) + r"):(\w+)")
pattern_tag = re.compile(r"#(" + "|".join(objects.keys()) + r"):(\w+)")
pattern_placeholder = re.compile(r'&&&.*&&&')

# File paths
tag_file = "sorted_ids.txt"  # Input file to import sorted IDs and positions

pagebreak = {
    "epub": '<p style:"page-break-after: always;"> </p>',
    "html": '<div style="page-break-after: always;"></div>',
    "latex": '\\newpage{}',
    "docx": '<w:p><w:r><w:br w:type="page"/></w:r></w:p>',
    "odt": '<text:p text:style-name="Pagebreak"/>',
    "context": '\\page',
    "typst": '#pagebreak()'
}

def read_source():
    """Reads the input from stdin."""
    try:
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    except AttributeError:
        input_stream = codecs.getreader("utf-8")(sys.stdin)
    return input_stream.read()

def format_citations(doc):
    """Process citation blocks and format cross-references."""
    for block in doc.get("blocks", []):
        # Search for 'Cite' blocks within each block
        for i, element in enumerate(block.get('c', [])):
            if isinstance(element, dict) and element['t'] == 'Cite':
                ids = get_ids(element)
                if ids:
                    for id in ids:
                        if id not in sorted_ids:
                            sorted_ids.append(id)
                            category = id.split(":")[0]
                            if category in counters:
                                counters[category] += 1
                                sorted_positions.append(counters[category])
                    # Replace the citation block with formatted references
                    block['c'][i] = {'t': 'Str', 'c': format_ids(ids)}
                else:
                    logging.warning(f"No IDs found in Cite block: {element}")
    logging.info(f"Sorted IDs: {sorted_ids}")
    logging.info(f"Counters: {counters}")
    return doc

def get_ids(elements):
    """Extract citation IDs from nested elements."""
    matches = []
    if isinstance(elements, list):
        for element in elements:
            matches.extend(get_ids(element))
    elif isinstance(elements, dict):
        content = elements.get('c')
        if isinstance(content, list):
            matches.extend(get_ids(content))
        elif isinstance(content, str):
            match = pattern_crossref.match(content.strip("[]"))
            if match:
                category, identifier = match.groups()
                matches.append(f"{category}:{identifier}")
    return matches

def format_range(numbers):
    numbers = sorted(set(numbers))
    ranges, start, last = [], numbers[0], numbers[0]

    for number in numbers[1:]:
        if number == last + 1:
            last = number
        else:
            ranges.append(f"{start}" if start == last else f"{start}-{last}")
            start, last = number, number
    ranges.append(f"{start}" if start == last else f"{start}-{last}")
    return ', '.join(ranges)

def format_ids(ids):
    """Format citation IDs into human-readable references."""
    categorized_ids = {key: [] for key in objects}
    output = []

    for id in ids:
        category = id.split(":")[0]
        if category in categorized_ids:
            categorized_ids[category].append(id)

    for key, label in objects.items():
        list_order = [sorted_positions[sorted_ids.index(id)] for id in categorized_ids[key]]
        if list_order:
            ranges_formatted = format_range(list_order)
            output.append(f"{label}{'s' if len(list_order) > 1 else ''} {ranges_formatted}")

    return ", ".join(output)

def collect_figs_tables(doc):
    """Collect figure and table blocks by their identifiers."""
    new_blocks, figure_table_blocks = [], {}

    for block in doc.get("blocks", []):
        block_str = str(block)
        match = pattern_tag.search(block_str)
        if match:
            identifier = match.group(2)
            tag = f"{match.group(1)}:{identifier}"
            if tag in sorted_ids:
                new_tag = f"{format_ids([tag])}. "
                block = json.dumps(block)
                block = block.replace("#" + tag, new_tag)
                block = json.loads(block)
                figure_table_blocks[tag] = block
                logging.info(f"Tag found: {tag}")
            else:
                new_blocks.append(block)
        else:
            new_blocks.append(block)

    return new_blocks, figure_table_blocks

# Function to place figures and tables
def place_figs_tables(new_blocks, figure_table_blocks, output_format):
    """Detect placeholders and insert figure/table blocks in the correct positions."""
    blocks_with_figs_tables = []
    used_tags = set()  # Track already inserted items

    for block in new_blocks:
        block_str = str(block)
        matches = pattern_placeholder.findall(block_str)

        if matches:
            for match in matches:
                structured_order = match.strip("&&&")  # Strip the new placeholder delimiters
                logging.info(f"Placeholder: {structured_order}")

                # If no comma, treat as a single group or a single element
                groups = [structured_order] if ',' not in structured_order else structured_order.split(',')

                # Collect all items that need to be inserted based on the group(s)
                items_to_insert = [tag for group in groups for tag in sorted_ids
                                   if tag.startswith(tuple(group.split('-'))) and tag in figure_table_blocks]

                # Insert a page break before items and the items themselves
                if items_to_insert:
                    for tag in items_to_insert:
                        if tag not in used_tags:  # Check if tag has already been used
                            blocks_with_figs_tables.append(figure_table_blocks.pop(tag))
                            blocks_with_figs_tables.append({"t":"RawBlock","c":[output_format, pagebreak[output_format]]})
                            used_tags.add(tag)
                else:
                    logging.warning(f"No valid items to insert for placeholder: {structured_order}")
        else:
            # If the block is not a placeholder, retain it as-is
            blocks_with_figs_tables.append(block)

    # Insert remaining items (if any) that were not placed during placeholder insertion
    for tag in sorted_ids:
        if tag in figure_table_blocks and tag not in used_tags:
            blocks_with_figs_tables.append(figure_table_blocks.pop(tag))
            blocks_with_figs_tables.append({"t":"RawBlock","c":[output_format, pagebreak[output_format]]})
            used_tags.add(tag)

    return blocks_with_figs_tables
 
def import_ids_from_file():
    """Read sorted_ids and sorted_positions from an external file, and update counters based on tag order."""
    try:
        # Clear sorted_ids and sorted_positions to avoid duplicates
        sorted_ids.clear()
        sorted_positions.clear()
        logging.info(f"Sorted IDS is {sorted_ids}")

        # Reset counters for each object type
        counters.update({key: 0 for key in objects})

        with open(tag_file, 'r') as f:
            for line in f:
                tags = line.strip().split()
                for tag in tags:
                    category = tag.split(":")[0]
                    if category in objects.keys():
                        # Update the counter for the category
                        counters[category] += 1
                        # Append the tag and its position
                        sorted_ids.append(tag)
                        sorted_positions.append(counters[category])
                    else:
                        logging.warning(f"Unknown category in tag: {tag}")

        logging.info(f"Imported sorted_ids: {sorted_ids}")
        logging.info(f"Imported sorted_positions: {sorted_positions}")
        logging.info(f"Updated counters: {counters}")

    except FileNotFoundError:
        logging.error(f"Input file {tag_file} not found.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error processing the file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    except AttributeError:
        # Python 2 does not have sys.stdin.buffer.
        # REF: https://stackoverflow.com/questions/2467928/python-unicodeencode
        input_stream = codecs.getreader("utf-8")(sys.stdin)

    source = input_stream.read()

    try:
        doc = json.loads(source)

        if len(sys.argv) > 1:
            format = sys.argv[1]
        else:
            format = ""

        # Check for the metadata flag in the document
        use_file_import = doc.get('meta', {}).get('file-import', {}).get('c', {})
        logging.info(format)

        if use_file_import:
            # Import sorted_ids and sorted_positions from file
            logging.info("Importing sorted_ids and sorted_positions from file.")
            import_ids_from_file()
        else:
            # Process citations if no file import
            logging.info("Running format_citations.")
             
        altered = format_citations(doc)

        # Save citation list to file
        with open(tag_file, "w") as f:
            for citation_id in sorted_ids:
                f.write(f"{citation_id}\n")

        # Collect and place figures/tables
        new_blocks, figure_table_blocks = collect_figs_tables(altered if not use_file_import else doc)
        doc["blocks"] = place_figs_tables(new_blocks, figure_table_blocks, format)

        # Output the final document
        sys.stdout.write(json.dumps(doc))
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON input")
