# Fix-Later Backlog

Items we are deferring so we can keep shipping improvements quickly. Tackle these once the current dev sprint finishes.

1. **Dialog UI reliability** – Main menu still falls back to the text interface on some terminals. Need to trace why `dialog` exits immediately (maybe terminfo/theme), add an environment probe, and restore the purple windowed UX by default.
2. **Model metadata fetch** – After `ollama pull` succeeds, `ollama show --json <tag>` sometimes returns a non-zero exit code. Investigate (daemon timing? version mismatch?) and ensure we surface accurate size/quantization data without warning spam.
3. **Progress piping for other ops** – Now that model downloads stream nicely, extend the same progress output to project packaging, training, and setup routines so every long-running task has visible feedback.
