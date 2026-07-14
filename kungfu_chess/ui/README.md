# UI package

Graphical UI layer for KFChess. This layer depends on the backend and is
never depended upon by it. It never implements game rules.

## Layer boundaries (final)

- `SpriteLibrary`: assets -> `AnimationData`.
- `SpriteAnimator`: `AnimationData` + time -> `Img` frame.
- `AnimationClock`: real time -> `elapsed_ms`.
- `AnimationProvider`: piece view state + clock -> `Img` frame (the
  `frame_provider`).
- `GraphicalRenderer`: snapshot + `Img` frame -> drawing (holds no state
  between renders; all per-frame data arrives as input).
- `GameApp` (future): orchestration only.

## Currently implemented components

- `piece_code` (`piece_code.py`)
  - Maps `(PieceKind, Color)` to the two-letter asset code (e.g. Queen +
    White -> `QW`). Keeps code strings in one place.
- `AnimationData` (`animation_data.py`)
  - Immutable data for one piece state: `frames`, `fps`, `is_loop`,
    `next_state_when_finished`, `speed_m_per_sec`.
- `SpriteLibrary` (`sprite_library.py`)
  - The only place that reads image and config files.
  - `get_animation(code, state)` loads all frames of a state and its
    `config.json`, and caches the result.
  - `background()` returns a fresh board canvas each call (drawing mutates
    it), loaded from the configured board path.
  - Does not decide the active state and does not advance animation.
- `SpriteAnimator` (`sprite_animator.py`)
  - Given `AnimationData` and an elapsed time, returns the current frame.
  - Manages only animation progression; no game rules, no state
    transitions.
- `AnimationClock` (`animation_clock.py`)
  - Minimal real-time source: `elapsed_ms()` since creation/`reset()`.
  - The time source is injectable, so tests drive it deterministically.
  - No game logic, no rendering.
- `AnimationProvider` (`animation_provider.py`)
  - The connection point used as the renderer's `frame_provider`.
  - Maps a piece's view state to an asset state, loads the animation from
    `SpriteLibrary`, and picks the current frame via `SpriteAnimator` using
    an injected `AnimationClock` (external time source).
  - Keeps time and state selection out of the renderer.
- `GraphicalRenderer` (`graphical_renderer.py`)
  - Subclasses `Renderer`, consumes only immutable `GameSnapshot` objects.
  - For each piece it asks an injected `frame_provider` for a ready frame.
  - Draws a selection border on `snapshot.selected_cell` when set (via
    `Img.draw_rect`); it does not compute selection, only draws it.
  - Applies an optional `board_offset` so the board can be drawn with a
    margin inside a larger canvas.
  - Draw order: background, pieces, selection, overlays. Returns the
    composed canvas.

## Asset structure (from the CTD26 repository)

```text
<pieces_root>/                 # a piece set, e.g. pieces1 or pieces2
  <CODE>/                      # e.g. QW, PB, NW
    states/
      <state>/                 # idle | jump | long_rest | move | short_rest
        config.json
        sprites/
          1.png 2.png ...
board.png                      # background canvas used by Img
```

- `config.json` holds `physics.speed_m_per_sec`,
  `physics.next_state_when_finished`, `graphics.frames_per_sec`,
  `graphics.is_loop`.
- The piece set is selected by the `pieces_root` path (no hard-coded set).
- `board.csv` from the repository is intentionally not used; the backend is
  the source of truth for the board.

## Bundled assets

- Required graphics are copied into the project under `KungFuChess/assets`
  so the project is self-contained and depends on no external path:

```text
KungFuChess/assets/
  board.png
  pieces2/
    <CODE>/states/<state>/{config.json, sprites/*.png}
```

- The demo uses the `pieces2` set. Every piece code has all five states with
  five frames each (complete). Callers inject `pieces_root`/`board_path`;
  `SpriteLibrary` itself keeps no hard-coded asset location.

## Demo (vertical slice)

- `examples/demo_ui.py` is a standalone entry point (no `MouseInput`, no
  `GameApp`). It uses the existing backend only to produce state:
  `BoardParser` builds a standard starting board, `GameFactory` wires the
  engine, and `SnapshotBuilder` turns the engine state into an immutable
  `GameSnapshot`.
- It then renders the full board through `GraphicalRenderer` + `Img`
  (`open_window` / `present` / `close`). Asset-state selection and animation
  live in the demo-owned `AnimationProvider`, which reads time from an
  injected `AnimationClock`, outside the renderer.
- The board is re-rendered every loop iteration, so idle animations play in
  real time according to the fps in each state's `config.json`.
- Run from the `KungFuChess` directory: `python -m examples.demo_ui`.

## View-only rendering

- `GraphicalRenderer` consumes only view data: it iterates
  `GameSnapshot.pieces` (immutable `PieceSnapshot` DTOs), reads a piece's
  `position`, and forwards the `PieceSnapshot` to the `frame_provider`.
- It does not import or depend on backend `Piece`/`GameState`.

## frame_provider (connection point)

- Signature: `Callable[[PieceSnapshot], Img]` — returns the ready frame to
  draw for a piece. `AnimationProvider.frame_for` implements it.
- Everything the provider needs is decided outside the renderer:
  - which asset state a piece is in (state mapping injected into
    `AnimationProvider`),
  - the elapsed time for the animation (from the injected
    `AnimationClock`),
  - which `AnimationData` / `SpriteAnimator` to use.
- The renderer never decides state, elapsed time, or animation.

## State mapping (open)

- No mapping is assumed between the backend `PieceState`
  (`IDLE`/`MOVING`/`CAPTURED`) and the asset states
  (`idle`/`jump`/`move`/`long_rest`/`short_rest`).
- Wiring `PieceState` to asset states will live inside the externally
  owned `frame_provider`; it is a future connection point.

## Current limitations

- Selection is shown as a rectangle border via `Img.draw_rect`.

## Img integration

- `Img` is course-supplied infrastructure at the project root (`img.py`),
  imported as `from img import Img`. It may be extended (per lecturer
  approval) but keeps all `cv2` usage inside itself.
- `Img` now exposes a small window layer for a continuous loop:
  `open_window(title)`, `present(wait_ms)` (non-blocking, returns `None`),
  `set_click_handler(handler)` where `handler(x, y)`, and `close()`. It also
  exposes minimal drawing primitives `draw_rect(...)` (used for the
  selection border) and `create_blank(w, h, color)` (used to build a
  window-sized canvas with a margin). The original
  `read`/`draw_on`/`put_text`/`show` are unchanged.
- The window/event calls are isolated behind a small window backend
  (`Cv2Window`) that is injectable, so tests use a fake and never open a
  real window.
- `cv2` (opencv-python) is required by `Img` and provided by the
  environment/course setup; it is not declared as an application dependency.

## Next implementation step

- Define the state-selection connection point (`frame_provider`), then
  integrate `MouseInput` and `GameApp`.
