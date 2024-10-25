# Figure-Table-Formatter Quarto Filter

## Overview

The Figure-Table-Formatter is a Quarto filter designed to format cross-references for figures, supplementary figures, tables, and supplementary tables, ensuring they are numbered sequentially throughout the document. The filter now includes enhanced features for sorting and inserting figures/tables at specific points using placeholders, and allows optional input of pre-defined figure/table orders from an external file.

### Key Features

- **Support for Multiple Citation Types**: Recognizes citation prefixes for figures (`fig:`), supplementary figures (`supfig:`), tables (`tbl:`), and supplementary tables (`suptbl:`).
- **Intelligent Formatting**: Automatically adjusts citation formats to handle singular vs. plural references and manages ranges (e.g., "Figures 1-2, 4").
- **Duplicate Citation Removal**: Automatically filters out duplicate citations within the same reference set.
- **Maintains Citation Order**: Ensures that unique citations are formatted in the order they appear in the document.
- **Flexible Placeholder Insertion**: Allows figures and tables to be inserted at specific locations using placeholders, with optional page breaks between entries.
- **Custom Figure/Table Order**: You can provide a custom order for figures and tables via an external file (`sorted_ids.txt`) for flexibility.
- **Automatic Output of Object Order**: The script generates a `sorted_ids.txt` file listing the order of figures and tables as they are processed, which can be reused in other documents for consistency.
- **Citation Logging**: Logs all citation IDs to a file for reference.

## Usage

To apply the filter to your Pandoc document, use this command:

```bash
quarto add iagopinal/figure-table-formatter
```

### Automatic Generation of Object Order

If no custom order file is provided, the filter will automatically generate a `sorted_ids.txt` file containing the figure and table IDs in the order they were processed. This file can be used to replicate the same order of objects in another document, ensuring consistency across multiple projects.

## Example YAML Front Matter

Here’s an example of a YAML front matter for a Markdown document using the Figure-Table-Formatter filter. Ensure the Python script is executable (e.g., `chmod 744 figure_table_formatter.py`).

```markdown
---
filters:
  - iagopinal/figure_table_formatter
---

# Introduction

This document discusses several experiments. We will refer to various figures and tables.

In Experiment 1, we can see the results in @fig:experiment1 and @fig:experiment2. Also, @fig:experiment4 illustrates an important finding.

The analysis is summarized in @tbl:results and detailed further in @tbl:summary.

Supplementary details can be found in @supfig:extra1 and @suptbl:appendixA.
```

After processing, the document will format the citations like this:

```markdown
# Introduction

This document discusses several experiments. We will refer to various figures and tables.

In Experiment 1, we can see the results in Figures 1-2, 4. Also, Tables 1-2 provide important information.

Supplementary details can be found in Supplementary Figure 1 and Supplementary Table A.
```

### Flexible Ordering with Placeholders

The filter supports placing figures and tables at specific points in the document using placeholders in the format `&&&tag&&&`. This feature allows you to control where different types of objects (figures, tables) should be inserted.

#### Placeholder Logic:

- **Dashes for Sequential Textual Order**: Use a dash (`-`) to intersperse different types of objects based on the order in which they were referenced. For example, `&&&fig-tbl&&&` will insert figures and tables in the order they were referenced within the document.
- **Commas for Exact Object Control**: Use commas (`,`) to control the specific objects and their exact insertion order. For example, `&&&fig1,tbl1&&&` will insert Figure 1 and Table 1 in the exact order in which they were referenced.
  
  **Example**: `&&&fig-tbl,supfig,suptbl&&&` will:
  - Insert the referenced figures and tables interspersed, 
  - Followed by supplementary figures, 
  - And finally, insert the supplementary tables.

This approach allows for flexible and customized placement of figures and tables in the document.

### Sorting and Custom Order Input

If you need a custom order for figures and tables, you can provide it via the `sorted_ids.txt` file. This file should list the figures and tables in the desired order:

```
fig:experiment1
tbl:results
supfig:extra1
suptbl:appendixA
```

When this file is provided, the filter will use the specified order to arrange the figures and tables accordingly.

### Supported Citation Formats

The filter recognizes the following citation prefixes:

- **Figures**: `@fig:label` (e.g., `@fig:experiment1`)
- **Tables**: `@tbl:label` (e.g., `@tbl:results`)
- **Supplementary Figures**: `@supfig:label` (e.g., `@supfig:extra1`)
- **Supplementary Tables**: `@suptbl:label` (e.g., `@suptbl:appendixA`)

### Formatting Behavior

- **Singular vs. Plural**:
  - Single figure citations will output as "Figure 1".
  - Multiple figures will be output as "Figures 1-2, 4".
- **Range Handling**:
  - Consecutive citations are formatted as a range, e.g., "Figures 1-3".
  - Non-consecutive citations are separated by commas, e.g., "Figures 1, 3-4".

## Output Files

The filter generates two output files:
- `sorted_ids.txt`: Lists all unique citation IDs used in the document, in either their order of appearance or as defined in a custom order file. This can be reused across documents.
- `figure_table_list.txt`: Provides a list of all unique citation IDs for further reference or processing.

## Logging

The filter logs all citation processing and figure/table placements, which can be viewed in the terminal when the script is executed with logging enabled.

## Conclusion

The Figure-Table-Formatter is a robust tool that simplifies citation management for figures and tables in Quarto documents. It offers flexible placement, sorting options, and ensures that all references are formatted consistently and professionally. If you encounter issues or have feature requests, feel free to contribute or contact the maintainers.
