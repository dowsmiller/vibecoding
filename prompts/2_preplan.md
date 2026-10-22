# Pre-Planning for a TEI-XML Transcription Editor

## The project
I'm a medievalist with little or no coding experience, working on [Windows / Mac] (delete one). Python (minimum 3.11) is already installed. I want to build a small tool with an AI coding agent (GitHub Copilot in VS Code, Plan then Interactive mode) for my personal research use. The tool will live in a single new subfolder of a pre-existing GitHub repository, managed by GitHub Desktop. The agent must not create, change, or delete anything outside that subfolder.

## The tool
A simple TEI-XML transcription editor that runs in a web browser using Python, entirely offline and without sending my data anywhere. It should show a single manuscript page, starting with one column of 30 lines, allow the user to add and remove lines and columns, and autosave to a single TEI file for the manuscript. Multiple pages and page navigation are out of scope for now.

## Questions
Help me decide the following:
- Which framework and packages do I need? Explain what each one is for and what the alternative would be.
- Are all of these widely used and stable, so that an AI coding assistant will know them well? Is there anything obscure I should avoid?
- Where should my data live, and in what format? How do I ensure that the data will still be accessible years from now even if the app stops working?
- How will I know the output is well-formed? What can I check independently, without trusting the code and without using the terminal?

Before you draft anything, ask me up to ten questions in a single numbered list, and suggest a sensible default for each, so I can reply "use your defaults" for anything I can't answer. Wait for my answers.

Then draft the plan as a single Markdown document with these sections: Goal; Who it's for; Technical decisions (language, packages, folder structure, and what NOT to use); Behaviour (numbered and testable); Output format (with an example); Build phases (small, each with a check I can do myself); Working rules for the agent; Out of scope.

## Requirements
- I should not have to use the terminal or run any manual commands at any point. Assume that I have no coding experience whatsoever.
- The first build phase must get me from nothing to a running (even if trivial) app in the fewest possible steps: a single start script, and everything I need to run the app explained in plain English.
- Each phase ends with the agent stopping, so I can run it, check it, and save a version before continuing.
- Use only the packages we've agreed. Where you would have to make a choice I haven't specified, give me the information that I need to make the choice instead.