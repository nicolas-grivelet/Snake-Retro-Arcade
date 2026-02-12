"""Canvas utility classes for Tkinter applications.

Provides Picture class for handling images in Canvas widgets.
"""
from tkinter import Canvas
from PIL import Image, ImageTk


class Picture:
    """Wrapper class for Canvas image objects with rotation and transformation support."""
    
    def __init__(self, master: Canvas, angle: int = 0, image: Image.Image = None, 
                 path: str = None, width: int = None, height: int = None):
        """Initialize a Picture object.
        
        Args:
            master: Canvas widget to draw on
            angle: Initial rotation angle (0-360)
            image: PIL Image object
            path: Path to image file (alternative to image parameter)
            width: Desired width (None = original size)
            height: Desired height (None = original size)
        """
        self.angle = angle
        self.master: Canvas = master
        self.id: int = None
        self.photo_image: ImageTk.PhotoImage = None
        self.x1: int = 0
        self.y1: int = 0
        
        # Load image from path or use provided Image object
        if isinstance(path, str) and path:
            self.image: Image.Image = Image.open(path)
        elif isinstance(image, Image.Image):
            self.image: Image.Image = image
        else:
            raise TypeError("Either 'image' (PIL.Image) or 'path' (str) must be provided.")
        
        # Set dimensions
        self.width: int = width if width is not None else self.image.size[0]
        self.height: int = height if height is not None else self.image.size[1]
        
        # Generate initial PhotoImage
        self.photo_image = self.generate_photo()
    
    def show(self, x1: int = 0, y1: int = 0):
        """Display the image on the canvas.
        
        Args:
            x1: X coordinate
            y1: Y coordinate
        """
        self.x1, self.y1 = x1, y1
        self.id = self.master.create_image(self.x1, self.y1, image=self.photo_image)
    
    def update_photo(self, resize: tuple[int, int] = None, angle: int = None):
        """Update the displayed photo with new size or rotation.
        
        Args:
            resize: Tuple of (width, height) for new size
            angle: New absolute angle
        """
        if isinstance(resize, tuple):
            self.width, self.height = resize
        if isinstance(angle, (int, float)):
            self.angle = angle
        
        self.photo_image = self.generate_photo()
        if self.id is not None:
            self.master.itemconfigure(self.id, image=self.photo_image)
    
    def generate_photo(self) -> ImageTk.PhotoImage:
        """Generate PhotoImage from current attributes.
        
        Returns:
            PhotoImage object ready for Tkinter
        """
        # Rotate counter-clockwise (Tkinter convention)
        rotated = self.image.rotate(360 - self.angle)
        resized = rotated.resize((self.width, self.height))
        return ImageTk.PhotoImage(resized.convert("RGBA"))
    
    def resize(self, width: int, height: int):
        """Resize the image (absolute).
        
        Args:
            width: New width
            height: New height
            
        Returns:
            self for method chaining
        """
        self.update_photo(resize=(width, height))
        return self
    
    def set_angle(self, angle: int):
        """Set rotation angle (absolute).
        
        Args:
            angle: New angle (0-360)
            
        Returns:
            self for method chaining
        """
        self.angle = angle % 360
        self.update_photo(angle=self.angle)
        return self
    
    def pivotate(self, _angle: int):
        """Rotate by relative angle.
        
        Args:
            _angle: Angle to add to current rotation
            
        Returns:
            self for method chaining
        """
        self.set_angle(angle=self.angle + _angle)
        return self
    
    def coords(self, x1: int = None, y1: int = None) -> tuple[int, int]:
        """Get or set coordinates (absolute).
        
        Args:
            x1: New X coordinate (None = no change)
            y1: New Y coordinate (None = no change)
            
        Returns:
            Current coordinates as tuple
        """
        if isinstance(x1, (int, float)):
            self.x1 = x1
        if isinstance(y1, (int, float)):
            self.y1 = y1
        
        if x1 is None and y1 is None:
            return self.master.coords(self.id)
        
        return self.master.coords(self.id, self.x1, self.y1)
    
    def move(self, _x1: int = None, _y1: int = None):
        """Move by relative offset.
        
        Args:
            _x1: X offset to add
            _y1: Y offset to add
            
        Returns:
            Current coordinates
        """
        if isinstance(_x1, (int, float)):
            self.x1 += _x1
        if isinstance(_y1, (int, float)):
            self.y1 += _y1
        
        return self.coords(x1=self.x1, y1=self.y1)
    
    def delete(self):
        """Remove the image from the canvas."""
        if self.id is not None:
            self.master.delete(self.id)
            self.id = None
