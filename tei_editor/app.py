"""The TEI page editor."""

from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import tempfile
from threading import Lock, Timer
import webbrowser
import xml.etree.ElementTree as ET

from flask import Flask, jsonify, render_template, request

TEI_NAMESPACE = "http://www.tei-c.org/ns/1.0"
NAMESPACES = {"tei": TEI_NAMESPACE}
APP_FOLDER = Path(__file__).resolve().parent
TRANSCRIPTION_FILE = APP_FOLDER / "data" / "transcription.xml"

ET.register_namespace("", TEI_NAMESPACE)

app = Flask(__name__)
SAVE_LOCK = Lock()


class TranscriptionLoadError(Exception):
    """The existing file cannot safely be loaded into this editor."""


def tei_tag(name: str) -> str:
    """Return an element name in the TEI namespace."""
    return f"{{{TEI_NAMESPACE}}}{name}"


def xml_local_name(element: ET.Element) -> str:
    """Return an element's name without its XML namespace."""
    if not isinstance(element.tag, str):
        return ""
    return element.tag.rsplit("}", 1)[-1]


def column_label(index: int) -> str:
    """Return alphabetic column labels: a through z, then aa, ab, and so on."""
    label = ""
    while index >= 0:
        label = chr(ord("a") + index % 26) + label
        index = index // 26 - 1
    return label


def line_text_from_element(element: ET.Element) -> str:
    """Read the text that follows an empty line-break element."""
    if len(element) or element.text is not None:
        raise TranscriptionLoadError("A line-break element contains unexpected content.")

    text_and_formatting = element.tail or ""
    line_text, separator, formatting = text_and_formatting.partition("\n")
    if separator and formatting.strip():
        raise TranscriptionLoadError("There is unexpected content after a line.")
    return line_text


def load_transcription(
    path: Path = TRANSCRIPTION_FILE,
) -> tuple[list[list[str]], bool]:
    """Load the transcription, or start with one column of 30 blank lines."""
    try:
        root = ET.parse(path).getroot()
    except FileNotFoundError:
        return [[""] * 30], False
    except (ET.ParseError, OSError) as error:
        raise TranscriptionLoadError(str(error)) from error

    if root.tag != tei_tag("TEI"):
        raise TranscriptionLoadError("The root element is not TEI in the TEI namespace.")

    paragraphs = root.findall("./tei:text/tei:body/tei:div/tei:p", NAMESPACES)
    if len(paragraphs) != 1:
        raise TranscriptionLoadError(
            "The file must contain one transcription paragraph at text/body/div/p."
        )

    paragraph = paragraphs[0]
    if paragraph.text and paragraph.text.strip():
        raise TranscriptionLoadError("There is unexpected text before the page marker.")

    children = list(paragraph)
    if len(children) < 3 or children[0].tag != tei_tag("pb"):
        raise TranscriptionLoadError("The paragraph must start with one page marker.")
    if children[0].get("n") != "1":
        raise TranscriptionLoadError("The page marker must be numbered 1.")
    if any(child.tag not in {tei_tag("cb"), tei_tag("lb")} for child in children[1:]):
        raise TranscriptionLoadError("The paragraph contains unsupported markup.")

    marker_names = {"pb", "cb", "lb"}
    expected_markers = [child.tag for child in children]
    actual_markers = [
        element.tag
        for element in root.iter()
        if xml_local_name(element) in marker_names
    ]
    if actual_markers != expected_markers:
        raise TranscriptionLoadError("The file contains page or line markers outside the paragraph.")

    if sum(xml_local_name(element) == "pb" for element in root.iter()) != 1:
        raise TranscriptionLoadError("The transcription must contain exactly one page marker.")

    for element in children[:2]:
        if len(element) or element.text is not None:
            raise TranscriptionLoadError("A page or column marker contains unexpected content.")

    columns = []
    current_column = None
    for element in children[1:]:
        if element.tag == tei_tag("cb"):
            expected_label = column_label(len(columns))
            if element.get("n") != expected_label:
                raise TranscriptionLoadError(
                    f"Column {len(columns) + 1} must be labelled {expected_label}."
                )
            columns.append([])
            current_column = columns[-1]
        else:
            if current_column is None:
                raise TranscriptionLoadError("A line appears before the first column marker.")
            expected_number = len(current_column) + 1
            if element.get("n") != str(expected_number):
                raise TranscriptionLoadError(
                    f"Line {expected_number} in column {column_label(len(columns) - 1)} "
                    f"must be numbered {expected_number}."
                )
            current_column.append(line_text_from_element(element))

    if not columns or any(not column for column in columns):
        raise TranscriptionLoadError("Every column must contain at least one line.")

    return columns, True


def is_xml_character(character: str) -> bool:
    """Check that a character is allowed in an XML 1.0 document."""
    codepoint = ord(character)
    return (
        codepoint in (0x9, 0xA, 0xD)
        or 0x20 <= codepoint <= 0xD7FF
        or 0xE000 <= codepoint <= 0xFFFD
        or 0x10000 <= codepoint <= 0x10FFFF
    )


def build_transcription_xml(columns: list[list[str]]) -> bytes:
    """Build the page's TEI XML without normalising the line text."""
    if not columns or any(not column for column in columns):
        raise ValueError("The transcription must contain at least one line in every column.")

    for column_number, column in enumerate(columns, start=1):
        for line_number, line in enumerate(column, start=1):
            if any(not is_xml_character(character) for character in line):
                raise ValueError(
                    f"Line {line_number} in column {column_label(column_number - 1)} "
                    "contains a character that XML cannot store."
                )

    root = ET.Element(tei_tag("TEI"))
    header = ET.SubElement(root, tei_tag("teiHeader"))
    file_description = ET.SubElement(header, tei_tag("fileDesc"))
    title_statement = ET.SubElement(file_description, tei_tag("titleStmt"))
    ET.SubElement(title_statement, tei_tag("title")).text = "Untitled transcription"
    publication_statement = ET.SubElement(file_description, tei_tag("publicationStmt"))
    ET.SubElement(publication_statement, tei_tag("p")).text = "Unpublished"
    source_description = ET.SubElement(file_description, tei_tag("sourceDesc"))
    ET.SubElement(source_description, tei_tag("p")).text = "Born-digital transcription"

    text = ET.SubElement(root, tei_tag("text"))
    body = ET.SubElement(text, tei_tag("body"))
    division = ET.SubElement(body, tei_tag("div"))
    paragraph = ET.SubElement(division, tei_tag("p"))
    ET.SubElement(paragraph, tei_tag("pb"), {"n": "1"})

    line_elements = []
    for column_number, column in enumerate(columns):
        ET.SubElement(paragraph, tei_tag("cb"), {"n": column_label(column_number)})
        for line_number, line in enumerate(column, start=1):
            element = ET.SubElement(
                paragraph, tei_tag("lb"), {"n": str(line_number)}
            )
            line_elements.append((element, line))

    ET.indent(root, space="  ")
    for number, (element, line) in enumerate(line_elements, start=1):
        indentation = "\n        " if number == len(line_elements) else "\n          "
        element.tail = line.strip(" ") + indentation

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def save_transcription(
    columns: list[list[str]], path: Path | None = None
) -> list[list[str]]:
    """Back up and safely replace the TEI file; return the saved, trimmed lines."""
    if path is None:
        path = TRANSCRIPTION_FILE

    saved_columns = [
        [line.strip(" ") for line in column]
        for column in columns
    ]
    xml_bytes = build_transcription_xml(saved_columns)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        shutil.copy2(path, path.with_name(f"{path.name}.bak"))

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=".transcription-",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(xml_bytes)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    return saved_columns


try:
    CURRENT_COLUMNS, HAS_SAVED_TRANSCRIPTION = load_transcription()
except TranscriptionLoadError as error:
    raise SystemExit(
        "ERROR: The existing transcription could not be loaded safely, so the editor "
        "has not opened or overwritten it.\n"
        f"Details: {error}"
    )


@app.get("/")
def home():
    """Show the current transcription."""
    return render_template(
        "index.html",
        columns=CURRENT_COLUMNS,
        column_labels=[column_label(index) for index in range(len(CURRENT_COLUMNS))],
        has_saved_transcription=HAS_SAVED_TRANSCRIPTION,
    )


@app.post("/save")
def save():
    """Save the current lines and return a visible status message."""
    global HAS_SAVED_TRANSCRIPTION

    if not request.is_json:
        return jsonify(error="The browser sent an invalid save request. Please try again."), 400

    try:
        payload = json.loads(request.get_data(as_text=True))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return jsonify(error="The browser sent an unreadable save request. Please try again."), 400

    if not isinstance(payload, dict) or not isinstance(payload.get("columns"), list):
        return jsonify(error="The transcription columns could not be read. Please try again."), 400

    columns = payload["columns"]
    if not columns or any(not isinstance(column, list) or not column for column in columns):
        return jsonify(error="Every column must contain at least one line."), 400
    if any(not isinstance(line, str) for column in columns for line in column):
        return jsonify(error="Every transcription line must be text."), 400

    with SAVE_LOCK:
        try:
            saved_columns = save_transcription(columns)
        except (OSError, UnicodeError, ValueError) as error:
            return jsonify(error=f"Could not save the transcription: {error}"), 500

        CURRENT_COLUMNS[:] = saved_columns
        HAS_SAVED_TRANSCRIPTION = True

    saved_at = datetime.now().astimezone().strftime("%H:%M:%S")
    return jsonify(saved_at=saved_at)


if __name__ == "__main__":
    # Give Flask a moment to start before opening the page in the browser.
    Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5001")).start()
    app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)
