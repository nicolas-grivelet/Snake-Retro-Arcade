"""Snake Game - Classic snake game implementation with Tkinter.

Uses Tkinter's after() method instead of threading for proper GUI updates.
"""
from canvas_utils import Picture
from PIL import Image, ImageTk
from tkinter import Tk, Canvas, PhotoImage, Button, CENTER
import random


class SnakeBody(Picture):
    """Snake body segment with rotation support."""
    
    def __init__(self, snake, _type: str = "body_image", *args, **kwargs):
        """Initialize a snake body segment.
        
        Args:
            snake: Parent Snake object
            _type: Type of segment ('head_image' or 'body_image')
        """
        super().__init__(*args, **kwargs)
        self.snake: 'Snake' = snake
        self.type = _type
    
    def set_angle(self, angle: int):
        """Set absolute rotation angle using pre-cached images.
        
        Args:
            angle: Target angle (0-360)
            
        Returns:
            self for method chaining
        """
        self.angle = int(angle % 360)
        # Use pre-cached rotated images for performance
        self.photo_image = self.snake.rotated_photo_images[self.type][self.angle]
        if self.id is not None:
            self.master.itemconfigure(self.id, image=self.photo_image)
        return self


class Apple(Picture):
    """Apple object that spawns at random locations."""
    
    def __init__(self, game, image: Image.Image = None, *args, **kwargs):
        """Initialize an apple.
        
        Args:
            game: Parent Game object
            image: Optional PIL Image (defaults to apple.gif)
        """
        self.game: 'Game' = game
        self.master: Board = self.game.board
        self.cell_position: list = [0, 0]  # Store current cell position [col, row]
        
        if image is None:
            image = Image.open("../assets/apple.gif").resize(
                (self.master.width // self.master.ncols, 
                 self.master.height // self.master.nrows)
            )
        
        super().__init__(master=self.master, image=image, *args, **kwargs)
    
    def _show(self):
        """Show apple at random location."""
        self.cell_position = self.random_cell()
        coords = self.master.get_coords(col=self.cell_position[0], row=self.cell_position[1])
        Picture.show(self, *coords)
    
    show = _show
    
    def regenerate(self):
        """Move apple to a new random location."""
        self.cell_position = self.random_cell()
        coords = self.master.get_coords(col=self.cell_position[0], row=self.cell_position[1])
        self.coords(*coords)
    
    def random_cell(self):
        """Get random free cell position.
        
        Returns:
            List of [col, row]
        """
        if self.master.free_cells:
            return random.choice(self.master.free_cells).copy()
        return [1, 1]


class Board(Canvas):
    """Game board with grid pattern."""
    
    def __init__(self, game, nrows: int = 20, ncols: int = 20, 
                 master: Tk = None, bg: str = "white", 
                 height: int = 750, width: int = 750, *args, **kwargs):
        """Initialize the game board.
        
        Args:
            game: Parent Game object
            nrows: Number of rows
            ncols: Number of columns
            master: Tkinter root window
            bg: Background color
            height: Board height in pixels
            width: Board width in pixels
        """
        super().__init__(master=master, bg=bg, height=height, width=width, *args, **kwargs)
        self.nrows, self.ncols = nrows, ncols
        self.width, self.height = width, height
        self.game: 'Game' = game
        self.free_cells: list = []
        
        # Create checkerboard pattern
        self.cells_id = [
            [
                self.create_rectangle(
                    (width / ncols * (col - 1),
                     height / nrows * (row - 1),
                     width / ncols * col,
                     height / nrows * row),
                    fill="#8BF52D" if (row + col) % 2 == 0 else "#6EBD28",
                    outline=""
                ) 
                for col in range(1, ncols + 1)
            ] 
            for row in range(1, nrows + 1)
        ]
    
    def update_free_cells(self):
        """Update list of cells not occupied by snake.
        
        Returns:
            List of free [col, row] positions
        """
        self.free_cells = [
            [i, j] 
            for i in range(1, self.ncols + 1) 
            for j in range(1, self.nrows + 1) 
            if not hasattr(self.game, "snake") 
               or not hasattr(self.game.snake, "cells") 
               or [i, j] not in self.game.snake.cells
        ]
        return self.free_cells
    
    def get_coords(self, col, row):
        """Convert cell position to pixel coordinates.
        
        Args:
            col: Column number (1-indexed)
            row: Row number (1-indexed)
            
        Returns:
            Tuple of (x, y) pixel coordinates (center of cell)
        """
        col_idx, row_idx = col - 1, row - 1
        x = int(self.width / (self.ncols * 2) + col_idx * self.width / self.ncols)
        y = int(self.height / (self.nrows * 2) + row_idx * self.height / self.nrows)
        return x, y
    
    def get_cell(self, coords):
        """Convert pixel coordinates to cell position.
        
        Args:
            coords: Tuple of (x, y) pixel coordinates
            
        Returns:
            Tuple of (col, row) cell position
        """
        x, y = coords
        col = int((x - self.width / (self.ncols * 2)) / (self.width / self.ncols)) + 1
        row = int((y - self.height / (self.nrows * 2)) / (self.height / self.nrows)) + 1
        return col, row
    
    def cell(self, _id, *args):
        """Get cell position from canvas object ID.
        
        Args:
            _id: Canvas object ID
            
        Returns:
            Tuple of (col, row)
        """
        return self.get_cell(self.coords(_id, *args))


class Game:
    """Main game controller."""
    
    def __init__(self, master, cheat_mode: bool = True):
        """Initialize the game.
        
        Args:
            master: Tkinter root window
            cheat_mode: Enable cheat mode (no collision, reverse allowed)
        """
        self.master: Tk = master
        self.board: Board = Board(self, master=master)
        self.score: int = 0
        self.difficulty: int = -1  # -1: Easy, 0: Average, 1: Difficult
        self.cheat_mode: bool = cheat_mode
        self.game_running: bool = False
        self.after_id = None  # Store after() callback ID
        
        # Initialize game objects
        self.snake: Snake = Snake(
            master=self.board, 
            head_image="../assets/snake_head.gif", 
            body_image="../assets/snake_body.gif",
            game=self
        )
        self.apple: Apple = Apple(self)
        
        # UI elements
        self.restart_button: Button = Button(
            master=self.board, 
            text="Restart", 
            font=("Arial", 25), 
            command=self.reset
        )
        
        # Setup
        self.board.pack()
        self.board.update()
        self.restart_button.update()
        self.snake.show()
        self.apple.show()
        
        # Bind cheat mode toggle
        self.master.bind("<Control-r>", self._toggle_cheat_mode)
        
        # Print controls to console only
        print("=" * 50)
        print("🎮 SNAKE GAME - CONTRÔLES")
        print("=" * 50)
        print("Flèches : Diriger le serpent")
        print("Ctrl+R  : Mode triche ON/OFF")
        print(f"Mode triche : {'✅ ACTIVÉ' if self.cheat_mode else '❌ DÉSACTIVÉ'}")
        print("=" * 50)
    
    def _toggle_cheat_mode(self, event=None):
        """Toggle cheat mode on/off."""
        self.cheat_mode = not self.cheat_mode
        if self.cheat_mode:
            self.snake.activate_cheat()
        else:
            self.snake.deactivate_cheat()
        
        # Visual feedback
        status = "✅ ACTIVÉ" if self.cheat_mode else "❌ DÉSACTIVÉ"
        message = f"MODE TRICHE : {status}"
        
        # Show temporary message
        temp_msg = self.board.create_text(
            self.board.width // 2, 
            50,
            text=message,
            anchor=CENTER,
            fill="#FF0000" if self.cheat_mode else "#00FF00",
            font=("Arial", 16, "bold")
        )
        
        # Remove message after 2 seconds
        self.master.after(2000, lambda: self.board.delete(temp_msg))
        
        print(f"🎮 Mode triche: {status}")
    
    def launch(self):
        """Start the game loop using Tkinter's after() method."""
        if not self.game_running:
            self.game_running = True
            self._game_loop()
    
    def _game_loop(self):
        """Main game loop - called repeatedly via after()."""
        if not self.game_running:
            return
        
        # Advance snake by one step
        still_alive = self.snake.advance()
        
        if still_alive:
            # Calculate delay between moves (gets faster as score increases)
            # Starts at ~200ms, decreases to minimum of ~50ms
            base_delay = 200
            min_delay = 50
            speed_delay = max(min_delay, base_delay - (self.score * 5))
            
            # Schedule next iteration
            self.after_id = self.master.after(speed_delay, self._game_loop)
        else:
            # Game over
            self.game_running = False
            self._show_game_over()
    
    def _show_game_over(self):
        """Display game over message and restart button."""
        message = f"GAME OVER\nScore: {self.score}"
        self.end_message = self.board.create_text(
            self.board.width // 2, 
            self.board.height // 2, 
            text=message,
            anchor=CENTER,
            activefill="#666666", 
            fill="#000000", 
            font=("Arial", 35),
            justify=CENTER
        )
        
        self.restart_button.place(
            x=(self.board.winfo_width() - self.restart_button.winfo_reqwidth()) // 2,
            y=(self.board.winfo_height() - self.restart_button.winfo_reqheight()) * 1.4 // 2
        )
    
    def add_score(self, points=1):
        """Add points to score and regenerate apple.
        
        Args:
            points: Points to add
        """
        self.score += points
        self.apple.regenerate()
    
    def reset(self):
        """Reset game to initial state."""
        # Cancel any pending after() callbacks
        if self.after_id is not None:
            self.master.after_cancel(self.after_id)
            self.after_id = None
        
        # Reset state
        self.score = 0
        self.game_running = False
        
        # Remove game over UI
        if hasattr(self, 'end_message'):
            self.board.delete(self.end_message)
        self.restart_button.place_forget()
        
        # Reset game objects
        self.snake.reset()
        self.apple.regenerate()
        
        # Restart game
        self.launch()


class Snake:
    """Snake object with movement and collision detection."""
    
    def __init__(self, head_image, body_image, game: Game, 
                 cell1: tuple[int, int] = None, cell2: tuple[int, int] = None, 
                 *args, **kwargs):
        """Initialize the snake.
        
        Args:
            head_image: Path or Image object for head
            body_image: Path or Image object for body segments
            game: Parent Game object
            cell1: Starting head position
            cell2: Starting tail position
        """
        self.length: int = 0
        self.cells: list[list] = []
        self.directions: list[int] = []
        self.alive: bool = True
        self.game: Game = game
        self.master: Board = self.game.board
        
        # Initialize position
        self.init(cell1, cell2)
        
        # Load and resize images
        def load_image(img):
            if isinstance(img, Image.Image):
                return img
            return Image.open(img)
        
        cell_width = int(self.master.width / self.master.ncols)
        cell_height = int(self.master.height / self.master.nrows)
        
        self.head_image = load_image(head_image).convert("RGBA").resize((cell_width, cell_height))
        self.body_image = load_image(body_image).convert("RGBA").resize((cell_width, cell_height))
        
        # Create body segments
        self.body = [
            SnakeBody(master=self.master, image=self.head_image, snake=self, _type="head_image"),
            *[SnakeBody(master=self.master, image=self.body_image, snake=self) 
              for _ in range(self.length - 1)]
        ]
        
        # Pre-cache rotated images for performance
        self.rotated_photo_images: dict = {
            "head_image": [ImageTk.PhotoImage(self.head_image.rotate(360 - angle)) 
                          for angle in range(360)],
            "body_image": [ImageTk.PhotoImage(self.body_image.rotate(360 - angle)) 
                          for angle in range(360)]
        }
        
        self.next_direction: int = self.directions[0]
        
        # Bind arrow keys
        self.master.master.bind("<Up>", lambda e: self.set_next_direction(360))
        self.master.master.bind("<Left>", lambda e: self.set_next_direction(270))
        self.master.master.bind("<Down>", lambda e: self.set_next_direction(180))
        self.master.master.bind("<Right>", lambda e: self.set_next_direction(90))
        
        # Apply cheat mode if enabled
        if self.game.cheat_mode:
            self.activate_cheat()
        
        # Store original methods for cheat toggle
        self._original_update_free_cells = self.master.update_free_cells
        self._original_set_next_direction = self._set_next_direction_impl
    
    def _set_next_direction_impl(self, angle) -> bool:
        """Internal implementation of direction setting with validation.
        
        Args:
            angle: Target direction (90, 180, 270, 360)
            
        Returns:
            True if direction was set
        """
        # Prevent 180-degree turns
        if abs(self.next_direction - angle) != 180 and angle != self.next_direction:
            self.next_direction = angle
        return True
    
    def activate_cheat(self):
        """Enable cheat mode (no collision, allow reverse)."""
        # Override free_cells to include all cells
        def cheat_update_free_cells():
            self.master.free_cells = [
                [i, j] 
                for i in range(1, self.master.ncols + 1) 
                for j in range(1, self.master.nrows + 1)
            ]
            return self.master.free_cells
        
        # Override direction setting to allow all directions
        def cheat_set_next_direction(angle):
            self.next_direction = angle
            return True
        
        self.master.update_free_cells = cheat_update_free_cells
        self.set_next_direction = cheat_set_next_direction
    
    def deactivate_cheat(self):
        """Disable cheat mode (restore normal rules)."""
        self.master.update_free_cells = self._original_update_free_cells
        self.set_next_direction = self._original_set_next_direction
    
    def set_next_direction(self, angle) -> bool:
        """Set next direction (normal mode with validation).
        
        This method can be overridden by cheat mode.
        
        Args:
            angle: Target direction
            
        Returns:
            True if direction was set
        """
        return self._set_next_direction_impl(angle)
    
    def init(self, cell1: tuple[int, int] = None, cell2: tuple[int, int] = None):
        """Initialize snake position and direction.
        
        Args:
            cell1: Head position (defaults to center-left)
            cell2: Tail position (defaults to 3 cells left of head)
        """
        # Default positions
        if cell1 is None:
            cell1 = (self.master.ncols // 2, self.master.nrows // 2)
        if cell2 is None:
            cell2 = (self.master.ncols // 2 - 3, self.master.nrows // 2)
        
        # Calculate length and cells
        dx = cell1[0] - cell2[0]
        dy = cell1[1] - cell2[1]
        self.length = max(abs(dx), abs(dy))
        
        # Generate cell positions
        self.cells = [
            [
                cell1[0] - i if dx != 0 else cell1[0],
                cell1[1] - i if dy != 0 else cell1[1]
            ]
            for i in range(self.length)
        ]
        
        # Update free cells early to prevent apple spawn on snake
        self.master.free_cells = [
            [i, j] 
            for i in range(1, self.master.ncols + 1) 
            for j in range(1, self.master.nrows + 1) 
            if [i, j] not in self.cells
        ]
        self.master.update_free_cells()
        
        # Determine initial direction
        def get_direction():
            col_diff = self.cells[0][0] - self.cells[1][0]
            row_diff = self.cells[0][1] - self.cells[1][1]
            
            if col_diff < 0:
                return 270  # Left
            elif col_diff > 0:
                return 90   # Right
            elif row_diff < 0:
                return 360  # Up
            elif row_diff > 0:
                return 180  # Down
            return 90  # Default right
        
        initial_direction = get_direction()
        self.directions = [initial_direction] * self.length
    
    def advance(self):
        """Advance snake one step in current direction.
        
        Returns:
            True if snake is still alive, False if game over
        """
        speed = 5  # Number of animation frames
        
        # Movement vectors for each direction
        direction_vectors = {
            90: (1, 0),    # Right
            180: (0, 1),   # Down
            270: (-1, 0),  # Left
            360: (0, -1)   # Up
        }
        
        # Update direction and position
        self.directions.insert(0, self.next_direction)
        new_col = self.cells[0][0] + direction_vectors[self.next_direction][0]
        new_row = self.cells[0][1] + direction_vectors[self.next_direction][1]
        self.cells.insert(0, [new_col, new_row])
        
        # Check collision
        if self.cells[0] not in self.master.free_cells:
            self.alive = False
        
        # Check if apple eaten - use stored cell position for accurate detection
        new_body = None
        if list(self.cells[0]) == list(self.game.apple.cell_position):
            self.game.add_score()
            new_body = self.create_body()
            # Get coordinates of the last cell (tail position)
            tail_col, tail_row = self.cells[-1]
            x1, y1 = self.master.get_coords(col=tail_col, row=tail_row)
            new_body.show(x1=x1, y1=y1)
        
        # Animate movement
        for i in range(1, speed + 1):
            for j, snake_body in enumerate(self.body):
                if not self.alive:
                    if i == speed or snake_body.angle == self.directions[j]:
                        return self.alive
                    else:
                        # Death animation for head
                        if j == 0:
                            angle_diff = self.directions[j] - snake_body.angle
                            snake_body.pivotate(int(angle_diff / speed))
                        continue
                
                # Rotate body segment if needed
                if snake_body.angle != self.directions[j]:
                    angle_diff = self.directions[j] - snake_body.angle
                    # Handle wrap-around
                    if angle_diff > 180:
                        angle_diff -= 360
                    elif angle_diff < -180:
                        angle_diff += 360
                    snake_body.pivotate(int(angle_diff / speed))
                
                # Move to new position
                curr_x, curr_y = self.master.get_coords(col=self.cells[j][0], row=self.cells[j][1])
                prev_x, prev_y = self.master.get_coords(col=self.cells[j + 1][0], row=self.cells[j + 1][1])
                
                # Interpolate position
                x1 = int(prev_x + i / speed * (curr_x - prev_x))
                y1 = int(prev_y + i / speed * (curr_y - prev_y))
                snake_body.coords(x1, y1)
        
        # Update state
        self.master.update_free_cells()
        
        if new_body is not None:
            # Grew by eating apple
            self.body.append(new_body)
            self.length += 1
        else:
            # Remove tail
            self.directions = self.directions[:-1]
            self.cells = self.cells[:-1]
        
        return self.alive
    
    def create_body(self):
        """Create a new body segment.
        
        Returns:
            New SnakeBody object
        """
        new_snake_body = SnakeBody(master=self.master, image=self.body_image, snake=self)
        new_snake_body.set_angle(self.directions[-1])
        return new_snake_body
    
    def show(self):
        """Display all snake segments on the board."""
        for snake_body, cell, angle in zip(self.body, self.cells, self.directions):
            x1, y1 = self.master.get_coords(col=cell[0], row=cell[1])
            snake_body.photo_image = ImageTk.PhotoImage(
                snake_body.image.rotate(360 - angle).convert("RGBA")
            )
            snake_body.show(x1=x1, y1=y1)
    
    def delete(self):
        """Remove all snake segments from the board."""
        for snake_body in self.body:
            snake_body.delete()
    
    def reset(self):
        """Reset snake to initial state."""
        self.delete()
        self.init()
        
        # Recreate body segments
        self.body = [
            SnakeBody(master=self.master, image=self.head_image, snake=self, _type="head_image"),
            *[SnakeBody(master=self.master, image=self.body_image, snake=self) 
              for _ in range(self.length - 1)]
        ]
        
        self.show()
        self.next_direction = self.directions[0]
        self.alive = True


def main():
    """Run the snake game."""
    window = Tk()
    window.title("Snake - Game")
    
    try:
        icon_photo_img = PhotoImage(file="../assets/snake_icon.png")
        window.iconphoto(False, icon_photo_img)
    except Exception:
        pass  # Icon file not found, continue without it
    
    game = Game(window, cheat_mode=False)
    game.launch()
    window.mainloop()


if __name__ == "__main__":
    main()
