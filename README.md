# Figure-Table-Formatter Documentation

## Overview

The Figure-Table-Formatter is a Pandoc/Quarto filter designed to enhance citation management for figures, tables, supplementary figures, and supplementary tables within documents. It automatically formats citations based on their prefixes, ensuring consistent styling and handling of ranges in citation numbers.
Key Features

- Handles Multiple Citation Types: Supports citations starting with fig:, supfig:, tbl:, and suptbl:.
- Smart Formatting: Formats citations to display singular or plural correctly and manages ranges (e.g., "Figures 1-2, 4").
- Deduplication: Automatically ignores duplicate citations within the same reference set.
- Ordered Citation Output: Maintains the order of appearance for unique citations across the document.
- Citation Logging: Saves a list of all unique citation IDs to an output file for further reference.

## Installation

To use the Figure-Table-Formatter, ensure you have Pandoc installed. You can then create a Python script with the filter code provided. Save this script as figure_table_formatter.py.

Requirements

- Python 3.x
- pandocfilters library

You can install the pandocfilters library using pip:

```bash
pip install pandocfilters
```

## Usage

To apply the filter to your Pandoc document, run the following command:

```bash
pandoc input.md --filter ./figure_table_formatter.py -o output.md
```

Replace input.md with your source document and output.md with your desired output file.

## Example YAML Front Matter

Here’s how you can structure a Markdown document with a YAML front matter while using the Figure-Table-Formatter filter. Make sure that the python file is an executable file (chmod 744 figure-table-formatter.py):

```markdown
---
filters:
  - ./figure_table_formatter.py
---

# Introduction

This document discusses various experiments. We will refer to several figures and tables.

In Experiment 1, we can see the results in @fig:experiment1 and @fig:experiment2. Also, @fig:experiment4 illustrates an important finding.

The analysis is summarized in @tbl:results and detailed further in @tbl:summary.

Supplementary details can be found in @supfig:extra1 and @suptbl:appendixA.
```

When processed, this document would yield the following formatted citations:

```markdown
# Introduction

This document discusses various experiments. We will refer to several figures and tables.

In Experiment 1, we can see the results in Figures 1-2, 4. Also, Tables 1-2 provide important information.

Supplementary details can be found in Supplementary Figure 1 and Supplementary Table A.
```

## Functionality

### Supported Citation Formats

The filter recognizes the following citation prefixes:

- Figures: @fig:label (e.g., @fig:experiment1)
- Tables: @tbl:label (e.g., @tbl:results)
- Supplementary Figures: @supfig:label (e.g., @supfig:extra1)
- Supplementary Tables: @suptbl:label (e.g., @suptbl:appendixA)

### Formatting Behavior

- Singular and Plural:
  - A single citation for a figure outputs as "Figure 1".
  - Multiple figures will output as "Figures 1-2, 4".
- Range Handling:
  - For consecutive citations, it formats as "Figures 1-3".
  - Non-consecutive citations are separated by commas (e.g., "Figures 1, 3-4").

## Output File

The filter will also create a file named citations_list.txt containing all unique citation IDs used in the document, in the order of their appearance. This can be used to generate a sorted list of tables and figures based in quarto.

## Logging

The filter logs the processing of citations for debugging purposes. You can view the logs in your console or terminal if you run the script with logging enabled.

## Conclusion

The Figure-Table-Formatter streamlines the process of managing citations for figures and tables in your documents, ensuring a polished and professional presentation of your references. For any issues or feature requests, feel free to contribute or contact the maintainers.