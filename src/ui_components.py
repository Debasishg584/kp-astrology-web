import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk # type: ignore
import os
import datetime
try:
    from tkcalendar import DateEntry # type: ignore
except ImportError:
    DateEntry = None

def create_compact_input(parent, label_text, entry_var_name, theme, fonts, entries, width=15, default=None):
    """Factory for compact input fields with labels."""
    frame = tk.Frame(parent, bg=theme["card_bg"])
    frame.pack(side=tk.LEFT, padx=5)
    
    lbl = tk.Label(frame, text=label_text, bg=theme["card_bg"], fg=theme["text_dim"], 
                  font=("Segoe UI", 9))
    lbl.pack(anchor="w")
    
    ent = ttk.Entry(frame, width=width, font=fonts["input"])
    if default:
        ent.insert(0, str(default))
    ent.pack()
    entries[entry_var_name] = ent
    return ent

class TimeEntryWrapper:
    """Wrapper to make 3 comboboxes act like a standard Entry widget for .get() and .insert()"""
    def __init__(self, h, m, s):
        self.h = h
        self.m = m
        self.s = s
    def get(self):
        return f"{self.h.get()}:{self.m.get()}:{self.s.get()}"
    def insert(self, index, string):
        try:
            parts = string.split(':')
            if len(parts) >= 1: self.h.set(parts[0].zfill(2))
            if len(parts) >= 2: self.m.set(parts[1].zfill(2))
            if len(parts) >= 3: self.s.set(parts[2].zfill(2))
        except:
            pass
    def delete(self, first, last=None):
        pass

def create_date_input(parent, label_text, entry_var_name, theme, fonts, entries, width=12, default=None):
    """Factory for compact Date field using tkcalendar DateEntry."""
    frame = tk.Frame(parent, bg=theme["card_bg"])
    frame.pack(side=tk.LEFT, padx=5)
    
    lbl = tk.Label(frame, text=label_text, bg=theme["card_bg"], fg=theme["text_dim"], 
                  font=("Segoe UI", 9))
    lbl.pack(anchor="w")
    
    if DateEntry is not None:
        ent = DateEntry(frame, width=width, background=theme["primary"], 
                        foreground="white", borderwidth=0, 
                        font=fonts["input"], date_pattern='dd-mm-yyyy')
        if default:
            try:
                dt = datetime.datetime.strptime(str(default), "%d-%m-%Y").date()
                ent.set_date(dt)
            except:
                pass
    else:
        # Fallback if tkcalendar isn't installed for some reason
        ent = ttk.Entry(frame, width=width, font=fonts["input"])
        if default:
            ent.insert(0, str(default))
            
    ent.pack()
    entries[entry_var_name] = ent
    return ent

def create_time_input(parent, label_text, entry_var_name, theme, fonts, entries, default="12:00:00"):
    """Factory for Time HH:MM:SS using dropdowns."""
    frame = tk.Frame(parent, bg=theme["card_bg"])
    frame.pack(side=tk.LEFT, padx=5)
    
    lbl = tk.Label(frame, text=label_text, bg=theme["card_bg"], fg=theme["text_dim"], 
                  font=("Segoe UI", 9))
    lbl.pack(anchor="w")
    
    time_frame = tk.Frame(frame, bg=theme["card_bg"])
    time_frame.pack()
    
    hours = [f"{i:02d}" for i in range(24)]
    mins = [f"{i:02d}" for i in range(60)]
    
    h_cb = ttk.Combobox(time_frame, values=hours, width=3, state="readonly", font=fonts["input"])
    m_cb = ttk.Combobox(time_frame, values=mins, width=3, state="readonly", font=fonts["input"])
    s_cb = ttk.Combobox(time_frame, values=mins, width=3, state="readonly", font=fonts["input"])
    
    h_cb.pack(side=tk.LEFT)
    tk.Label(time_frame, text=":", bg=theme["card_bg"], fg=theme["text_main"]).pack(side=tk.LEFT)
    m_cb.pack(side=tk.LEFT)
    tk.Label(time_frame, text=":", bg=theme["card_bg"], fg=theme["text_main"]).pack(side=tk.LEFT)
    s_cb.pack(side=tk.LEFT)
    
    wrapper = TimeEntryWrapper(h_cb, m_cb, s_cb)
    if default:
        wrapper.insert(0, str(default))
    else:
        wrapper.insert(0, "12:00:00")
        
    entries[entry_var_name] = wrapper
    return wrapper

def create_compact_detail(parent, label_text, theme, width=10):
    """Factory for compact readonly detail fields."""
    frame = tk.Frame(parent, bg=theme["card_bg"])
    frame.pack(side=tk.LEFT, padx=5)
    
    tk.Label(frame, text=label_text, bg=theme["card_bg"], fg=theme["text_dim"], 
             font=("Segoe UI", 9)).pack(anchor="w")
    
    ent = ttk.Entry(frame, width=width, font=("Segoe UI", 9))
    ent.pack()
    return ent

def create_tool_button(parent, text, command, accent_color, theme, fonts):
    """Factory for tool buttons with custom accent — Premium styling."""
    btn_container = tk.Frame(parent, bg=theme["card_bg_alt"], bd=0)
    
    # Accent strip — thicker for visual weight
    tk.Frame(btn_container, bg=accent_color, width=5).pack(side=tk.LEFT, fill=tk.Y)
    
    btn = tk.Button(btn_container, text=text, bg=theme["card_bg_alt"], 
                   fg=theme["text_main"], font=fonts["button_small"],
                   activebackground=theme["header_accent"], activeforeground=theme["primary"],
                   relief=tk.FLAT, bd=0, padx=18, pady=14, anchor="w",
                   cursor="hand2", command=command)
    btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Hover effects — smooth background + accent color text
    def _on_enter(e):
        btn.config(bg=theme["header_accent"], fg=accent_color)
    def _on_leave(e):
        btn.config(bg=theme["card_bg_alt"], fg=theme["text_main"])
    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)
    
    return btn_container
