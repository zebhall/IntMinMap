# interactive mineral map viewer

import customtkinter as ctk
from tkinter import filedialog
from CTkColorPicker import AskColor
import os
import re
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pilutil import toimage
from random import randint


__author__ = "Z Hall"
__contact__ = "hzeb@pm.me"
__version__ = "v1.0.1"
__versiondate__ = "2024/08/17"


# Create a 1024x1024x3 array of 8 bit unsigned integers
# data = np.zeros((1024, 1024, 3), dtype=np.uint8)

# data[512, 512] = [254, 0, 0]  # Makes the middle pixel red
# data[512, 513] = [0, 0, 255]  # Makes the next pixel blue

# img = toimage(data)  # Create a PIL image
# img.show()  # View in default viewer


class MinMapApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # initialise non-ui object vars
        self.maptxt_file_path:str = None
        self.header_info:dict = None
        self.minerals_info:dict = None
        self.pixels_info:dict = None
        self.image_pixel_array:np.ndarray = None # pixel data for map image.
        self.image_dimensions:tuple[int, int] = None
        self.pixel_size_um:float = None
        self.color_map:dict[int, tuple[int, int, int]] = {}
        
        # self.geometry("600x900")
        self.title("Interactive Mineral Map Viewer")

        # icons
        self.icon_palette = ctk.CTkImage(
            light_image=Image.open(resource_path("icons/palette-b.png")), dark_image=Image.open(resource_path("icons/palette-w.png")), size=(22, 22)
        )
        self.icon_root_path = resource_path("icons/pss_o.ico")
        self.iconbitmap(default=self.icon_root_path)

        # FILE OPERATIONS FRAME
        self.frame_fileoperations = ctk.CTkFrame(self, height=40)
        self.frame_fileoperations.pack(
            side=ctk.TOP,
            fill="x",
            anchor=ctk.N,
            expand=False,
            padx=8,
            pady=[8,4],
            ipadx=4,
            ipady=4,
        )
        self.button_loadfile = ctk.CTkButton(self.frame_fileoperations, text="Load File", command=self.button_loadfile_click)
        self.button_loadfile.pack(side=ctk.LEFT, padx=8, pady=4)
        self.checkbox_scaleruler = ctk.CTkCheckBox(self.frame_fileoperations, text="Include Scale", onvalue=True, offvalue=False,)
        self.checkbox_scaleruler.pack(side=ctk.RIGHT, padx=8, pady=4)
        self.button_saveimage = ctk.CTkButton(self.frame_fileoperations, text="Save Image", command=self.button_saveimage_click)
        self.button_saveimage.pack(side=ctk.RIGHT, padx=8, pady=4)

        
        # MINERALS FRAME
        self.mineral_rows:list[MineralRow] = []
        self.frame_minerals = ctk.CTkScrollableFrame(self, width=290)
        self.frame_minerals.pack(
            side=ctk.LEFT,
            fill="both",
            expand=True,
            padx=[8,4],
            pady=[4,8],
            ipadx=4,
            ipady=4,
        )


        # MAP DISPLAY FRAME
        self.frame_mapdisplay = ctk.CTkFrame(self, width=900, height=600)
        self.frame_mapdisplay.pack(
            side=ctk.RIGHT,
            fill="both",
            expand=True,
            padx=[4,8],
            pady=[4,8],
            ipadx=4,
            ipady=4,
        )

    # add methods to app
    def button_loadfile_click(self):
        self.maptxt_file_path = ctk.filedialog.askopenfilename(filetypes=[("Map-as-Text Files", "*.txt")], initialdir=os.getcwd())
        print(f"loading file: {self.maptxt_file_path}")
        self.digest_map_file(path=self.maptxt_file_path)

    def button_saveimage_click(self):
        print("saveimage click")
        self.save_image_as(self.image_pil,include_scale_ruler=self.checkbox_scaleruler.get())

    def digest_map_file(self, path: str):
        print("digesting map file...")
        with open(path, mode="r") as f:
            file_data = f.read()
        
        # header
        header_match = re.search(r"<Header>(.*?)</Header>", file_data, re.DOTALL)
        header_content = header_match.group(1).strip() if header_match else ""
        self.header_info = self.parse_header(header_content)
        
        # minerals
        minerals_match = re.search(r"<Minerals>(.*?)</Minerals>", file_data, re.DOTALL)
        minerals_content = minerals_match.group(1).strip() if minerals_match else ""
        self.minerals_info = self.parse_minerals(minerals_content)
        
        # pixel section
        pixels_match = re.search(r"<Pixels>(.*?)</Pixels>", file_data, re.DOTALL)
        pixels_content = pixels_match.group(1).strip() if pixels_match else ""
        self.pixels_info = self.parse_pixels(pixels_content)
        self.image_dimensions = self.get_pixel_dimensions(self.pixels_info)
        
        self.create_mineral_rows(self.minerals_info)
        self.image_dimensions = self.get_pixel_dimensions(self.pixels_info)
        print(f"Map dimensions: {self.image_dimensions}")

        self.reconstruct_and_display_image()


    def reconstruct_and_display_image(self):
        # convert pixel info to array for PIL
        self.image_pixel_array = self.create_pixel_array(self.pixels_info)
        
        # show image
        self.display_image(self.image_pixel_array)

    def parse_header(self, header_content: str) -> dict:
        header_info = {}
        for line in header_content.split("\n"):
            key, value = line.split(":")
            header_info[key.strip()] = value.strip()
        self.pixel_size_um = float(header_info["Pixel size"])
        return header_info

    def parse_minerals(self, minerals_content: str) -> dict:
        minerals_info = {}
        for line in minerals_content.split("\n"):
            name, id = line.split(":")
            minerals_info[name.strip()] = int(id.strip())
        return minerals_info

    def parse_pixels(self, pixels_content: str) -> dict:
        pixels_info = {}
        for line in pixels_content.split("\n"):
            coords, id = line.split(":")
            pixels_info[coords.strip()] = int(id.strip())
        return pixels_info

    def create_mineral_rows(self, minerals_info: dict):
        for mineral_name in minerals_info.keys():
            id = minerals_info[mineral_name]
            initial_colour = (randint(0,255), randint(0,255), randint(0,255))
            self.color_map[minerals_info[mineral_name]] = initial_colour
            self.add_mineral_row(mineral_name, id, initial_colour)
            # Add default colour mapping {id: (rgb colour tuple)}
            # self.color_map[minerals_info[mineral_name]] = (255, 255, 255)  # Default to white


    def add_mineral_row(self, mineral_name: str, id:int, initial_colour:tuple[int, int, int]):
        mineral_row = MineralRow(self, self.frame_minerals, mineral_name, id, initial_colour, self.icon_palette)
        self.mineral_rows.append(mineral_row)

    def get_pixel_dimensions(self, pixels_info: dict) -> tuple[int,int]:
        max_x = 0
        max_y = 0
        for coords in pixels_info.keys():
            x, y = map(int, coords.split(","))
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
        return max_x + 1, max_y + 1
    
    def create_pixel_array(self, pixels_info:dict) -> np.ndarray:
        # get dims
        if self.image_dimensions is None:
            self.image_dimensions = self.get_pixel_dimensions(self.pixels_info)
        height,width = self.image_dimensions

        # init empty array
        pixel_array = np.zeros((width, height, 3), dtype=np.uint8)

        for coords, mineral_id in pixels_info.items():
            x, y = map(int, coords.split(","))
            if mineral_id in self.color_map:
                color = self.color_map[mineral_id]
                pixel_array[y, x] = color
        
        return pixel_array

    def display_image(self, image_data:np.ndarray):
        self.image_pil = toimage(image_data)  # Create a PIL image
        # img.show()  # View in default viewer
        try:
            #if re-displaying, kill old image
            self.label_mapimage.pack_forget()
        except AttributeError:
            pass
        self.label_mapimage = ctk.CTkLabel(self.frame_mapdisplay, text="", image=ctk.CTkImage(light_image=self.image_pil, size=self.image_pil.size))
        self.label_mapimage.pack(expand=True)

    def add_scale_ruler(self, image: Image.Image, micron_per_pixel: float) -> Image.Image:
        # copy of original
        new_image = image.copy()

        width, height = new_image.size
        # scale ruler dim and pos
        ruler_height = 50
        ruler_margin = 10
        ruler_length = 200  # total length in pixels of whole 'ruler'
        micron_length = ruler_length * micron_per_pixel  # Length in microns of the ruler
        
        # Create a new image with extra space at the bottom for the ruler
        result_image = Image.new('RGB', (width, height + ruler_height + ruler_margin), (255, 255, 255))
        result_image.paste(new_image, (0, 0))
        
        # Draw the ruler on the new image
        draw = ImageDraw.Draw(result_image)
        
        # Define the starting and ending points of the ruler
        ruler_start = (ruler_margin, height + ruler_margin)
        ruler_end = (ruler_margin + ruler_length, height + ruler_margin)
        
        # Draw the ruler line
        draw.line([ruler_start, ruler_end], fill='black', width=2)
        
        # Add text label indicating the length in microns
        font = ImageFont.load_default()
        text = f"{micron_length/1000:.1f} mm"
        text_size = draw.textlength(text,font=font)
        text_position = (ruler_start[0] + (ruler_length - text_size) // 2, ruler_start[1] + 5)
        draw.text(text_position, text, fill='black', font=font)
        
        return result_image

    def save_image_as(self, pil_image:Image.Image, include_scale_ruler:bool=True):
        # save as
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialdir=os.getcwd(),
            filetypes=[
                ("PNG files", "*.png"),
                ("Bitmap files", "*.bmp"),
                ("JPEG files", "*.jpg;*.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            if include_scale_ruler:
                # get scale

                pil_image = self.add_scale_ruler(pil_image,self.pixel_size_um)
            # Save the image to the chosen path
            pil_image.save(file_path)

        

class MineralRow():
    def __init__(self, outer_instance:MinMapApp, parent, mineral_name:str, id:int, initial_colour:tuple[int,int,int], icon):
        
        self.mineral_name = mineral_name
        self.mineral_id = id
        self.initial_colour = initial_colour
        self.outer_instance = outer_instance
        # for tkinter color purposes, fg_color for swatch should be defined as rgb_to_hex(self.initial_colour)

        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="x", padx=4, pady=2, ipadx=4, ipady=2)

        self.label = ctk.CTkLabel(self.frame, text=mineral_name, anchor="w")
        self.label.pack(side=ctk.LEFT, padx=6, expand=True, fill="both")

        # self.visibility_var = ctk.BooleanVar(value=True)
        # self.checkbox = ctk.CTkCheckBox(self.frame, variable=self.visibility_var, text=None, width=10)
        # self.checkbox.pack(side=ctk.LEFT, padx=5)

        self.color_button = ctk.CTkButton(self.frame, text="", image=icon, command=self.select_color_clicked, width=30)
        self.color_button.pack(side=ctk.LEFT, padx=5)

        self.color_swatch = ctk.CTkLabel(self.frame, width=70, height=30, fg_color=rgb_to_hex(self.initial_colour), text="", corner_radius=5)
        self.color_swatch.pack(side=ctk.LEFT, padx=5)

    def select_color_clicked(self):
        # get current color to start at
        current = self.color_swatch.cget("fg_color")
        self.pick_color = AskColor(title=f"Choose color for {self.label.cget('text')}", initial_color=current) # open the color picker
        self.color_code = self.pick_color.get() # get the color string
        # print(self.color_code)
        if self.color_code:
            self.color_swatch.configure(fg_color=self.color_code)
            self.outer_instance.color_map[self.mineral_id] = hex_to_rgb(self.color_code)
            self.outer_instance.reconstruct_and_display_image()


def hex_to_rgb(hex:str) -> tuple[int,int,int]:
    #print(type(hex))
    if hex.startswith("#"):
        # strip leading # if needed
        hex=hex.replace("#","")
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: tuple[int,int,int], include_hash:bool=True) -> str:
    if include_hash:
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    else:
        return "{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)



def main():
    app = MinMapApp()
    app.mainloop()


if __name__ == "__main__":
    main()