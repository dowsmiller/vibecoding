"""Check the saved transcription's XML and the editor's expected structure."""

from pathlib import Path
import string
import xml.etree.ElementTree as ET

TEI_NAMESPACE = "http://www.tei-c.org/ns/1.0"
NAMESPACES = {"tei": TEI_NAMESPACE}
TRANSCRIPTION_FILE = Path(__file__).resolve().parent / "data" / "transcription.xml"


def tei_tag(name: str) -> str:
    """Return an element name in the TEI namespace."""
    return f"{{{TEI_NAMESPACE}}}{name}"


def local_name(tag: object) -> str:
    """Return the readable name from a namespaced XML element."""
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def column_label(index: int) -> str:
    """Return alphabetic column labels: a through z, then aa, ab, and so on."""
    label = ""
    while index >= 0:
        label = string.ascii_lowercase[index % 26] + label
        index = index // 26 - 1
    return label


def check_tree(root: ET.Element) -> tuple[list[str], dict[str, int], list[tuple[str, int]]]:
    """Return structural problems, marker counts, and lines found per column."""
    problems = []
    markers = {
        name: [element for element in root.iter() if local_name(element.tag) == name]
        for name in ("pb", "cb", "lb")
    }
    counts = {name: len(elements) for name, elements in markers.items()}

    if root.tag != tei_tag("TEI"):
        problems.append("The root element must be TEI in the TEI namespace.")

    for name, elements in markers.items():
        for element in elements:
            if element.tag != tei_tag(name):
                problems.append(f"A <{name}/> element is not in the TEI namespace.")

    if counts["pb"] != 1:
        problems.append(f"There must be exactly one <pb/> element; found {counts['pb']}.")
    if counts["cb"] < 1:
        problems.append("There must be at least one <cb/> element.")

    paragraphs = root.findall("./tei:text/tei:body/tei:div/tei:p", NAMESPACES)
    if len(paragraphs) != 1:
        problems.append(
            "There must be exactly one transcription paragraph at text/body/div/p."
        )

    line_counts = []
    if len(paragraphs) == 1:
        paragraph = paragraphs[0]
        parents = {
            child: parent
            for parent in root.iter()
            for child in parent
        }

        def is_inside_transcription_paragraph(element: ET.Element) -> bool:
            parent = parents.get(element)
            while parent is not None:
                if parent is paragraph:
                    return True
                parent = parents.get(parent)
            return False

        for name in ("cb", "lb"):
            for element in markers[name]:
                if not is_inside_transcription_paragraph(element):
                    problems.append(
                        f"A <{name}/> element is outside the transcription paragraph."
                    )

        for element in markers["pb"]:
            if not is_inside_transcription_paragraph(element):
                problems.append(
                    "The <pb/> element is outside the transcription paragraph."
                )

        columns = []
        current_column = None
        for element in paragraph.iter():
            name = local_name(element.tag)
            if name == "cb":
                expected_label = column_label(len(columns))
                actual_label = element.get("n", "")
                if actual_label != expected_label:
                    problems.append(
                        f"Column {len(columns) + 1} must be labelled "
                        f"{expected_label}; found {actual_label or 'no label'}."
                    )
                columns.append((actual_label or expected_label, 0))
                current_column = len(columns) - 1
            elif name == "lb":
                if current_column is None:
                    problems.append("A <lb/> appears before the first <cb/>.")
                    continue

                expected_number = columns[current_column][1] + 1
                actual_number = element.get("n", "")
                if actual_number != str(expected_number):
                    label = columns[current_column][0]
                    problems.append(
                        f"Line {expected_number} in column {label} must be numbered "
                        f"{expected_number}; found {actual_number or 'no number'}."
                    )
                label, line_count = columns[current_column]
                columns[current_column] = (label, line_count + 1)

        if not columns:
            problems.append("The transcription paragraph must contain a <cb/> element.")
        for label, line_count in columns:
            if line_count == 0:
                problems.append(f"Column {label} must contain at least one <lb/> line.")
        line_counts = columns

    return problems, counts, line_counts


def check_file(path: Path = TRANSCRIPTION_FILE) -> int:
    """Check one XML file and print the results in plain English."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        print(f"The file is not well-formed XML: {error}")
        return 1
    except OSError as error:
        print(f"Could not read {path}: {error}")
        return 1

    print("The file is well-formed XML.")
    problems, counts, line_counts = check_tree(root)

    if problems:
        for problem in problems:
            print(f"Problem: {problem}")
    else:
        print("The TEI structure checks passed.")

    print(
        f"Found {counts['pb']} <pb/>, {counts['cb']} <cb/>, "
        f"and {counts['lb']} <lb/> elements."
    )
    if line_counts:
        for label, line_count in line_counts:
            print(f"Column {label}: {line_count} lines.")
    else:
        print("No transcription columns could be counted.")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(check_file())
