# CLAUDE.md

Guidance for Claude Code when working in this repository.

## `(AI: ...)` marks in markdown

The author leaves instructions to Claude inline in markdown files (specs,
notes) as `(AI: <instruction>)`, for example `(AI: put image illustrating
the example)` or `(AI: do not touch)`. Whenever you read or edit a `.md`
file here, look for these marks and treat each one as a task placed at that
spot in the document.

- A mark that asks for something (an image, a paragraph, a rewrite) is
  resolved in place, and the mark is removed once done — an image mark
  becomes the `![...]` line, for instance.
- `(AI: do not touch)` means leave that section exactly as it is, even if it
  looks unfinished or duplicated.
- When first asked to look at a file, list the marks found and say how each
  is understood before acting, unless told to just do them.

## Specs and figures

- Specs live in `spec/`, one file per spec, `NNN-short-name.md`, in English,
  starting from `spec/TEMPLATE.md`. Numbers are never reused. A new spec is
  added to the index in `spec/README.md` and to the list in `README.md`.
- Cross-references use `[spec NNN](NNN-short-name.md)`.
- Figures are drawn by a matplotlib script per figure in `docs/figures/`,
  run from the repository root, writing a PNG into `docs/images/`. Each new
  script gets a row in `docs/figures/README.md`. Black and white, no
  explanatory paragraph inside the image.
