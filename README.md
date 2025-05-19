# 🚜 Tiny Tractor Tycoon — *Rabbits Edition*

*A bite‑sized, coin‑driven farming sim that lives entirely in one Python + Pygame file.*

In Tiny Tractor Tycoon you roam an **8 × 6**‑tile field, plant quirky emoji crops, and race mischievous rabbits that pop up the instant your harvest ripens. Earn coins, reinvest in seeds and fertilizer, and see how much produce you can stash before the bunnies devour it!

---

## Table of Contents

1. [Features](#features)
2. [Controls](#controls)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Running the Game](#running-the-game)
6. [Gameplay](#gameplay)
7. [Tips & Tricks](#tips--tricks)
8. [Troubleshooting](#troubleshooting)
9. [Credits](#credits)
10. [License](#license)

---

## Features

| 🌾 Mechanic                | 📋 Details                                                                                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Six Crops**              | Corn, Potato, Tomato, Cucumber, Cabbage, Broccoli — each with its own cost, grow‑time, and payout.                                                            |
| **Emoji‑Only Graphics**    | The entire game world (tractor, crops, rabbits, sparkles) is rendered with font glyphs — no assets needed.                                                    |
| **Rabbit Raids**           | The moment a crop hits stage 3, a rabbit spawns somewhere on the field and begins hopping every **0.6 s**. If it lands on a ripe crop, the produce is *gone*. |
| **Fertilizer Boost**       | Spend **5 💰** on any growing crop to halve its remaining grow‑time. Sparkles indicate the boost.                                                             |
| **Edge Wrapping**          | Drive off one edge of the field to appear on the opposite side — useful for outrunning rabbits.                                                               |
| **Single‑File Simplicity** | Everything — game loop, data, UI — fits in one readable `tiny_tractor_tycoon.py`. Perfect for tinkering.                                                      |

---

## Controls

| Key                                   | Action                                         |
| ------------------------------------- | ---------------------------------------------- |
| **W / A / S / D** *or* **Arrow keys** | Move tractor (wraps at edges)                  |
| **1 – 6**                             | Select seed type                               |
| **SPACE**                             | Plant on empty tile **or** harvest a ripe crop |
| **F**                                 | Fertilize selected tile (costs **5 💰**)       |
| **ESC**                               | Quit game                                      |

---

## Requirements

* **Python 3.8 +** (3.11 recommended)
* **Pygame 2.5 +**

> **Windows emoji font note**
> For full‑color glyphs on Windows, copy `seguiemj.ttf` (Segoe UI Emoji) into the game folder or install Noto Color Emoji. The script auto‑detects available fonts.

---

## Installation

```bash
# 1. Clone or download the repo
git clone https://github.com/your-username/tiny-tractor-tycoon.git
cd tiny-tractor-tycoon

# 2. Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install pygame
```

---

## Running the Game

```bash
python tiny_tractor_tycoon.py
```

A **1024 × 384** window opens: farm on the left, sidebar on the right. Resize is disabled to keep emoji scaling crisp.

---

## Gameplay

1. **Start with 25 💰.** Pick a seed (keys **1 – 6**).
2. **Plant** on any empty soil tile with **SPACE**. The tile flashes yellow briefly.
3. **Wait** (or fertilize) while crops progress through 4 emoji stages (0 – 3).
4. **Harvest** at stage 3 for coins **before rabbits nibble them!**
5. **Reinvest.** Buy more expensive seeds and fertilizer to snowball your earnings.
6. **Track stats** in the sidebar: current coins, total harvests per crop, and a concise control legend.

---

## Tips & Tricks

* **Timing is everything.** Hover near nearly‑ripe crops so you can harvest the tick they mature and outrun any rabbit spawn.
* **Use the wrap.** Driving off‑screen can be quicker than turning.
* **Fertilizer > seed spam.** A well‑timed fertilizer on high‑value crops yields better ROI than planting cheap seeds.
* **Rabbit herding.** Rabbits can’t harm the tractor; bait them to one side of the map before mass harvesting the other.

---

## Troubleshooting

| Symptom                         | Fix                                                                                                                    |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| *Blank emoji squares*           | Install a color‑emoji‑capable font (e.g. Segoe UI Emoji on Windows, Noto Color Emoji on Linux).                        |
| *`ModuleNotFoundError: pygame`* | Make sure you activated your virtual environment and ran `pip install pygame`.                                         |
| *Low FPS*                       | Pygame can struggle on HiDPI monitors. Lower your display scale or comment out alpha‑blending calls for a speed boost. |

---

## Credits

* **Idea & Code:** *DOKKA*
* **Emoji Artwork:** Unicode Consortium
* **Libraries:** Pygame

---

## License

This project is released under the **MIT License** — see [LICENSE](LICENSE) for details. Feel free to fork, tweak constants, or add new critters (foxes? crows?) — just keep it open!

Happy farming 🚜🌱✨

---
