# TEI Page Editor

This is a small app that runs on your own computer and opens in a web browser. It listens only on your computer, at `http://127.0.0.1:5001`.

## Before you start

Install Python 3.11 or newer if it is not already installed:

1. Go to [python.org/downloads](https://www.python.org/downloads/).
2. Download and install Python for your computer.
3. Close and reopen File Explorer (Windows) or Finder (macOS), then try the start script below.

The first time you start the app, it creates its private Python environment and installs Flask. This setup may need an internet connection. After that, starting and using the app does not need internet access.

## Start the app on Windows

1. Open the `tei_editor` folder in File Explorer.
2. Double-click `start.bat`.
3. Keep the black window open while you use the app. Your browser should open and show **TEI Page Editor**, with 30 editable lines in column **a**.
4. To stop the app, close the black window.

## Start the app on macOS

1. Open the `tei_editor` folder in Finder.
2. Double-click `start.command`.
3. If macOS asks you to confirm, Control-click `start.command`, choose **Open**, and confirm **Open**.
4. Keep the Terminal window open while you use the app. Your browser should open and show **TEI Page Editor**, with 30 editable lines in column **a**.
5. To stop the app, close the Terminal window.

## Saving your transcription

The editor saves automatically about one second after you stop typing. The status below the lines shows when the last save finished. If a save fails, an error appears there and your text remains in the boxes.

If you try to leave while edits are waiting to be saved, your browser will warn you. Stay on the page until the status says **Saved at ...**. Force-closing the browser or computer before a save finishes can lose the latest edits.

The first save creates `data/transcription.xml`. Before each later save, the previous XML file is copied to `data/transcription.xml.bak`. This is one rolling backup: it contains the version from immediately before the most recent save.

## Check the TEI file

The checker reports whether `data/transcription.xml` is well-formed XML, checks the TEI namespace and the expected page, column, and line numbering, then prints the element and line counts. It does not validate the file against a TEI schema.

1. Make sure the app setup has been run at least once.
2. Double-click `check.bat` on Windows or `check.command` on macOS.
3. Read the result in the window that opens, then press a key (or Return on macOS) to close it.

You can open `data/transcription.xml` in VS Code to inspect the saved text. Restart the app to confirm that the text loads again.

## If something goes wrong

Read the message in the app or the window opened by a double-clicked script. If Python is missing or too old, install Python 3.11 or newer and try again. If Flask cannot be installed on the first run, connect to the internet and double-click the start script again. If the editor cannot load an existing XML file, it will stop rather than replace that file; keep the original and ask for help before changing it.

