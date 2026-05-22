# =============================================================================
# UI THEME MODULE - Divine Drishti 2.0
# Premium Dark Mode Theme for KP ASTROLOGER
# =============================================================================

import tkinter as tk
from tkinter import ttk
import math

# =============================================================================
# COLOR PALETTE
# =============================================================================
class Colors:
    """Premium Dark Mode Color Palette"""
    # Backgrounds
    BG_DARK = "#0a0a0f"
    BG_MEDIUM = "#12121a"
    BG_CARD = "#16213e"
    BG_HOVER = "#1e2a4a"
    BG_INPUT = "#0d1117"
    
    # Primary Accents
    GOLD = "#f5af19"
    GOLD_LIGHT = "#ffd700"
    GOLD_DARK = "#c48f00"
    
    # Secondary Accents
    CYAN = "#00d9ff"
    CYAN_LIGHT = "#5ce1e6"
    CYAN_DARK = "#00a3bf"
    
    # Status Colors
    SUCCESS = "#00f5a0"
    WARNING = "#ffbe0b"
    ERROR = "#ff4757"
    INFO = "#7b68ee"
    PURPLE = "#a855f7"
    
    # Text Colors
    TEXT_PRIMARY = "#e8e8e8"
    TEXT_SECONDARY = "#a0a0a0"
    TEXT_MUTED = "#6b7280"
    TEXT_GOLD = "#ffd700"
    
    # Borders
    BORDER_SUBTLE = "#2a2a3e"
    BORDER_GLOW = "#f5af19"

# =============================================================================
# FONTS
# =============================================================================
class Fonts:
    """Typography System"""
    TITLE = ("Cinzel", 28, "bold")
    SUBTITLE = ("Segoe UI", 16, "bold")
    HEADING = ("Segoe UI", 14, "bold")
    BODY = ("Segoe UI", 11)
    BODY_BOLD = ("Segoe UI", 11, "bold")
    SMALL = ("Segoe UI", 9)
    CONSOLE = ("Cascadia Code", 10)
    CONSOLE_BOLD = ("Cascadia Code", 10, "bold")
    BUTTON = ("Segoe UI", 10, "bold")
    TAB = ("Segoe UI", 11, "bold")

# =============================================================================
# GRADIENT FRAME (Simulated)
# =============================================================================
class GradientFrame(tk.Canvas):
    """A frame with a simulated vertical gradient background."""
    
    def __init__(self, parent, color1=Colors.BG_DARK, color2=Colors.BG_MEDIUM, **kwargs):
        tk.Canvas.__init__(self, parent, highlightthickness=0, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self._draw_gradient)
        
    def _draw_gradient(self, event=None):
        """Draw the gradient on resize."""
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Create gradient with 50 bands
        bands = 50
        for i in range(bands):
            r1, g1, b1 = self._hex_to_rgb(self.color1)
            r2, g2, b2 = self._hex_to_rgb(self.color2)
            
            ratio = i / bands
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            y1 = int(height * i / bands)
            y2 = int(height * (i + 1) / bands) + 1
            
            self.create_rectangle(0, y1, width, y2, fill=color, outline=color, tags="gradient")
        
        # Lower the gradient so widgets appear on top
        self.tag_lower("gradient")
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# =============================================================================
# MODERN BUTTON
# =============================================================================
class ModernButton(tk.Canvas):
    """A modern button with hover effects and rounded corners."""
    
    def __init__(self, parent, text="Button", command=None, 
                 bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                 hover_bg=Colors.BG_HOVER, hover_fg=Colors.GOLD,
                 width=160, height=42, corner_radius=8, **kwargs):
        
        tk.Canvas.__init__(self, parent, width=width, height=height, 
                          bg=parent.cget('bg') if hasattr(parent, 'cget') else Colors.BG_DARK,
                          highlightthickness=0, **kwargs)
        
        self.text = text
        self.command = command
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        self.width = width
        self.height = height
        self.radius = corner_radius
        self.is_hovered = False
        
        self._draw_button()
        
        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        
    def _draw_button(self):
        """Draw the button with rounded corners."""
        self.delete("all")
        
        bg_color = self.hover_bg if self.is_hovered else self.bg
        fg_color = self.hover_fg if self.is_hovered else self.fg
        
        # Draw rounded rectangle
        self._create_rounded_rect(2, 2, self.width-2, self.height-2, self.radius, 
                                  fill=bg_color, outline=Colors.BORDER_SUBTLE if not self.is_hovered else Colors.GOLD)
        
        # Draw text
        self.create_text(self.width/2, self.height/2, text=self.text, 
                        font=Fonts.BUTTON, fill=fg_color, tags="text")
        
    def _create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle."""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
            x1 + radius, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        self.is_hovered = True
        self._draw_button()
        self.config(cursor="hand2")
        
    def _on_leave(self, event):
        self.is_hovered = False
        self._draw_button()
        self.config(cursor="")
        
    def _on_click(self, event):
        if self.command:
            self.command()

# =============================================================================
# GLOW LABEL
# =============================================================================
class GlowLabel(tk.Canvas):
    """A label with a subtle glow effect."""
    
    def __init__(self, parent, text="", font=Fonts.TITLE, 
                 fg=Colors.GOLD, glow_color=Colors.GOLD_DARK, **kwargs):
        
        # Calculate size based on font
        tk.Canvas.__init__(self, parent, highlightthickness=0, 
                          bg=parent.cget('bg') if hasattr(parent, 'cget') else Colors.BG_DARK, **kwargs)
        
        self.text = text
        self.font = font
        self.fg = fg
        self.glow_color = glow_color
        
        self._draw_text()
        
    def _draw_text(self):
        """Draw text with glow effect."""
        self.delete("all")
        
        # Get canvas size
        width = self.winfo_reqwidth() or 800
        height = self.winfo_reqheight() or 60
        
        # Draw glow layers (offset text in multiple directions)
        offsets = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in offsets:
            self.create_text(width/2 + dx, height/2 + dy, text=self.text, 
                            font=self.font, fill=self.glow_color, tags="glow")
        
        # Draw main text
        self.create_text(width/2, height/2, text=self.text, 
                        font=self.font, fill=self.fg, tags="main")

# =============================================================================
# CARD FRAME
# =============================================================================
class CardFrame(tk.Frame):
    """A card-style frame with subtle border and background."""
    
    def __init__(self, parent, title=None, **kwargs):
        tk.Frame.__init__(self, parent, bg=Colors.BG_CARD, 
                         highlightbackground=Colors.BORDER_SUBTLE,
                         highlightthickness=1, **kwargs)
        
        if title:
            title_label = tk.Label(self, text=title, font=Fonts.HEADING,
                                  fg=Colors.GOLD, bg=Colors.BG_CARD)
            title_label.pack(anchor="w", padx=15, pady=(10, 5))

# =============================================================================
# STATUS INDICATOR
# =============================================================================
class StatusIndicator(tk.Canvas):
    """A small circular status indicator."""
    
    def __init__(self, parent, size=12, color=Colors.SUCCESS, **kwargs):
        tk.Canvas.__init__(self, parent, width=size+4, height=size+4,
                          highlightthickness=0, 
                          bg=parent.cget('bg') if hasattr(parent, 'cget') else Colors.BG_DARK, **kwargs)
        
        self.size = size
        self.color = color
        self._draw()
        
    def _draw(self):
        self.delete("all")
        # Outer glow
        self.create_oval(1, 1, self.size+3, self.size+3, 
                        fill=self.color, outline="", tags="glow")
        # Inner dot
        self.create_oval(3, 3, self.size+1, self.size+1, 
                        fill=self.color, outline=Colors.BG_DARK, width=1)
        
    def set_status(self, color_or_bool):
        """Update the indicator color. Supports boolean for quick success/error mapping."""
        if isinstance(color_or_bool, bool):
            self.color = Colors.SUCCESS if color_or_bool else Colors.ERROR
        else:
            self.color = color_or_bool
        self._draw()

# =============================================================================
# STYLED SCROLLBAR
# =============================================================================
class StyledScrollbar(tk.Canvas):
    """A modern styled scrollbar replacement (placeholder - uses standard)."""
    pass  # Tkinter scrollbar styling is limited; keeping standard for now

# =============================================================================
# CONSOLE OUTPUT
# =============================================================================
class EnhancedConsole(tk.Text):
    """Enhanced console with better styling and tags."""
    
    def __init__(self, parent, **kwargs):
        # Default console styling
        defaults = {
            'bg': Colors.BG_INPUT,
            'fg': Colors.TEXT_PRIMARY,
            'font': Fonts.CONSOLE,
            'insertbackground': Colors.CYAN,
            'selectbackground': Colors.BG_HOVER,
            'selectforeground': Colors.TEXT_PRIMARY,
            'relief': 'flat',
            'padx': 10,
            'pady': 10,
            'wrap': 'word'
        }
        defaults.update(kwargs)
        
        tk.Text.__init__(self, parent, **defaults)
        
        # Configure enhanced tags
        self._setup_tags()
        
    def _setup_tags(self):
        """Configure text tags for syntax highlighting."""
        # Status tags
        self.tag_config("gold", foreground=Colors.GOLD)
        self.tag_config("success", foreground=Colors.SUCCESS)
        self.tag_config("error", foreground=Colors.ERROR)
        self.tag_config("warning", foreground=Colors.WARNING)
        self.tag_config("info", foreground=Colors.INFO)
        self.tag_config("cyan", foreground=Colors.CYAN)
        self.tag_config("purple", foreground=Colors.PURPLE)
        self.tag_config("red", foreground=Colors.ERROR)
        self.tag_config("green", foreground=Colors.SUCCESS)
        
        # Style tags
        self.tag_config("title", foreground=Colors.GOLD, font=Fonts.HEADING)
        self.tag_config("header", foreground=Colors.GOLD_LIGHT, font=Fonts.BODY_BOLD)
        self.tag_config("highlight", foreground=Colors.CYAN, font=Fonts.BODY_BOLD)
        self.tag_config("muted", foreground=Colors.TEXT_MUTED)
        self.tag_config("timestamp", foreground=Colors.TEXT_MUTED, font=Fonts.SMALL)
        
    def log(self, message, tag=None):
        """Add a message to the console."""
        self.insert(tk.END, f"{message}\n", tag)
        self.see(tk.END)
        
    def clear(self):
        """Clear the console."""
        self.delete(1.0, tk.END)

# =============================================================================
# TAB STYLING
# =============================================================================
def apply_tab_style(style: ttk.Style):
    """Apply modern styling to ttk.Notebook tabs."""
    style.theme_use('clam')
    
    # Notebook styling
    style.configure("TNotebook", 
                   background=Colors.BG_DARK, 
                   borderwidth=0,
                   tabmargins=[0, 0, 0, 0])
    
    style.configure("TNotebook.Tab",
                   background=Colors.BG_MEDIUM,
                   foreground=Colors.TEXT_SECONDARY,
                   font=Fonts.TAB,
                   padding=[25, 12],
                   borderwidth=0)
    
    style.map("TNotebook.Tab",
             background=[("selected", Colors.BG_CARD), ("active", Colors.BG_HOVER)],
             foreground=[("selected", Colors.GOLD), ("active", Colors.GOLD_LIGHT)],
             expand=[("selected", [0, 0, 0, 2])])
    
    # Frame styling
    style.configure("Card.TFrame", background=Colors.BG_CARD)
    style.configure("Dark.TFrame", background=Colors.BG_DARK)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
def create_separator(parent, color=Colors.BORDER_SUBTLE, height=1):
    """Create a horizontal separator line."""
    sep = tk.Frame(parent, height=height, bg=color)
    return sep

def create_spacer(parent, height=20):
    """Create vertical spacing."""
    spacer = tk.Frame(parent, height=height, bg=parent.cget('bg'))
    return spacer
