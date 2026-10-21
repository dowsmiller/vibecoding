I'm a medievalist with little or no coding experience. I want to build a small tool with an AI coding agent (GitHub Copilot in VS Code, agent mode). Help me write a build plan for the agent.

The tool: a TEI-XML transcription editor that runs in my web browser using Python and Flask. It shows one manuscript page, starting with one column of 30 lines, lets me add and remove lines and columns, and autosaves to a TEI file.

My decisions so far: [your decisions list]

Before you draft anything, ask me up to five questions about anything unclear or unspecified. Wait for my answers.

Then draft the plan as a single Markdown document with these sections: Goal; Who it's for; Technical decisions (language, packages, folder structure, and what NOT to use); Behaviour (numbered and testable); Output format (with an example); Build phases (small, each with a check I can do myself); Working rules for the agent; Out of scope.

Requirements:
- Phase 1 must get me from nothing to a running (even if trivial) app in the fewest possible steps: a single start script, exact commands for [Windows / macOS], and everything I need to install explained in plain English.
- Each phase ends with the agent stopping, so I can run it, check it, and save a version before continuing.
- Use only the packages we've agreed. Where you would have to make a choice I haven't specified, list it for me instead of choosing.

After the draft, list the five places where an agent would most likely have to guess or improvise, and suggest how to close each gap.