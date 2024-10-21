#!/usr/bin/env python3

import sys
from pandocfilters import toJSONFilter, Str, Cite
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global dictionary to store citation counters
counters = {
    "fig": {},
    "tbl": {},
    "supfig": {},
    "suptbl": {}
}

# Global counter for each category
counter_values = {
    "fig": 1,
    "tbl": 1,
    "supfig": 1,
    "suptbl": 1
}

# Set to track unique citation IDs across the entire document
global_unique_citations = set()

# List to maintain the order of appearance of unique citations
citation_order = []

# File path to save the citations
output_file = "citations_list.txt"

def get_citation_label(citation_id):
    """Get the label and type for the given citation ID."""
    if citation_id.startswith("fig:"):
        return "Figure", "fig"
    elif citation_id.startswith("tbl:"):
        return "Table", "tbl"
    elif citation_id.startswith("supfig:"):
        return "Supplementary Figure", "supfig"
    elif citation_id.startswith("suptbl:"):
        return "Supplementary Table", "suptbl"
    return None, None

def get_counter_for_citation(citation_id, citation_type):
    """Retrieve or assign a counter for a citation."""
    if citation_id not in counters[citation_type]:
        counters[citation_type][citation_id] = counter_values[citation_type]
        counter_values[citation_type] += 1
    return counters[citation_type][citation_id]

def format_citation_list(citation_list, label):
    """Format a list of citation counters, merging consecutive numbers into ranges."""
    if not citation_list:
        return ""

    citation_list = sorted(map(int, citation_list))  # Sort the list of citation counters
    ranges = []
    range_start = citation_list[0]
    prev = citation_list[0]

    for current in citation_list[1:]:
        if current == prev + 1:
            # Continue the range
            prev = current
        else:
            # End the current range and start a new one
            if range_start == prev:
                ranges.append(str(range_start))
            else:
                ranges.append(f"{range_start}-{prev}")
            range_start = current
            prev = current

    # Add the last range
    if range_start == prev:
        ranges.append(str(range_start))
    else:
        ranges.append(f"{range_start}-{prev}")

    # Join the ranges with commas
    if len(citation_list) == 1:
        return f"{label} {ranges[0]}"
    else:
        return f"{label}s {', '.join(ranges)}"

def replace_custom_citations(key, value, format, meta):
    if key == 'Cite':
        citations = value[0]  # The list of citations
        local_unique_citations = set()  # Local set for each citation block
        new_citation_texts = []

        # Dictionary to hold processed labels and counters
        citation_groups = {"fig": [], "tbl": [], "supfig": [], "suptbl": []}

        # Process each citation
        for citation in citations:
            citation_id = citation['citationId']  # Access the citation ID
            label, citation_type = get_citation_label(citation_id)

            if label and citation_type:
                # Only process citations with the correct prefix
                if citation_id not in local_unique_citations:
                    local_unique_citations.add(citation_id)
                    # Add to the global unique citation set
                    if citation_id not in global_unique_citations:
                        global_unique_citations.add(citation_id)
                        citation_order.append(citation_id)

                    # Retrieve the counter for the citation and store it
                    counter = get_counter_for_citation(citation_id, citation_type)
                    citation_groups[citation_type].append(str(counter))

        # Format the output for each citation group
        formatted_citations = []
        for citation_type, citation_list in citation_groups.items():
            if citation_list:
                # Format and append the formatted citations (handling ranges)
                formatted_citations.append(format_citation_list(citation_list, get_citation_label(f'{citation_type}:')[0]))

        # Join all the citation groups together
        if formatted_citations:
            new_citation_texts.append(Str("; ".join(formatted_citations)))

        # Log citation groups for debugging
        logging.info(f"Citations processed: {new_citation_texts}")
        
        # Return the modified citation as a string
        if new_citation_texts:
            return new_citation_texts  # Only return modified texts if there's a match
        else:
            return None  # Ignore citations that don't match the prefixes

if __name__ == "__main__":
    # Apply the filter to collect citations
    toJSONFilter(replace_custom_citations)

    # After processing, save the citation list to a file
    with open(output_file, "w") as f:
        for citation_id in citation_order:
            f.write(citation_id + "\n")

    logging.info(f"Unique citations saved to {output_file}")
