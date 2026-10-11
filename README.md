# Memory Color Pattern Repair Lab

## Student Details

- **Name:** Shrikar Desai
- **SRN:** PES1UG24CS916
- **Project:** Memory Color Pattern Repair Lab
- **Technology:** Python 3.10+ and Pygame
- **AI pair-programming tool:** GitHub Copilot in VS Code

## Project Overview

Memory Color Pattern is a Simon-style pattern-recall game built with Pygame. The player watches a sequence of colored pads, then repeats the sequence in the same order. Each successful round adds one new color to the sequence.

The project uses a simple finite-state flow:

- `WATCH`: The game plays the sequence for the player.
- `PLAYER_TURN`: The player repeats the sequence before the countdown expires.
- `GAME_OVER`: Incorrect input or timer expiry ends the round. Press `R` to restart.

## Features Implemented

### Task 1 — Sequence duplication fix

Each successful round appends exactly one new color to the existing sequence. Previously generated colors retain their order.

### Task 2 — Dynamic playback acceleration

The game reduces the pad flash and between-flash pause durations as the round number increases. Minimum limits keep playback from becoming excessively fast.

For round number \(n\):

- Flash duration: `max(180, 450 - 25 × (n - 1))` milliseconds.
- Pause duration: `max(80, 200 - 12 × (n - 1))` milliseconds.

### Task 3 — Sound effects

Each colored pad has a distinct generated sine-wave tone. Sounds play when pads illuminate during sequence playback and when the player clicks a pad. Tones are cached, and the game continues without sound if audio initialization fails.

| Pad | Frequency |
|---|---:|
| Red | 261.63 Hz |
| Blue | 329.63 Hz |
| Green | 392.00 Hz |
| Yellow | 523.25 Hz |

### Task 4 — Player-turn countdown timer

A horizontal countdown bar is shown only during `PLAYER_TURN`. The timer starts after the sequence playback finishes and uses elapsed time rather than frame counts. When time expires, the game transitions to `GAME_OVER`; late clicks are rejected.

The time budget is calculated from the sequence length and clamped to a minimum of 3,500 ms and a maximum of 15,000 ms:

`duration = clamp(3500 + sequence_length × 900, 3500, 15000)` milliseconds.

## Setup and Run

Make sure Python 3.10 or newer is installed. From the repository root, install Pygame:

```bash
python -m pip install pygame
```

Run the game:

```bash
python main.py
```

### Controls

- Left-click a colored pad to enter the sequence.
- Press `R` on the Game Over screen to restart.

## Repository Structure

```text
58_color_pattern/
├── game/
│   ├── color_button.py
│   ├── game_engine.py
│   └── __pycache__/            # Generated Python bytecode (not needed to run)
├── submission/
│   ├── Before.mp4              # Gameplay before changes
│   ├── After.mp4               # Gameplay after changes
│   ├── chat.json               # Exported Copilot chat history
│   └── copilot_1.png ... copilot_6.png  # Copilot evidence screenshots
├── main.py
└── README.md
```

Syntax checks and focused runtime assertions were reported as passing during development. Interactive testing should also be performed on the target machine, especially to verify audio output and timer expiry.

## Submission

The `submission/` directory contains the before and after gameplay videos, the exported Copilot chat history, and supporting Copilot screenshots.

- **Before video:** [submission/Before.mp4](submission/Before.mp4)
- **After video:** [submission/After.mp4](submission/After.mp4)
- **Exported Copilot chat history:** [submission/chat.json](submission/chat.json)
