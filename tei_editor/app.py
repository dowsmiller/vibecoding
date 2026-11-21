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


def line_text_from_element(element: ET.Element) -> str:
    """Read the text that follows an empty line-break element."""
    if len(element) or element.text is not None:
        raise TranscriptionLoadError("A line-break element contains unexpected content.")

    text_and_formatting = element.tail or ""
    line_text, separator, formatting = text_and_formatting.partition("\n")
    if separator and formatting.strip():
        raise TranscriptionLoadError("There is unexpected content after a line.")
    return line_text


def load_transcription(path: Path = TRANSCRIPTION_FILE) -> tuple[list[str], bool]:
    """Load this editor's single-column transcription, or start with 30 blank lines."""
    try:
        root = ET.parse(path).getroot()
    except FileNotFoundError:
        return [""] * 30, False
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
    if children[1].tag != tei_tag("cb") or children[1].get("n") != "a":
        raise TranscriptionLoadError("This phase can load only column a.")
    if children[0].get("n") != "1":
        raise TranscriptionLoadError("The page marker must be numbered 1.")
    if any(child.tag != tei_tag("lb") for child in children[2:]):
        raise TranscriptionLoadError("The paragraph contains unsupported markup.")
    if not children[2:]:
        raise TranscriptionLoadError("The transcription must contain at least one line.")

    expected_markers = [tei_tag("pb"), tei_tag("cb"), *([tei_tag("lb")] * (len(children) - 2))]
    actual_markers = [
        element.tag
        for element in root.iter()
        if element.tag in {tei_tag("pb"), tei_tag("cb"), tei_tag("lb")}
    ]
    if actual_markers != expected_markers:
        raise TranscriptionLoadError("The file contains page or line markers outside the paragraph.")

    lines = []
    for number, element in enumerate(children[2:], start=1):
        if element.get("n") != str(number):
            raise TranscriptionLoadError(
                f"Line {number} must have the line number {number}."
            )
        lines.append(line_text_from_element(element))

    return lines, True


def is_xml_character(character: str) -> bool:
    """Check that a character is allowed in an XML 1.0 document."""
    codepoint = ord(character)
    return (
        codepoint in (0x9, 0xA, 0xD)
        or 0x20 <= codepoint <= 0xD7FF
        or 0xE000 <= codepoint <= 0xFFFD
        or 0x10000 <= codepoint <= 0x10FFFF
    )


def build_transcription_xml(lines: list[str]) -> bytes:
    """Build the page's TEI XML without normalising the line text."""
    for number, line in enumerate(lines, start=1):
        if any(not is_xml_character(character) for character in line):
            raise ValueError(f"Line {number} contains a character that XML cannot store.")

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
    ET.SubElement(paragraph, tei_tag("cb"), {"n": "a"})

    line_elements = []
    for number in range(1, len(lines) + 1):
        line_elements.append(
            ET.SubElement(paragraph, tei_tag("lb"), {"n": str(number)})
        )

    ET.indent(root, space="  ")
    for number, (element, line) in enumerate(zip(line_elements, lines), start=1):
        indentation = "\n        " if number == len(lines) else "\n          "
        element.tail = line.strip(" ") + indentation

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def save_transcription(
    lines: list[str], path: Path | None = None
) -> list[str]:
    """Back up and safely replace the TEI file; return the saved, trimmed lines."""
    if path is None:
        path = TRANSCRIPTION_FILE

    saved_lines = [line.strip(" ") for line in lines]
    xml_bytes = build_transcription_xml(saved_lines)
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

    return saved_lines


try:
    CURRENT_LINES, HAS_SAVED_TRANSCRIPTION = load_transcription()
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
        lines=CURRENT_LINES,
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

    if not isinstance(payload, dict) or not isinstance(payload.get("lines"), list):
        return jsonify(error="The transcription lines could not be read. Please try again."), 400

    lines = payload["lines"]
    if any(not isinstance(line, str) for line in lines):
        return jsonify(error="Every transcription line must be text."), 400

    with SAVE_LOCK:
        if len(lines) != len(CURRENT_LINES):
            return jsonify(error="The number of lines changed unexpectedly. Reload the page."), 400

        try:
            saved_lines = save_transcription(lines)
        except (OSError, UnicodeError, ValueError) as error:
            return jsonify(error=f"Could not save the transcription: {error}"), 500

        CURRENT_LINES[:] = saved_lines
        HAS_SAVED_TRANSCRIPTION = True

    saved_at = datetime.now().astimezone().strftime("%H:%M:%S")
    return jsonify(saved_at=saved_at)


if __name__ == "__main__":
    # Give Flask a moment to start before opening the page in the browser.
    Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5001")).start()
    app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)
