# 🐍 Snake – Retro Arcade Edition

A modern, object-oriented implementation of the classic arcade game **Snake**.  
Built with **Python**, **tkinter**, and **Pillow**, this project features smooth animations, progressive difficulty, and a custom rendering engine.

---

## 🌟 Key Features

- **Object-Oriented Architecture**  
  Modular design separating game logic, rendering (`Board`), and entities (`Snake`, `Apple`).

- **Smooth Movement**  
  Uses the `tkinter.after()` event loop for fluid motion and precise refresh handling.

- **Dynamic Difficulty**  
  The snake’s speed increases mathematically based on your score.

- **Asset Management**  
  Dynamic loading system via the `assets/` folder, handled with robust relative paths (`os.path`).

- **Developer Tools**  
  Built-in cheat mode (*Cheat Mode*) to test collisions and pass through obstacles.

---

## 🎮 Controls

| Key                    | Action                                              |
|------------------------|-----------------------------------------------------|
| Arrow keys             | Control the snake (Up, Down, Left, Right)           |
| Ctrl + R               | Enable / Disable Cheat Mode (No Clip)               |

---

## 🛠️ Installation

Clone the repository:

```bash
git clone https://github.com/nicolas-grivelet/Snake-Retro-Arcade.git
````

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the game:

```bash
python src/main.py
```

---

## 📂 Project Structure

```
Snake-Retro-Arcade/
├── assets/              # Images and sprites (png/gif)
├── src/                 # Source code
│   ├── canvas_utils.py # Rendering engine (Picture sprite handling)
│   └── main.py         # Game loop and main logic
└── requirements.txt    # Python dependencies (Pillow)
```

---

## 🧠 Technical Details

The architecture relies on a clear separation between:

* `canvas_utils.py`, which provides a generic `Picture` class to manipulate images on a Tkinter Canvas (rotation, resizing),
* `main.py`, which handles the game rules.

The system uses dynamic file paths to ensure the game works correctly regardless of the execution directory.

---

## 📝 License

Distributed under the MIT license.
See the `LICENSE` file for more information.
