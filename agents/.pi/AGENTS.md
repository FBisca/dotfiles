# Pi instructions

## Codemode

Codemode runs JavaScript that calls the other tools; only the script's output reaches the model. Use it when it saves context; a direct tool call is cheaper for a single operation.

- Batch independent calls with `Promise.allSettled()`; sequence dependent ones.
- Filter large outputs inside the script; return only relevant findings, paths, and diagnostics.
- Preserve exit codes, failures, and error details in what you return; report verification results exactly as they ran. Verification rests on raw test artifacts and exit codes; a summary alone never proves a test passed.
- Cap noisy scripts with a first-line `// @options: {"max_output_tokens": N}`; keep evidence needed for correctness whole.
- Keep scripts plain: when one command suffices, run it directly.
