Removed the `continue-on-error` flags so lint failures now fail the workflow, matching the requested behavior in the lint workflow.

Details: updated the two lint steps in `.github/workflows/lint.yml` to allow `flake8` and `black` to block the job when they fail.

If you want, I can also verify the workflow triggers by simulating a change in a `.py` file.