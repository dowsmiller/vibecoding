# TEI Page Editor: Build Plan

## Goal

Build a small web app that runs on my own laptop and lets me transcribe one manuscript page into TEI-XML. I type in the browser, and the app saves my work to a TEI file automatically.

## Who it's for

I am a medievalist with no coding experience. Setting up and running the app must take as few steps as possible, and everything you do must be explained to me in plain English.

## Technical decisions (do not deviate)

- Python 3.11 or newer, with **Flask** as the only third-party package. Use the standard library (`xml.etree.ElementTree`) for XML. Ask me before adding any other package.
- Plain HTML, CSS, and vanilla JavaScript. No JavaScript frameworks, no build tools, no database, no accounts, no API keys, and no internet connection needed at runtime.
- Put everything inside a folder called `tei_editor/`. Do not create or modify anything outside it.
- Use a virtual environment at `tei_editor/.venv`, with dependencies pinned in `requirements.txt`.
- The server must listen on `127.0.0.1` only, so that nobody else on the network can reach it.
- Save the data to `tei_editor/data/transcription.xml`, encoded as UTF-8.

## Behaviour

1. On first launch, the editor shows one page with one column of 30 empty, numbered lines.
2. Each line is a single-line text box. Columns sit side by side and are labelled a, b, c, and so on.
3. I can add and remove lines (within a column) and add and remove columns. Line numbers update automatically and restart at 1 in each column. Ask for confirmation before removing anything that contains text. Always keep at least one column and one line.
4. **Autosave:** save about one second after I stop typing, and immediately after any structural change. Show "Saved at HH:MM:SS" on screen. If saving fails, show a clear error message. Never fail silently.
5. Before each save, copy the previous file to `transcription.xml.bak`.
6. On startup, load `transcription.xml` if it exists, so my work carries over between sessions.
7. Keep my text exactly as typed, apart from trimming leading and trailing spaces on each line. Characters such as `<`, `>`, `&`, accented letters, and combining or medieval characters must survive saving and reloading unchanged. Never normalise Unicode.

## TEI output

Use this structure. Each `<lb/>` goes on its own line, with the line's text immediately after it.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt><title>Untitled transcription</title></titleStmt>
      <publicationStmt><p>Unpublished</p></publicationStmt>
      <sourceDesc><p>Born-digital transcription</p></sourceDesc>
    </fileDesc>
  </teiHeader>
  <text>
    <body>
      <div>
        <p>
          <pb n="1"/>
          <cb n="a"/>
          <lb n="1"/>First line of column a
          <lb n="2"/>Second line of column a
          <cb n="b"/>
          <lb n="1"/>First line of column b
        </p>
      </div>
    </body>
  </text>
</TEI>
```

Empty lines still get an `<lb n="…"/>` element. If you are unsure whether any markup is valid TEI, tell me rather than guessing.

## Build phases

Work through the phases in order. **Stop at the end of each phase** and wait for me.

**Phase 1: Setup and "hello world"**
Create `tei_editor/` with a virtual environment, `requirements.txt` (Flask, version pinned), a `.gitignore` (excluding `.venv/`, `__pycache__/`, and `*.bak`), and a minimal `app.py` that shows a page saying "TEI editor is running". Add a start script that I run by double-clicking: `start.bat` (Windows) and `start.command` (macOS, made executable). It must work from any location by first changing to its own folder. It must check that Python 3.11 or newer is installed, and say so in plain English if not. On first run it creates the virtual environment and installs requirements. It starts the app on port 5001 (not 5000, which macOS uses for AirPlay), opens it in my browser, and if anything fails it keeps the window open so I can read the message. Write a short `README.md` explaining, step by step, how to start the app on each system.
*My check: I double-click the start script and see the page in my browser.*

**Phase 2: The page layout**
Show one column of 30 numbered, editable lines. No saving yet.
*My check: I can type in every line, and the layout is readable.*

**Phase 3: Saving to TEI**
Add autosave, TEI generation, the backup file, the on-screen save status, and loading on startup. Also write `check_tei.py` and a double-clickable `check.bat` / `check.command` that runs it, shows the result, and waits for a key press. It reports whether `data/transcription.xml` is well-formed XML. It then checks the structure and reports each problem in plain English: there is exactly one `<pb/>`; there is at least one `<cb/>`; every `<cb/>` and `<lb/>` sits inside the `<p>`; columns are labelled a, b, c in order; and each column's lines are numbered 1, 2, 3 with no gaps or repeats. Finally, it prints the number of `<pb/>`, `<cb/>`, and `<lb/>` elements, and the number of lines in each column.
*My check: I type text, open the XML file in VS Code, double-click the check script, and restart the app to confirm my text is still there.*

**Phase 4: Editing the structure**
Add and remove lines and columns, with confirmation for anything non-empty, and keep the TEI file in sync.
*My check: the line and column counts reported by `check_tei.py` match what I see on screen after every change.*

**Phase 5: Robustness**
Test the edge cases: empty lines, `<` and `&`, accented and combining characters, very long lines, rapid typing, removing the last column or line, and a restart in the middle of editing. Fix anything that breaks. Update `README.md` for a non-programmer.
*My check: nothing is lost, and every error is visible.*

## Working rules for the agent

- Complete one phase at a time and stop at the end of each.
- Run all terminal commands yourself: do not assume that I know how to use the terminal.
- At each stop, tell me in plain English: which files you changed and why, how I can run and test the result, what you tested yourself, and any choice you made on my behalf. Remind me to review the changes and commit them in GitHub Desktop before we continue.
- Do not add features, files, or packages that are not in this plan. Ask first.
- If anything in this plan is ambiguous or contradictory, ask me instead of guessing.
- Write simple, readable code with comments aimed at a non-programmer, in small functions.
- Never catch an error and hide it. Report it visibly.
- Never delete or overwrite my transcription without keeping a backup.
- Do not commit or push to Git. I will do that myself in GitHub Desktop.
- Before running any terminal command, explain what it does.

## Out of scope (for now)

Multiple pages and page navigation, displaying a facsimile image, editing the TEI header, schema validation, other export formats, user accounts, and putting the app online.