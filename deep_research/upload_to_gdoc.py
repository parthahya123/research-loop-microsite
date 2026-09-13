"""Upload synthesis.md from a deep research run to a new Google Doc."""

import json
import random
import re
import site
import sys
import os
import time

# Ensure user site-packages are on the path (needed in some sandboxed environments)
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import httplib2
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

AI_RESEARCH_FOLDER_NAME = "AI Research Outputs"

# Unique marker that won't appear in real content
TABLE_MARKER = "\u200b\u200bTBL\u200b\u200b"


def retry_api_call(fn, max_retries=3, base_delay=2.0):
    """Retry a Google API call with exponential backoff."""
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            if attempt == max_retries:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"  API error (attempt {attempt+1}/{max_retries+1}): {e}")
            print(f"  Retrying in {delay:.1f}s...")
            time.sleep(delay)


def get_credentials():
    """Load OAuth credentials from token.json at repo root, or run OAuth flow."""
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
    creds_path = os.path.join(os.path.dirname(__file__), "..", "credentials.json")
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())
    return creds


def get_or_create_folder(drive_service, folder_name):
    """Find an existing Drive folder by name, or create it. Returns folder ID."""
    query = (
        f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
        " and trashed = false"
    )
    results = retry_api_call(lambda: drive_service.files().list(
        q=query, spaces="drive", fields="files(id, name)", pageSize=1
    ).execute())
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    # Create the folder
    file_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = retry_api_call(lambda: drive_service.files().create(body=file_metadata, fields="id").execute())
    print(f"  Created Drive folder: {folder_name}")
    return folder["id"]


def move_to_folder(drive_service, file_id, folder_id):
    """Move a file into the specified Drive folder."""
    # Get current parents to remove
    f = retry_api_call(lambda: drive_service.files().get(fileId=file_id, fields="parents").execute())
    previous_parents = ",".join(f.get("parents", []))
    retry_api_call(lambda: drive_service.files().update(
        fileId=file_id,
        addParents=folder_id,
        removeParents=previous_parents,
        fields="id, parents",
    ).execute())


def parse_markdown_line(line):
    """Parse a line for bold and link markdown, return clean text and formatting ranges.

    Returns (clean_text, bold_ranges, link_ranges) where ranges are relative to line start.
    """
    bold_ranges = []
    link_ranges = []
    result_parts = []
    cursor = 0
    i = 0

    while i < len(line):
        # Check for bold marker **
        if line[i : i + 2] == "**":
            end_bold = line.find("**", i + 2)
            if end_bold != -1:
                bold_text = line[i + 2 : end_bold]
                bold_ranges.append({"start": cursor, "length": len(bold_text)})
                result_parts.append(bold_text)
                cursor += len(bold_text)
                i = end_bold + 2
                continue

        # Check for markdown link [text](url)
        if line[i] == "[":
            bracket_end = line.find("]", i + 1)
            if (
                bracket_end != -1
                and bracket_end + 1 < len(line)
                and line[bracket_end + 1] == "("
            ):
                paren_end = line.find(")", bracket_end + 2)
                if paren_end != -1:
                    link_text = line[i + 1 : bracket_end]
                    link_url = line[bracket_end + 2 : paren_end]
                    link_ranges.append(
                        {"start": cursor, "length": len(link_text), "url": link_url}
                    )
                    result_parts.append(link_text)
                    cursor += len(link_text)
                    i = paren_end + 1
                    continue

        result_parts.append(line[i])
        cursor += 1
        i += 1

    return "".join(result_parts), bold_ranges, link_ranges


def is_table_row(line):
    """Check if a line is a markdown table row (starts and ends with |)."""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 1


def is_separator_row(line):
    """Check if a line is a markdown table separator (e.g. |---|---|)."""
    stripped = line.strip()
    if not is_table_row(stripped):
        return False
    cells = [c.strip() for c in stripped.strip("|").split("|")]
    return all(re.match(r"^[-:]+$", c) for c in cells if c)


def parse_table_cells(line):
    """Parse a markdown table row into a list of cell text values."""
    stripped = line.strip().strip("|")
    return [c.strip() for c in stripped.split("|")]


def extract_tables_and_replace(text):
    """Replace markdown tables with placeholders. Return modified text and table data.

    Returns (modified_text, tables) where tables is a list of row-lists in order.
    """
    lines = text.split("\n")
    output_lines = []
    tables = []
    i = 0

    while i < len(lines):
        if is_table_row(lines[i]):
            table_rows = []
            while i < len(lines) and is_table_row(lines[i]):
                if not is_separator_row(lines[i]):
                    table_rows.append(parse_table_cells(lines[i]))
                i += 1
            if table_rows:
                tables.append(table_rows)
                output_lines.append(TABLE_MARKER)
        else:
            output_lines.append(lines[i])
            i += 1

    return "\n".join(output_lines), tables


def build_text_requests(text):
    """Build requests to insert and format text (no tables). Returns list of requests."""
    lines = text.split("\n")
    requests = []
    clean_lines = []
    formatting = []

    for line_idx, line in enumerate(lines):
        stripped = line.strip()

        heading_level = 0
        if stripped.startswith("###"):
            heading_level = 3
            stripped = stripped[3:].strip()
        elif stripped.startswith("##"):
            heading_level = 2
            stripped = stripped[2:].strip()
        elif stripped.startswith("#"):
            heading_level = 1
            stripped = stripped[1:].strip()

        clean_text, bold_ranges, link_ranges = parse_markdown_line(stripped)
        clean_lines.append(clean_text)
        if heading_level:
            formatting.append((line_idx, "heading", heading_level))
        for br in bold_ranges:
            formatting.append((line_idx, "bold", br))
        for lr in link_ranges:
            formatting.append((line_idx, "link", lr))

    full_text = "\n".join(clean_lines) + "\n"

    # Insert all text at index 1
    requests.append(
        {"insertText": {"location": {"index": 1}, "text": full_text}}
    )

    # Compute absolute positions
    line_starts = []
    pos = 1
    for cl in clean_lines:
        line_starts.append(pos)
        pos += len(cl) + 1

    for line_idx, fmt_type, info in formatting:
        line_start = line_starts[line_idx]
        line_end = line_start + len(clean_lines[line_idx])

        if fmt_type == "heading":
            style_map = {1: "HEADING_1", 2: "HEADING_2", 3: "HEADING_3"}
            requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": line_start, "endIndex": line_end},
                        "paragraphStyle": {"namedStyleType": style_map[info]},
                        "fields": "namedStyleType",
                    }
                }
            )
        elif fmt_type == "bold":
            abs_start = line_start + info["start"]
            abs_end = abs_start + info["length"]
            requests.append(
                {
                    "updateTextStyle": {
                        "range": {"startIndex": abs_start, "endIndex": abs_end},
                        "textStyle": {"bold": True},
                        "fields": "bold",
                    }
                }
            )
        elif fmt_type == "link":
            abs_start = line_start + info["start"]
            abs_end = abs_start + info["length"]
            requests.append(
                {
                    "updateTextStyle": {
                        "range": {"startIndex": abs_start, "endIndex": abs_end},
                        "textStyle": {
                            "link": {"url": info["url"]},
                            "foregroundColor": {
                                "color": {
                                    "rgbColor": {
                                        "red": 0.06,
                                        "green": 0.36,
                                        "blue": 0.72,
                                    }
                                }
                            },
                            "underline": True,
                        },
                        "fields": "link,foregroundColor,underline",
                    }
                }
            )

    return requests


def find_marker_paragraphs(doc):
    """Find all TABLE_MARKER placeholder paragraphs in the doc.

    Returns list of (startIndex, endIndex) for each marker paragraph.
    """
    results = []
    for element in doc.get("body", {}).get("content", []):
        if "paragraph" in element:
            for text_run in element["paragraph"].get("elements", []):
                text = text_run.get("textRun", {}).get("content", "")
                if TABLE_MARKER in text:
                    results.append((element["startIndex"], element["endIndex"]))
                    break
    return results


def find_tables_in_doc(doc):
    """Find all table elements in the doc with their cell paragraph indices and ranges.

    Returns list of dicts with:
      - cells: list of rows, each row is a list of paragraph startIndex values
      - start: table startIndex
      - end: table endIndex
      - num_rows: number of rows
      - num_cols: number of columns
    """
    tables = []
    for element in doc.get("body", {}).get("content", []):
        if "table" in element:
            table_cells = []
            for row in element["table"]["tableRows"]:
                row_cells = []
                for cell in row["tableCells"]:
                    para_start = cell["content"][0]["startIndex"]
                    row_cells.append(para_start)
                table_cells.append(row_cells)
            tables.append({
                "cells": table_cells,
                "start": element["startIndex"],
                "end": element["endIndex"],
                "num_rows": len(table_cells),
                "num_cols": len(table_cells[0]) if table_cells else 0,
            })
    return tables


def build_full_content(run_dir):
    """Assemble synthesis + all research files into one markdown document."""
    synthesis_path = os.path.join(run_dir, "synthesis.md")
    if not os.path.exists(synthesis_path):
        print(f"ERROR: {synthesis_path} not found. Has synthesis phase completed?")
        sys.exit(1)

    with open(synthesis_path, "r") as f:
        content = f.read().rstrip("\n")

    # Appendix files in order
    appendices = [
        ("Scale Research", os.path.join(run_dir, "research", "scale.md")),
        ("Cost Research", os.path.join(run_dir, "research", "cost.md")),
        ("Cost Decline Analysis", os.path.join(run_dir, "research", "cost_decline.md")),
        ("Timeline Research", os.path.join(run_dir, "research", "timeline.md")),
        ("Red Team Assessment", os.path.join(run_dir, "research", "red_team.md")),
        ("Evidence & Sources", os.path.join(run_dir, "research", "evidence.md")),
        ("Deepening Log", os.path.join(run_dir, "deepening_log.md")),
    ]

    appendix_sections = []
    for label, path in appendices:
        if os.path.exists(path):
            with open(path, "r") as f:
                body = f.read().strip()
            if body:
                appendix_sections.append(f"## Appendix: {label}\n\n{body}")

    if appendix_sections:
        content += "\n\n---\n\n# Appendices — Full Research\n\n"
        content += "\n\n---\n\n".join(appendix_sections)

    return content


def upload_single_markdown(content, title, folder_id, docs_service, drive_service):
    """Create a Google Doc from markdown content, move to folder, return URL.

    Uses a multi-pass approach for reliable table rendering:
    1. Extract markdown tables, replace with placeholder text
    2. Insert all text (with placeholders) and apply formatting
    3. Read doc, find marker positions, replace each with an empty table (reverse order)
    4. Read doc again, find actual cell indices from table elements
    5. Fill all table cells and apply cell formatting in one batch
    """
    # Create the doc
    doc = retry_api_call(lambda: docs_service.documents().create(body={"title": title}).execute())
    doc_id = doc["documentId"]

    # Move to folder
    move_to_folder(drive_service, doc_id, folder_id)

    # Step 1: Extract tables, replace with markers
    text_with_markers, tables = extract_tables_and_replace(content)
    print(f"  Found {len(tables)} tables to render")

    # Step 2: Insert text (with markers) and apply formatting
    text_requests = build_text_requests(text_with_markers)
    if text_requests:
        retry_api_call(lambda: docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": text_requests}
        ).execute())

    if not tables:
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
        return doc_url

    # Step 3: Read doc, find markers, replace with empty tables
    doc = retry_api_call(lambda: docs_service.documents().get(documentId=doc_id).execute())
    markers = find_marker_paragraphs(doc)

    if len(markers) != len(tables):
        print(
            f"  WARNING: Found {len(markers)} markers but {len(tables)} tables. "
            "Some tables may not render correctly."
        )

    # Build requests to delete markers and insert tables (reverse order)
    table_insert_requests = []
    paired = list(zip(markers, tables))
    paired.sort(key=lambda x: x[0][0], reverse=True)

    for (m_start, m_end), table_rows in paired:
        num_rows = len(table_rows)
        num_cols = max(len(r) for r in table_rows) if table_rows else 0

        table_insert_requests.append(
            {"deleteContentRange": {"range": {"startIndex": m_start, "endIndex": m_end}}}
        )
        table_insert_requests.append(
            {
                "insertTable": {
                    "rows": num_rows,
                    "columns": num_cols,
                    "location": {"index": m_start},
                }
            }
        )

    retry_api_call(lambda: docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": table_insert_requests}
    ).execute())
    print(f"  Inserted {len(tables)} empty tables")

    # Step 4: Read doc again to get actual cell indices
    doc = retry_api_call(lambda: docs_service.documents().get(documentId=doc_id).execute())
    doc_tables = find_tables_in_doc(doc)

    if len(doc_tables) != len(tables):
        print(
            f"  WARNING: Found {len(doc_tables)} tables in doc but expected {len(tables)}. "
            "Cell filling may be incorrect."
        )

    # Step 5: Fill all table cells in one batch
    fill_requests = []
    all_cell_ops = []

    for table_idx in range(min(len(doc_tables), len(tables))):
        cell_indices = doc_tables[table_idx]["cells"]
        cell_data = tables[table_idx]

        for r in range(len(cell_data)):
            if r >= len(cell_indices):
                break
            for c in range(len(cell_data[r])):
                if c >= len(cell_indices[r]):
                    break
                text = cell_data[r][c]
                if not text:
                    continue
                para_idx = cell_indices[r][c]
                clean_text, bold_ranges, link_ranges = parse_markdown_line(text)
                all_cell_ops.append({
                    "para_idx": para_idx,
                    "text": clean_text,
                    "bold_ranges": bold_ranges,
                    "link_ranges": link_ranges,
                    "is_header": r == 0,
                })

    all_cell_ops.sort(key=lambda x: x["para_idx"], reverse=True)

    for op in all_cell_ops:
            idx = op["para_idx"]
            text = op["text"]

            fill_requests.append(
                {"insertText": {"location": {"index": idx}, "text": text}}
            )

            if op["is_header"]:
                fill_requests.append(
                    {
                        "updateTextStyle": {
                            "range": {"startIndex": idx, "endIndex": idx + len(text)},
                            "textStyle": {"bold": True},
                            "fields": "bold",
                        }
                    }
                )

            for br in op["bold_ranges"]:
                abs_start = idx + br["start"]
                abs_end = abs_start + br["length"]
                fill_requests.append(
                    {
                        "updateTextStyle": {
                            "range": {"startIndex": abs_start, "endIndex": abs_end},
                            "textStyle": {"bold": True},
                            "fields": "bold",
                        }
                    }
                )

            for lr in op["link_ranges"]:
                abs_start = idx + lr["start"]
                abs_end = abs_start + lr["length"]
                fill_requests.append(
                    {
                        "updateTextStyle": {
                            "range": {"startIndex": abs_start, "endIndex": abs_end},
                            "textStyle": {
                                "link": {"url": lr["url"]},
                                "foregroundColor": {
                                    "color": {
                                        "rgbColor": {
                                            "red": 0.06,
                                            "green": 0.36,
                                            "blue": 0.72,
                                        }
                                    }
                                },
                                "underline": True,
                            },
                            "fields": "link,foregroundColor,underline",
                        }
                    }
                )

    if fill_requests:
        retry_api_call(lambda: docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": fill_requests}
        ).execute())
    print(f"  Filled {sum(len(t) for t in tables)} table rows")

    # Step 6: Read doc again for post-fill indices, then set font size + row height
    doc = retry_api_call(lambda: docs_service.documents().get(documentId=doc_id).execute())
    doc_tables_final = find_tables_in_doc(doc)

    PAGE_WIDTH_PT = 7.5 * 72  # 540 pt

    format_requests = []
    for tbl in doc_tables_final:
        format_requests.append(
            {
                "updateTextStyle": {
                    "range": {"startIndex": tbl["start"], "endIndex": tbl["end"]},
                    "textStyle": {"fontSize": {"magnitude": 10, "unit": "PT"}},
                    "fields": "fontSize",
                }
            }
        )

        num_cols = tbl["num_cols"]
        if num_cols > 0:
            col_width_pt = PAGE_WIDTH_PT / num_cols
            for c in range(num_cols):
                format_requests.append(
                    {
                        "updateTableColumnProperties": {
                            "tableStartLocation": {"index": tbl["start"]},
                            "columnIndices": [c],
                            "tableColumnProperties": {
                                "widthType": "FIXED_WIDTH",
                                "width": {"magnitude": col_width_pt, "unit": "PT"},
                            },
                            "fields": "widthType,width",
                        }
                    }
                )

        for r in range(tbl["num_rows"]):
            for c in range(tbl["num_cols"]):
                format_requests.append(
                    {
                        "updateTableCellStyle": {
                            "tableRange": {
                                "tableCellLocation": {
                                    "tableStartLocation": {"index": tbl["start"]},
                                    "rowIndex": r,
                                    "columnIndex": c,
                                },
                                "rowSpan": 1,
                                "columnSpan": 1,
                            },
                            "tableCellStyle": {
                                "paddingTop": {"magnitude": 1, "unit": "PT"},
                                "paddingBottom": {"magnitude": 1, "unit": "PT"},
                                "paddingLeft": {"magnitude": 3, "unit": "PT"},
                                "paddingRight": {"magnitude": 3, "unit": "PT"},
                            },
                            "fields": "paddingTop,paddingBottom,paddingLeft,paddingRight",
                        }
                    }
                )

        format_requests.append(
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": tbl["start"], "endIndex": tbl["end"]},
                    "paragraphStyle": {
                        "spaceAbove": {"magnitude": 0, "unit": "PT"},
                        "spaceBelow": {"magnitude": 0, "unit": "PT"},
                        "lineSpacing": 100,
                    },
                    "fields": "spaceAbove,spaceBelow,lineSpacing",
                }
            }
        )

    if format_requests:
        retry_api_call(lambda: docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": format_requests}
        ).execute())
    print(f"  Applied table formatting (font 10pt, fit to page)")

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_url


def build_summary_content(run_dir, full_doc_url):
    """Build summary content: just synthesis.md + a link to the full doc."""
    synthesis_path = os.path.join(run_dir, "synthesis.md")
    if not os.path.exists(synthesis_path):
        print(f"ERROR: {synthesis_path} not found. Has synthesis phase completed?")
        sys.exit(1)

    with open(synthesis_path, "r") as f:
        content = f.read().rstrip("\n")

    content += f"\n\n---\n\n**Full research with appendices:** [View full document]({full_doc_url})"
    return content


def upload(run_dir):
    """Create two Google Docs (summary + full) and print their URLs."""
    config_path = os.path.join(run_dir, "config.json")

    with open(config_path, "r") as f:
        config = json.load(f)

    content = build_full_content(run_dir)
    topic = config.get("topic", config.get("sc_label", "Unknown"))

    # Save local copy
    local_path = os.path.join(run_dir, "full_document.md")
    with open(local_path, "w") as f:
        f.write(content)
    print(f"  Saved local copy: {local_path}")

    creds = get_credentials()
    http = httplib2.Http(timeout=300)
    authorized_http = AuthorizedHttp(creds, http=http)
    docs_service = build("docs", "v1", http=authorized_http)
    drive_service = build("drive", "v3", http=authorized_http)

    folder_id = get_or_create_folder(drive_service, AI_RESEARCH_FOLDER_NAME)

    # 1. Upload full doc (with appendices)
    full_title = f"Deep Research (Full): {topic}"
    print(f"  Uploading full doc...")
    full_doc_url = upload_single_markdown(
        content, full_title, folder_id, docs_service, drive_service
    )
    print(f"Full doc created: {full_doc_url}")

    # Save full URL
    with open(os.path.join(run_dir, "full_doc_url.txt"), "w") as f:
        f.write(full_doc_url + "\n")

    # 2. Upload summary doc (synthesis only + link to full)
    summary_content = build_summary_content(run_dir, full_doc_url)
    summary_title = f"Deep Research (Summary): {topic}"
    print(f"  Uploading summary doc...")
    summary_doc_url = upload_single_markdown(
        summary_content, summary_title, folder_id, docs_service, drive_service
    )
    print(f"Summary doc created: {summary_doc_url}")

    # Save summary URL (primary shareable link)
    with open(os.path.join(run_dir, "doc_url.txt"), "w") as f:
        f.write(summary_doc_url + "\n")

    return summary_doc_url


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python upload_to_gdoc.py <run_dir>")
        sys.exit(1)
    upload(sys.argv[1])
