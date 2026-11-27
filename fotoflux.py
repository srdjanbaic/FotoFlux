#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps

import os
import threading


APP_NAME = "FotoFlux"
VERSION = "1.0.1"


class FotoFlux:

    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {VERSION} - Linux Photo Editor")
        self.root.geometry("1250x800")
        self.root.minsize(950, 650)

        self.original = None
        self.current = None
        self.base_image = None
        self.right_effect_base = None
        self.preview_image = None
        self.undo_stack = []
        self.image_path = None
        self._updating_sliders = False
        self._preview_after_id = None
        self.selective_blur_strength = tk.DoubleVar(value=12.0)
        self._selective_busy = False
        self._rembg_session = None
        self._image_revision = 0

        self.brightness = tk.DoubleVar(value=1.0)
        self.contrast = tk.DoubleVar(value=1.0)
        self.saturation = tk.DoubleVar(value=1.0)
        self.sharpness = tk.DoubleVar(value=1.0)
        self.blur = tk.DoubleVar(value=0.0)
        self.temperature = tk.DoubleVar(value=0.0)

        self.filters = [
            ("Original", "Original"),
            ("Black & White", "bw"),
            ("Classic Mono", "classic_mono"),
            ("Noir", "noir"),
            ("Silver", "silver"),
            ("Sepia", "sepia"),
            ("Vintage", "vintage"),
            ("Retro 70s", "retro70"),
            ("Retro 80s", "retro80"),
            ("Polaroid", "polaroid"),
            ("Old Photo", "old_photo"),
            ("Faded Film", "faded"),
            ("Warm Film", "warm_film"),
            ("Cool Film", "cool_film"),
            ("Cinematic", "cinematic"),
            ("Teal & Orange", "teal_orange"),
            ("Drama", "drama"),
            ("Moody", "moody"),
            ("Dark Mood", "dark"),
            ("Night", "night"),
            ("Golden Hour", "golden"),
            ("Sunset", "sunset"),
            ("Summer", "summer"),
            ("Winter", "winter"),
            ("Autumn", "autumn"),
            ("Spring", "spring"),
            ("Pastel", "pastel"),
            ("Soft Colors", "soft"),
            ("Vivid", "vivid"),
            ("Color Boost", "color_boost"),
            ("Color Pop", "color_pop"),
            ("Oversaturated", "oversaturated"),
            ("Dreamy", "dreamy"),
            ("Soft Focus", "soft_focus"),
            ("Glow", "glow"),
            ("Romantic", "romantic"),
            ("Bright", "bright"),
            ("High Contrast", "high_contrast"),
            ("Matte", "matte"),
            ("Fade", "fade"),
            ("Dramatic B&W", "dramatic_bw"),
            ("Vintage Warm", "vintage_warm"),
            ("Vintage Cool", "vintage_cool"),
            ("Kodak Style", "kodak"),
            ("Fuji Style", "fuji"),
            ("Lomo", "lomo"),
            ("HDR Style", "hdr"),
            ("Sharpen", "sharpen"),
            ("Gaussian Blur", "gaussian"),
            ("Pixelate", "pixelate"),
            ("Posterize", "posterize"),
        ]

        self.build_interface()
        self.update_display()

    # --------------------------------------------------
    # INTERFACE
    # --------------------------------------------------

    def build_interface(self):

        self.root.configure(bg="#171923")

        style = ttk.Style()
        style.theme_use("clam")

        # Consistent modern dark theme with a violet accent.
        style.configure(
            "TButton",
            padding=(10, 7),
            background="#343a50",
            foreground="#eef0ff",
            borderwidth=0,
            focusthickness=0,
            font=("Sans", 9)
        )
        style.map(
            "TButton",
            background=[("active", "#454d68"), ("pressed", "#2c3144")],
            foreground=[("disabled", "#737b94")]
        )
        style.configure(
            "Primary.TButton",
            padding=(11, 8),
            background="#6558d3",
            foreground="#ffffff",
            borderwidth=0,
            font=("Sans", 9, "bold")
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#796cf0"), ("pressed", "#5145b5")]
        )
        style.configure(
            "TEntry",
            padding=7,
            fieldbackground="#1b2030",
            foreground="#eef0ff",
            insertcolor="#ffffff",
            bordercolor="#3b4052",
            lightcolor="#3b4052",
            darkcolor="#3b4052"
        )
        style.configure(
            "TScrollbar",
            background="#343a50",
            troughcolor="#1d2030",
            bordercolor="#1d2030",
            arrowcolor="#c7cbea"
        )

        style.configure(
            "TLabel",
            background="#242838",
            foreground="#eef0ff"
        )

        style.configure(
            "TFrame",
            background="#242838"
        )

        style.configure(
            "TNotebook",
            background="#242838"
        )

        style.configure(
            "TNotebook.Tab",
            padding=(10, 6)
        )

        # TOP BAR

        topbar = tk.Frame(
            self.root,
            bg="#1d2030",
            height=62
        )

        topbar.pack(
            side=tk.TOP,
            fill=tk.X
        )

        topbar.pack_propagate(False)

        title = tk.Label(
            topbar,
            text="FotoFlux",
            font=("Sans", 20, "bold"),
            fg="#ffffff",
            bg="#1d2030"
        )

        title.pack(
            side=tk.LEFT,
            padx=20
        )

        version = tk.Label(
            topbar,
            text="PHOTO EDITOR  •  VERSION 1.0.1",
            font=("Sans", 9),
            fg="#a7adc4",
            bg="#1d2030"
        )

        version.pack(
            side=tk.LEFT,
            padx=8
        )

        ttk.Button(
            topbar,
            text="＋  Open Image",
            command=self.open_image,
            style="Primary.TButton"
        ).pack(
            side=tk.RIGHT,
            padx=10,
            pady=8
        )

        ttk.Button(
            topbar,
            text="Save As",
            command=self.save_image
        ).pack(
            side=tk.RIGHT,
            padx=5,
            pady=8
        )

        # MAIN AREA

        main = tk.Frame(
            self.root,
            bg="#171923"
        )

        main.pack(
            fill=tk.BOTH,
            expand=True
        )

        # LEFT PANEL

        left = tk.Frame(
            main,
            bg="#242838",
            width=245
        )

        left.pack(
            side=tk.LEFT,
            fill=tk.Y
        )

        left.pack_propagate(False)

        left_canvas = tk.Canvas(
            left,
            bg="#242838",
            highlightthickness=0,
            borderwidth=0
        )

        left_scrollbar = ttk.Scrollbar(
            left,
            orient=tk.VERTICAL,
            command=left_canvas.yview
        )

        left_canvas.configure(
            yscrollcommand=left_scrollbar.set
        )

        left_scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        left_canvas.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        controls = tk.Frame(
            left_canvas,
            bg="#242838"
        )

        controls_window = left_canvas.create_window(
            (0, 0),
            window=controls,
            anchor=tk.NW
        )

        def update_left_scrollregion(event=None):
            left_canvas.configure(
                scrollregion=left_canvas.bbox("all")
            )

        def resize_left_controls(event):
            left_canvas.itemconfigure(
                controls_window,
                width=event.width
            )

        controls.bind(
            "<Configure>",
            update_left_scrollregion
        )

        left_canvas.bind(
            "<Configure>",
            resize_left_controls
        )

        def scroll_left_panel(event):
            if event.num == 4:
                left_canvas.yview_scroll(-3, "units")
            elif event.num == 5:
                left_canvas.yview_scroll(3, "units")
            else:
                left_canvas.yview_scroll(
                    int(-1 * (event.delta / 120) * 3),
                    "units"
                )

        left_canvas.bind(
            "<MouseWheel>",
            scroll_left_panel
        )

        left_canvas.bind(
            "<Button-4>",
            scroll_left_panel
        )

        left_canvas.bind(
            "<Button-5>",
            scroll_left_panel
        )

        tk.Label(
            controls,
            text="IMAGE ADJUSTMENTS",
            font=("Sans", 10, "bold"),
            bg="#242838",
            fg="#ffffff"
        ).pack(
            anchor=tk.W,
            padx=15,
            pady=(18, 14)
        )

        self.create_slider(
            controls,
            "Brightness",
            self.brightness,
            0.0,
            2.0
        )

        self.create_slider(
            controls,
            "Contrast",
            self.contrast,
            0.0,
            2.0
        )

        self.create_slider(
            controls,
            "Saturation",
            self.saturation,
            0.0,
            2.0
        )

        self.create_slider(
            controls,
            "Sharpness",
            self.sharpness,
            0.0,
            3.0
        )

        self.create_slider(
            controls,
            "Blur",
            self.blur,
            0.0,
            10.0
        )

        self.create_slider(
            controls,
            "Temperature",
            self.temperature,
            -100.0,
            100.0
        )

        ttk.Button(
            controls,
            text="Apply Adjustments",
            command=self.apply_adjustments,
            style="Primary.TButton"
        ).pack(
            fill=tk.X,
            padx=12,
            pady=(12, 5)
        )

        ttk.Button(
            controls,
            text="Reset Adjustments",
            command=self.reset_adjustments
        ).pack(
            fill=tk.X,
            padx=12,
            pady=5
        )

        ttk.Button(
            controls,
            text="Rotate Left",
            command=lambda: self.rotate(90)
        ).pack(
            fill=tk.X,
            padx=12,
            pady=(15, 5)
        )

        ttk.Button(
            controls,
            text="Rotate Right",
            command=lambda: self.rotate(-90)
        ).pack(
            fill=tk.X,
            padx=12,
            pady=5
        )

        ttk.Button(
            controls,
            text="Flip Horizontal",
            command=self.flip_horizontal
        ).pack(
            fill=tk.X,
            padx=12,
            pady=5
        )

        ttk.Button(
            controls,
            text="Flip Vertical",
            command=self.flip_vertical
        ).pack(
            fill=tk.X,
            padx=12,
            pady=5
        )

        ttk.Button(
            controls,
            text="Undo",
            command=self.undo
        ).pack(
            fill=tk.X,
            padx=12,
            pady=(15, 5)
        )

        ttk.Button(
            controls,
            text="Reset Image",
            command=self.reset_image
        ).pack(
            fill=tk.X,
            padx=12,
            pady=5
        )

        # CENTER IMAGE VIEW

        center = tk.Frame(
            main,
            bg="#151925"
        )

        center.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        self.canvas = tk.Canvas(
            center,
            bg="#151925",
            highlightthickness=0
        )

        self.canvas.pack(
            fill=tk.BOTH,
            expand=True,
            padx=16,
            pady=16
        )

        self.canvas.bind(
            "<Configure>",
            lambda event: self.update_display()
        )

        # RIGHT FILTER PANEL

        right = tk.Frame(
            main,
            bg="#242838",
            width=260
        )

        right.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        right.pack_propagate(False)

        tk.Label(
            right,
            text="FILTERS",
            font=("Sans", 10, "bold"),
            bg="#242838",
            fg="#ffffff"
        ).pack(
            anchor=tk.W,
            padx=15,
            pady=(18, 14)
        )

        self.filter_search = tk.StringVar()

        search = ttk.Entry(
            right,
            textvariable=self.filter_search
        )

        search.pack(
            fill=tk.X,
            padx=10,
            pady=(0, 8)
        )

        search.insert(
            0,
            ""
        )

        self.filter_search.trace_add(
            "write",
            lambda *args: self.populate_filters()
        )

        # Keep the Original filter fixed above the scrollable filter list.
        original_button = ttk.Button(
            right,
            text="↺  Original",
            command=lambda: self.apply_filter("Original", "Original"),
            style="Original.TButton"
        )

        original_button.pack(
            fill=tk.X,
            padx=10,
            pady=(0, 8)
        )

        # AI-powered selective blur controls
        tk.Label(
            right, text="SELECTIVE BLUR", font=("Sans", 9, "bold"),
            bg="#242838", fg="#ffffff"
        ).pack(anchor=tk.W, padx=12, pady=(3, 5))

        strength_frame = tk.Frame(right, bg="#242838")
        strength_frame.pack(fill=tk.X, padx=10, pady=(0, 4))
        tk.Label(
            strength_frame, text="Strength", bg="#242838", fg="#c7cbea",
            font=("Sans", 8)
        ).pack(anchor=tk.W)
        tk.Scale(
            strength_frame, variable=self.selective_blur_strength,
            from_=2, to=30, resolution=1, orient=tk.HORIZONTAL,
            bg="#242838", fg="#eef0ff", highlightthickness=0,
            troughcolor="#3b4052", activebackground="#9a8cff",
            sliderlength=16, width=10, bd=0, font=("Sans", 8)
        ).pack(fill=tk.X)

        self.foreground_blur_button = ttk.Button(
            right, text="Foreground Blur",
            command=lambda: self.apply_selective_blur("foreground")
        )
        self.foreground_blur_button.pack(fill=tk.X, padx=10, pady=2)

        self.background_blur_button = ttk.Button(
            right, text="Background Blur", style="Primary.TButton",
            command=lambda: self.apply_selective_blur("background")
        )
        self.background_blur_button.pack(fill=tk.X, padx=10, pady=(2, 8))

        style.configure(
            "Original.TButton",
            padding=(10, 9),
            background="#6558d3",
            foreground="#ffffff",
            font=("Sans", 10, "bold")
        )

        style.map(
            "Original.TButton",
            background=[("active", "#796cf0"), ("pressed", "#5145b5")],
            foreground=[("disabled", "#a7adc4")]
        )

        tk.Frame(
            right,
            bg="#3b4052",
            height=1
        ).pack(
            fill=tk.X,
            padx=10,
            pady=(0, 8)
        )

        filter_frame = tk.Frame(
            right,
            bg="#242838"
        )

        filter_frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        self.filter_canvas = tk.Canvas(
            filter_frame,
            bg="#242838",
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            filter_frame,
            orient=tk.VERTICAL,
            command=self.filter_canvas.yview
        )

        self.filter_canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.filter_canvas.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        self.filter_list_frame = tk.Frame(
            self.filter_canvas,
            bg="#242838"
        )

        self.filter_window = self.filter_canvas.create_window(
            (0, 0),
            window=self.filter_list_frame,
            anchor=tk.NW
        )

        self.filter_list_frame.bind(
            "<Configure>",
            lambda event: self.filter_canvas.configure(
                scrollregion=self.filter_canvas.bbox("all")
            )
        )

        self.filter_canvas.bind(
            "<Configure>",
            lambda event: self.filter_canvas.itemconfigure(
                self.filter_window,
                width=event.width
            )
        )

        self.populate_filters()

        # BOTTOM BAR

        bottom = tk.Frame(
            self.root,
            bg="#1d2030",
            height=35
        )

        bottom.pack(
            side=tk.BOTTOM,
            fill=tk.X
        )

        bottom.pack_propagate(False)

        self.status = tk.Label(
            bottom,
            text="Ready - Open an image to begin",
            fg="#b8bfd6",
            bg="#1d2030",
            anchor=tk.W,
            font=("Sans", 9)
        )

        self.status.pack(
            fill=tk.BOTH,
            padx=14
        )

    # --------------------------------------------------
    # SLIDERS
    # --------------------------------------------------

    def create_slider(
        self,
        parent,
        name,
        variable,
        minimum,
        maximum
    ):

        frame = tk.Frame(
            parent,
            bg="#242838"
        )

        frame.pack(
            fill=tk.X,
            padx=12,
            pady=7
        )

        label = tk.Label(
            frame,
            text=name,
            bg="#242838",
            fg="#eef0ff",
            anchor=tk.W
        )

        label.pack(
            fill=tk.X
        )

        slider = tk.Scale(
            frame,
            variable=variable,
            from_=minimum,
            to=maximum,
            resolution=0.05 if name != "Temperature" else 1,
            orient=tk.HORIZONTAL,
            bg="#242838",
            fg="#eef0ff",
            highlightthickness=0,
            troughcolor="#3b4052",
            activebackground="#9a8cff",
            sliderlength=18,
            width=12,
            bd=0,
            font=("Sans", 8),
            command=self.on_adjustment_change
        )

        slider.pack(
            fill=tk.X
        )

    # --------------------------------------------------
    # FILTER LIST
    # --------------------------------------------------

    def populate_filters(self):

        for widget in self.filter_list_frame.winfo_children():
            widget.destroy()

        search_text = self.filter_search.get().lower()

        for name, key in self.filters:

            # Original has its own fixed button above the scrollable list.
            if key == "Original":
                continue

            if search_text and search_text not in name.lower():
                continue

            button = ttk.Button(
                self.filter_list_frame,
                text=name,
                command=lambda k=key, n=name: self.apply_filter(k, n)
            )

            button.pack(
                fill=tk.X,
                padx=8,
                pady=2
            )

    # --------------------------------------------------
    # OPEN IMAGE
    # --------------------------------------------------

    def open_image(self):

        self.cancel_pending_preview()
        path = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff *.gif"),
                ("All files", "*.*")
            ]
        )

        if not path:
            return

        try:

            image = Image.open(path)

            image = ImageOps.exif_transpose(image)

            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")

            self.original = image.copy()
            self.current = image.copy()
            self.base_image = image.copy()
            self.right_effect_base = None
            self.image_path = path
            self._image_revision += 1

            self.undo_stack.clear()

            self.reset_slider_values()

            self.status.config(
                text=f"Opened: {os.path.basename(path)}"
            )

            self.update_display()

        except Exception as error:

            messagebox.showerror(
                "Open Error",
                str(error)
            )

    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------

    def update_display(self):

        if self.current is None:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width < 10 or canvas_height < 10:
            return

        image = self.preview_image if self.preview_image is not None else self.current

        display_image = image.copy()

        display_image.thumbnail(
            (
                canvas_width - 40,
                canvas_height - 40
            ),
            Image.Resampling.LANCZOS
        )

        self.tk_image = ImageTk.PhotoImage(
            display_image
        )

        self.canvas.delete("all")

        self.canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=self.tk_image,
            anchor=tk.CENTER
        )

    # --------------------------------------------------
    # UNDO
    # --------------------------------------------------

    def save_undo(self):

        if self.current is not None:
            self._image_revision += 1

            self.undo_stack.append({
                "current": self.current.copy(),
                "base_image": (
                    self.base_image.copy()
                    if self.base_image is not None else None
                ),
                "right_effect_base": (
                    self.right_effect_base.copy()
                    if self.right_effect_base is not None else None
                ),
                "sliders": (
                    self.brightness.get(),
                    self.contrast.get(),
                    self.saturation.get(),
                    self.sharpness.get(),
                    self.blur.get(),
                    self.temperature.get()
                )
            })

            if len(self.undo_stack) > 20:
                self.undo_stack.pop(0)

    def undo(self):

        if not self.undo_stack:
            return

        self.cancel_pending_preview()
        state = self.undo_stack.pop()

        self.current = state["current"]
        self.base_image = state["base_image"]
        self.right_effect_base = state["right_effect_base"]
        self.preview_image = None

        self._updating_sliders = True
        try:
            self.brightness.set(state["sliders"][0])
            self.contrast.set(state["sliders"][1])
            self.saturation.set(state["sliders"][2])
            self.sharpness.set(state["sliders"][3])
            self.blur.set(state["sliders"][4])
            self.temperature.set(state["sliders"][5])
        finally:
            self._updating_sliders = False

        self.update_live_preview()
        self.status.config(text="Undo completed")

    # --------------------------------------------------
    # ADJUSTMENTS
    # --------------------------------------------------

    def reset_slider_values(self):

        # Prevent slider callbacks while restoring their default values.
        self._updating_sliders = True
        try:
            self.brightness.set(1.0)
            self.contrast.set(1.0)
            self.saturation.set(1.0)
            self.sharpness.set(1.0)
            self.blur.set(0.0)
            self.temperature.set(0.0)
        finally:
            self._updating_sliders = False

    def on_adjustment_change(self, value=None):

        """Schedule a lightweight, debounced live preview."""
        if self._updating_sliders or self.current is None:
            return

        # Do not process every tiny mouse movement. Keep only the newest one.
        if self._preview_after_id is not None:
            try:
                self.root.after_cancel(self._preview_after_id)
            except tk.TclError:
                pass

        self._preview_after_id = self.root.after(45, self.update_live_preview)

    def update_live_preview(self):

        self._preview_after_id = None

        if self.current is None or self._updating_sliders:
            return

        try:
            # A small preview is enough while dragging; full resolution is
            # retained in self.current and used when Apply Adjustments is pressed.
            preview = self.current.copy()
            preview.thumbnail((700, 700), Image.Resampling.BILINEAR)
            self.preview_image = self.adjust_image(preview)
            self.update_display()
            self.status.config(text="Live preview - press Apply Adjustments to commit")
        except Exception as error:
            self.preview_image = None
            self.update_display()
            self.status.config(text=f"Preview error: {error}")

    def cancel_pending_preview(self):

        if self._preview_after_id is not None:
            try:
                self.root.after_cancel(self._preview_after_id)
            except tk.TclError:
                pass
            self._preview_after_id = None

    def adjust_image(self, image):

        result = image.copy()

        result = ImageEnhance.Brightness(
            result
        ).enhance(
            self.brightness.get()
        )

        result = ImageEnhance.Contrast(
            result
        ).enhance(
            self.contrast.get()
        )

        result = ImageEnhance.Color(
            result
        ).enhance(
            self.saturation.get()
        )

        result = ImageEnhance.Sharpness(
            result
        ).enhance(
            self.sharpness.get()
        )

        blur_value = self.blur.get()

        if blur_value > 0:

            result = result.filter(
                ImageFilter.GaussianBlur(
                    radius=blur_value
                )
            )

        temp = self.temperature.get()

        if temp != 0:

            result = self.apply_temperature(
                result,
                temp
            )

        return result

    def apply_temperature(self, image, value):

        image = image.convert("RGB")

        r, g, b = image.split()

        value = value / 100.0

        r = r.point(
            lambda x: max(
                0,
                min(
                    255,
                    int(x + value * 45)
                )
            )
        )

        b = b.point(
            lambda x: max(
                0,
                min(
                    255,
                    int(x - value * 45)
                )
            )
        )

        return Image.merge(
            "RGB",
            (r, g, b)
        )

    def apply_adjustments(self):

        if self.current is None:
            return

        self.cancel_pending_preview()
        self.save_undo()

        self.current = self.adjust_image(self.current)

        if self.right_effect_base is not None:
            self.right_effect_base = self.adjust_image(
                self.right_effect_base
            )

        self.base_image = self.current.copy()

        self.preview_image = None

        self.reset_slider_values()

        self.update_display()

        self.status.config(
            text="Adjustments applied"
        )

    def reset_adjustments(self):

        if self.current is None:
            return

        self.cancel_pending_preview()
        self.preview_image = None

        self.reset_slider_values()

        self.update_display()

    # --------------------------------------------------
    # FILTER ENGINE
    # --------------------------------------------------

    def apply_filter(self, key, name):

        if self.current is None:
            messagebox.showinfo(
                "FotoFlux",
                "Please open an image first."
            )
            return

        self.cancel_pending_preview()

        if key == "Original":

            if self.right_effect_base is None:
                return

            self.save_undo()
            self.current = self.right_effect_base.copy()
            self.base_image = self.current.copy()
            self.right_effect_base = None
            self.preview_image = None
            self.update_live_preview()
            self.status.config(text="Right-panel effects removed")
            return

        self.save_undo()
        image = self.current.copy().convert("RGB")

        try:
            result = self.filter_engine(image, key)

            if self.right_effect_base is None:
                self.right_effect_base = self.current.copy()

            self.current = result.convert("RGB")
            self.base_image = self.current.copy()
            self.preview_image = None
            self.update_live_preview()
            self.status.config(text=f"Filter applied: {name}")

        except Exception as error:
            if self.undo_stack:
                self.undo_stack.pop()
            messagebox.showerror("Filter Error", str(error))

    def filter_engine(self, image, key):

        # BASIC EFFECTS

        if key in ("bw", "classic_mono"):
            image = ImageOps.grayscale(image).convert("RGB")

            if key == "classic_mono":
                image = ImageEnhance.Contrast(image).enhance(1.15)

            return image

        if key == "noir":
            image = ImageOps.grayscale(image)
            image = ImageEnhance.Contrast(image).enhance(2.0)
            image = ImageEnhance.Brightness(image).enhance(0.9)
            return image.convert("RGB")

        if key == "silver":
            image = ImageOps.grayscale(image)
            image = ImageEnhance.Contrast(image).enhance(1.3)
            return image.convert("RGB")

        if key == "dramatic_bw":
            image = ImageOps.grayscale(image)
            image = ImageEnhance.Contrast(image).enhance(1.8)
            image = ImageEnhance.Sharpness(image).enhance(1.5)
            return image.convert("RGB")

        if key == "sepia":
            image = ImageOps.grayscale(image)
            image = ImageOps.colorize(
                image,
                "#21130b",
                "#e5c18b"
            )
            return image.convert("RGB")

        if key == "old_photo":
            image = ImageOps.grayscale(image)
            image = ImageOps.colorize(
                image,
                "#36251a",
                "#d2b58c"
            )
            image = ImageEnhance.Contrast(image).enhance(0.8)
            return image.convert("RGB")

        if key == "faded":
            image = ImageEnhance.Contrast(image).enhance(0.7)
            image = ImageEnhance.Color(image).enhance(0.8)
            image = ImageEnhance.Brightness(image).enhance(1.1)
            return image

        if key == "matte":
            image = ImageEnhance.Contrast(image).enhance(0.75)
            image = ImageEnhance.Color(image).enhance(0.9)
            return image

        if key == "fade":
            image = ImageEnhance.Contrast(image).enhance(0.8)
            image = ImageEnhance.Brightness(image).enhance(1.05)
            return image

        # COLOR AND TONE

        if key == "vivid":
            image = ImageEnhance.Color(image).enhance(1.6)
            image = ImageEnhance.Contrast(image).enhance(1.15)
            return image

        if key == "color_boost":
            image = ImageEnhance.Color(image).enhance(1.35)
            image = ImageEnhance.Contrast(image).enhance(1.1)
            return image

        if key == "color_pop":
            image = ImageEnhance.Color(image).enhance(1.8)
            image = ImageEnhance.Contrast(image).enhance(1.2)
            return image

        if key == "oversaturated":
            image = ImageEnhance.Color(image).enhance(2.0)
            return image

        if key == "pastel":
            image = ImageEnhance.Color(image).enhance(0.65)
            image = ImageEnhance.Brightness(image).enhance(1.15)
            image = ImageEnhance.Contrast(image).enhance(0.85)
            return image

        if key == "soft":
            image = ImageEnhance.Color(image).enhance(0.8)
            image = ImageEnhance.Contrast(image).enhance(0.85)
            image = ImageEnhance.Brightness(image).enhance(1.08)
            return image

        if key == "bright":
            image = ImageEnhance.Brightness(image).enhance(1.25)
            return image

        if key == "high_contrast":
            image = ImageEnhance.Contrast(image).enhance(1.7)
            return image

        # VINTAGE AND FILM

        if key in ("vintage", "vintage_warm", "retro70", "polaroid"):

            image = ImageEnhance.Color(image).enhance(0.75)
            image = ImageEnhance.Contrast(image).enhance(0.85)
            image = self.apply_temperature(image, 25)

            if key == "polaroid":
                image = ImageEnhance.Brightness(image).enhance(1.1)

            if key == "retro70":
                image = ImageEnhance.Color(image).enhance(1.1)

            return image

        if key in ("vintage_cool", "cool_film", "winter"):

            image = self.apply_temperature(image, -30)
            image = ImageEnhance.Contrast(image).enhance(0.9)

            if key == "winter":
                image = ImageEnhance.Brightness(image).enhance(1.1)

            return image

        if key in ("warm_film", "golden", "sunset", "summer", "autumn", "romantic"):

            amount = 25

            if key == "golden":
                amount = 40

            if key == "sunset":
                amount = 55

            if key == "summer":
                amount = 30

            if key == "autumn":
                amount = 45

            if key == "romantic":
                amount = 25

            image = self.apply_temperature(image, amount)

            image = ImageEnhance.Color(image).enhance(1.15)

            if key in ("golden", "sunset"):
                image = ImageEnhance.Brightness(image).enhance(1.1)

            if key == "romantic":
                image = ImageEnhance.Contrast(image).enhance(0.85)

            return image

        if key == "retro80":

            image = ImageEnhance.Color(image).enhance(1.35)
            image = self.apply_temperature(image, 15)
            image = ImageEnhance.Contrast(image).enhance(1.1)

            return image

        if key == "kodak":

            image = ImageEnhance.Color(image).enhance(1.15)
            image = ImageEnhance.Contrast(image).enhance(1.05)
            image = self.apply_temperature(image, 18)

            return image

        if key == "fuji":

            image = ImageEnhance.Color(image).enhance(1.1)
            image = ImageEnhance.Contrast(image).enhance(0.95)
            image = self.apply_temperature(image, -8)

            return image

        if key == "lomo":

            image = ImageEnhance.Color(image).enhance(1.5)
            image = ImageEnhance.Contrast(image).enhance(1.5)

            return image

        # CINEMATIC

        if key in ("cinematic", "teal_orange", "drama", "moody", "dark", "night"):

            image = ImageEnhance.Contrast(image).enhance(1.25)

            if key == "cinematic":
                image = self.apply_temperature(image, -15)

            if key == "teal_orange":
                image = self.apply_temperature(image, -20)
                image = ImageEnhance.Color(image).enhance(1.35)

            if key == "drama":
                image = ImageEnhance.Contrast(image).enhance(1.5)
                image = ImageEnhance.Sharpness(image).enhance(1.4)

            if key == "moody":
                image = ImageEnhance.Brightness(image).enhance(0.85)
                image = ImageEnhance.Color(image).enhance(0.8)

            if key == "dark":
                image = ImageEnhance.Brightness(image).enhance(0.65)
                image = ImageEnhance.Contrast(image).enhance(1.3)

            if key == "night":
                image = ImageEnhance.Brightness(image).enhance(0.75)
                image = self.apply_temperature(image, -35)

            return image

        # DREAMY AND SOFT

        if key in ("dreamy", "soft_focus", "glow"):

            blurred = image.filter(
                ImageFilter.GaussianBlur(
                    radius=3
                )
            )

            image = Image.blend(
                image,
                blurred,
                0.35
            )

            image = ImageEnhance.Brightness(image).enhance(1.1)

            if key == "glow":
                image = Image.blend(
                    image,
                    image.filter(
                        ImageFilter.GaussianBlur(8)
                    ),
                    0.4
                )

            return image

        if key == "sharpen":

            return image.filter(
                ImageFilter.UnsharpMask(
                    radius=2,
                    percent=180,
                    threshold=3
                )
            )

        if key == "gaussian":

            return image.filter(
                ImageFilter.GaussianBlur(
                    radius=4
                )
            )

        if key == "pixelate":

            width, height = image.size

            small = image.resize(
                (
                    max(1, width // 20),
                    max(1, height // 20)
                ),
                Image.Resampling.NEAREST
            )

            return small.resize(
                (
                    width,
                    height
                ),
                Image.Resampling.NEAREST
            )

        if key == "posterize":

            return ImageOps.posterize(
                image,
                bits=4
            )

        if key == "hdr":

            image = ImageEnhance.Contrast(image).enhance(1.5)
            image = ImageEnhance.Sharpness(image).enhance(2.0)
            image = ImageEnhance.Color(image).enhance(1.2)

            return image

        return image

    # --------------------------------------------------
    # AI SELECTIVE BLUR
    # --------------------------------------------------

    def apply_selective_blur(self, target):
        """Blur only the detected foreground or background using rembg."""
        if self.current is None:
            messagebox.showinfo("FotoFlux", "Please open an image first.")
            return

        if self._selective_busy:
            return

        self.cancel_pending_preview()
        self.preview_image = None
        source = self.current.copy().convert("RGB")
        revision = self._image_revision
        radius = float(self.selective_blur_strength.get())
        self._selective_busy = True
        self.foreground_blur_button.configure(state="disabled")
        self.background_blur_button.configure(state="disabled")
        self.status.config(text="AI is detecting the main subject... Please wait")

        def worker():
            try:
                from rembg import new_session, remove

                if self._rembg_session is None:
                    self._rembg_session = new_session("u2net")

                # Segment a reduced copy for better performance, then enlarge mask.
                analysis_image = source.copy()
                analysis_image.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
                mask = remove(
                    analysis_image, session=self._rembg_session,
                    only_mask=True, post_process_mask=True
                )
                if not isinstance(mask, Image.Image):
                    mask = Image.fromarray(mask)
                mask = mask.convert("L").resize(source.size, Image.Resampling.LANCZOS)
                # Feather the boundary to avoid a hard cutout edge.
                feather = max(1.5, min(5.0, min(source.size) / 350.0))
                mask = mask.filter(ImageFilter.GaussianBlur(radius=feather))

                blurred = source.filter(ImageFilter.GaussianBlur(radius=radius))
                if target == "background":
                    # White mask = subject; invert it to blur the background.
                    blend_mask = ImageOps.invert(mask)
                else:
                    blend_mask = mask
                result = Image.composite(blurred, source, blend_mask)
                self.root.after(0, lambda: self._finish_selective_blur(
                    result, target, revision, None
                ))
            except Exception as error:
                error_text = str(error)
                self.root.after(0, lambda msg=error_text: self._finish_selective_blur(
                    None, target, revision, msg
                ))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_selective_blur(self, result, target, revision, error):
        self._selective_busy = False
        self.foreground_blur_button.configure(state="normal")
        self.background_blur_button.configure(state="normal")

        if revision != self._image_revision:
            self.status.config(text="Selective blur cancelled because the image changed")
            return

        if error:
            if "No module named 'rembg'" in error or "rembg" in error.lower() and "module" in error.lower():
                messagebox.showerror(
                    "AI Selective Blur - Missing component",
                    "The AI segmentation package is not installed.\n\n"
                    "Install it in a Python virtual environment with:\n\n"
                    "python3 -m venv .venv\n"
                    "source .venv/bin/activate\n"
                    "python -m pip install --upgrade pip\n"
                    "python -m pip install Pillow \"rembg[cpu]\"\n\n"
                    "Then start FotoFlux using the Python interpreter from .venv."
                )
            else:
                messagebox.showerror("Selective Blur Error", error)
            self.status.config(text="Selective blur could not be completed")
            return

        self.save_undo()

        if self.right_effect_base is None:
            self.right_effect_base = self.current.copy()

        self.current = result.convert("RGB")
        self.base_image = self.current.copy()
        self.preview_image = None
        self.update_live_preview()
        label = "Background Blur" if target == "background" else "Foreground Blur"
        self.status.config(text=f"{label} applied successfully")

    # --------------------------------------------------
    # ROTATION AND FLIP
    # --------------------------------------------------

    def rotate(self, angle):

        if self.current is None:
            return

        self.save_undo()

        self.current = self.current.rotate(angle, expand=True)

        if self.right_effect_base is not None:
            self.right_effect_base = self.right_effect_base.rotate(
                angle, expand=True
            )

        self.base_image = self.current.copy()
        self.preview_image = None
        self.update_live_preview()

    def flip_horizontal(self):

        if self.current is None:
            return

        self.save_undo()

        self.current = ImageOps.mirror(self.current)

        if self.right_effect_base is not None:
            self.right_effect_base = ImageOps.mirror(
                self.right_effect_base
            )

        self.base_image = self.current.copy()
        self.preview_image = None
        self.update_live_preview()

    def flip_vertical(self):

        if self.current is None:
            return

        self.save_undo()

        self.current = ImageOps.flip(self.current)

        if self.right_effect_base is not None:
            self.right_effect_base = ImageOps.flip(
                self.right_effect_base
            )

        self.base_image = self.current.copy()
        self.preview_image = None
        self.update_live_preview()

    # --------------------------------------------------
    # RESET
    # --------------------------------------------------

    def reset_image(self):

        if self.original is None:
            return

        self.save_undo()

        self.current = self.original.copy()

        self.base_image = self.current.copy()
        self.right_effect_base = None

        self.preview_image = None

        self.reset_slider_values()

        self.update_display()

        self.status.config(
            text="Original image restored"
        )

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    def save_image(self):

        if self.current is None:
            messagebox.showinfo(
                "FotoFlux",
                "Please open an image first."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save Image",
            defaultextension=".jpg",
            filetypes=[
                ("JPEG", "*.jpg"),
                ("PNG", "*.png"),
                ("WebP", "*.webp"),
                ("TIFF", "*.tiff"),
                ("BMP", "*.bmp")
            ]
        )

        if not path:
            return

        try:

            image = self.current.copy()

            if path.lower().endswith((".jpg", ".jpeg")):

                image = image.convert("RGB")

                image.save(
                    path,
                    quality=95
                )

            elif path.lower().endswith(".webp"):

                image.save(
                    path,
                    quality=95
                )

            else:

                image.save(path)

            self.status.config(
                text=f"Saved: {os.path.basename(path)}"
            )

            messagebox.showinfo(
                "FotoFlux",
                "Image successfully saved."
            )

        except Exception as error:

            messagebox.showerror(
                "Save Error",
                str(error)
            )

# ------------------------------------------------------
# APPLICATION START
# ------------------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = FotoFlux(root)

    root.mainloop()