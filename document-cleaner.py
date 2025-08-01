# Document Image Cleaner - GUI Tool
# Copyright (C) 2025 Orange Data & ChatGPT (OpenAI assisted)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

#!/usr/bin/env python3

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import subprocess
import sys
from datetime import datetime

class DocumentCleanerApp:
    def __init__(self, master, initial_file=None):
        self.master = master
        self.master.title("Document Image Cleaner")

        self.original_image = None
        self.processed_image = None
        self.original_path = ""
        self.is_dragged = False
        self.ocr_lang = "ita"  # Default OCR language
        self.threshold_value = "60%"
        self.deskew_value = "40%"

        self.ocr_available = self.check_ocr_dependencies()

        self.setup_gui()

        # Drag-and-drop support
        self.master.drop_target_register(tkdnd.DND_FILES)
        self.master.dnd_bind('<<Drop>>', self.drop_image)

        if initial_file:
            self.load_image(initial_file)

    def check_ocr_dependencies(self):
        missing = []
        required_langs = ["ita", "eng", "deu"]
        try:
            output = subprocess.check_output(["tesseract", "--list-langs"], stderr=subprocess.STDOUT).decode()
            installed = [line.strip() for line in output.splitlines()[1:]]
            for lang in required_langs:
                if lang not in installed:
                    missing.append(lang)
        except Exception as e:
            messagebox.showwarning("OCR not available", f"Tesseract not available: {e}")
            return False

        if missing:
            messagebox.showwarning("Missing languages", f"Following OCR languages are not installed: {', '.join(missing)}\n\nInstall with:\nsudo apt install " + ' '.join(f"tesseract-ocr-{lang}" for lang in missing))
            return False

        return True

    def setup_gui(self):
        # Buttons
        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Open img", command=self.open_image).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Reload img", command=self.reload_image).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Threshold", command=self.apply_threshold).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Deskew", command=self.apply_deskew).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Crop", command=self.apply_crop).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save JPG", command=self.save_jpg).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save PDF", command=self.save_pdf).pack(side=tk.LEFT, padx=5)

        self.btn_ocr = tk.Button(btn_frame, text="Save PDF + OCR", command=self.save_pdf_ocr, state=(tk.NORMAL if self.ocr_available else tk.DISABLED))
        self.btn_ocr.pack(side=tk.LEFT, padx=5)

        # Dropdowns for threshold, deskew, OCR language
        settings_frame = tk.Frame(self.master)
        settings_frame.pack(pady=5)

        # Threshold selection
        tk.Label(settings_frame, text="Threshold:").pack(side=tk.LEFT)
        thresh_options = ["40%", "50%", "60%", "70%"]
        self.thresh_var = tk.StringVar(value=self.threshold_value)
        tk.OptionMenu(settings_frame, self.thresh_var, *thresh_options, command=self.set_threshold).pack(side=tk.LEFT)

        # Deskew selection
        tk.Label(settings_frame, text="Deskew:").pack(side=tk.LEFT, padx=(10, 0))
        deskew_options = ["20%", "30%", "40%", "50%"]
        self.deskew_var = tk.StringVar(value=self.deskew_value)
        tk.OptionMenu(settings_frame, self.deskew_var, *deskew_options, command=self.set_deskew).pack(side=tk.LEFT)

        # OCR language selection
        tk.Label(settings_frame, text="OCR language:").pack(side=tk.LEFT, padx=(10, 0))
        lang_options = ["ita", "eng", "deu"]
        self.lang_var = tk.StringVar(value=self.ocr_lang)
        lang_menu = tk.OptionMenu(settings_frame, self.lang_var, *lang_options, command=self.set_ocr_lang)
        lang_menu.pack(side=tk.LEFT)
        if not self.ocr_available:
            lang_menu.configure(state=tk.DISABLED)

        # Image panels
        img_frame = tk.Frame(self.master)
        img_frame.pack()

        self.original_label = tk.Label(img_frame, text="Original")
        self.original_label.pack(side=tk.LEFT, padx=5)

        self.processed_label = tk.Label(img_frame, text="Modified")
        self.processed_label.pack(side=tk.LEFT, padx=5)

    def set_ocr_lang(self, value):
        self.ocr_lang = value

    def set_threshold(self, value):
        self.threshold_value = value

    def set_deskew(self, value):
        self.deskew_value = value

    def open_image(self):
        path = filedialog.askopenfilename(filetypes=[["Image Files", "*.png *.jpg *.jpeg *.tif"]])
        if path:
            self.is_dragged = False
            self.load_image(path)

    def drop_image(self, event):
        files = self.master.tk.splitlist(event.data)
        if files:
            self.is_dragged = True
            self.load_image(files[0])

    def load_image(self, path):
        try:
            self.original_path = path
            self.original_image = Image.open(path)
            self.display_image(self.original_image, self.original_label)
            self.processed_image = self.original_image.copy()
            self.display_image(self.processed_image, self.processed_label)
        except Exception as e:
            messagebox.showerror("Error opening image", str(e))

    def reload_image(self):
        if self.original_image:
            self.processed_image = self.original_image.copy()
            self.display_image(self.processed_image, self.processed_label)

    def display_image(self, img, label):
        img_resized = img.copy()
        img_resized.thumbnail((800, 800))
        img_tk = ImageTk.PhotoImage(img_resized)
        label.configure(image=img_tk)
        label.image = img_tk

    def apply_threshold(self):
        self.run_imagemagick(["-colorspace", "Gray", "-threshold", self.threshold_value])

    def apply_deskew(self):
        self.run_imagemagick(["-deskew", self.deskew_value])

    def apply_crop(self):
        self.run_imagemagick(["-trim", "+repage"])

    def run_imagemagick(self, args):
        if not self.processed_image or not self.original_path:
            return

        temp_input = "_temp_input.png"
        temp_output = "_temp_output.png"
        self.processed_image.save(temp_input)

        command = ["convert", temp_input] + args + ["-background", "white", "-flatten", temp_output]
        subprocess.run(command)

        self.processed_image = Image.open(temp_output)
        self.display_image(self.processed_image, self.processed_label)

        os.remove(temp_input)
        os.remove(temp_output)

    def suggest_filename(self, extension):
        if self.original_path and not self.is_dragged:
            base = os.path.splitext(os.path.basename(self.original_path))[0]
        else:
            now = datetime.now().strftime("%Y%m%d%H%M")
            base = f"{now}_document-cleaner"
        return f"{base}.{extension}"

    def save_jpg(self):
        if not self.processed_image:
            return
        default_name = self.suggest_filename("jpg")
        path = filedialog.asksaveasfilename(defaultextension=".jpg", initialfile=default_name)
        if path:
            self.processed_image.save(path, "JPEG")

    def save_pdf(self):
        if not self.processed_image:
            return
        default_name = self.suggest_filename("pdf")
        path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=default_name)
        if path:
            self.processed_image.save(path, "PDF", resolution=150.0)

    def save_pdf_ocr(self):
        if not self.processed_image or not self.ocr_available:
            return
        default_pdf = self.suggest_filename("pdf")
        default_txt = self.suggest_filename("txt")

        path_pdf = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=default_pdf)
        if not path_pdf:
            return

        temp_img = "_ocr_input.png"
        temp_pdf = "_ocr_base.pdf"

        try:
            self.processed_image.save(temp_img)
            subprocess.run(["convert", temp_img, temp_pdf])
            subprocess.run(["ocrmypdf", "--skip-text", "-l", self.ocr_lang, temp_pdf, path_pdf])

            # Extract OCR text
            text_output = path_pdf.replace(".pdf", ".txt") if path_pdf.endswith(".pdf") else path_pdf + ".txt"
            with open(text_output, "w") as f:
                subprocess.run(["tesseract", temp_img, "stdout", "-l", self.ocr_lang], stdout=f)

        finally:
            if os.path.exists(temp_img):
                os.remove(temp_img)
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)

if __name__ == "__main__":
    import tkinterdnd2 as tkdnd
    root = tkdnd.TkinterDnD.Tk()

    initial_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = DocumentCleanerApp(root, initial_file)
    root.mainloop()
