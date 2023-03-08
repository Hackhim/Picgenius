"""Script to generate mockups"""
import os
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mp

## OLD
# "template_1": {
#      "template_path": "./templates/1.png",
#      "tab_size": (1053, 1403),
#      "position": (473, 297),
#  },

#### Templates 4 Designs
# 1)   Position 1er pixel: U1:(442;177) / U2:(1076;177) / U3:(444;1055) / U4:(1076;1055)
#   Dimensions tableaux : 493x732 px
#
# 2)  Position 1er pixel: U1:(427;185) / U2:(996;185)
#   Dimensions tableaux : 482x688 px
#
# 3)  [Cactus] Position 1er pixel: U1:(525;307)
#   Dimensions tableaux : 1130x1455 px
#
# 4)  [Petit Chat] Position 1er pixel: U1:(370;254) / U2:(1053;250)
#   Dimensions tableaux :   U1: 601x742 px
#           U2: 600x742 px
#


#### Templates 1 Design:
# 6: POS: (439, 252) | SIZE: (1555-439, 1745-252)
# 7: POS: (422, 256) | SIZE: (1576-422, 1750-256)
#


TEMPLATES_1_DESIGN = {
    "templates": [
        {
            "template_path": "./templates-1-design/1-bedroom.png",
            "position": (705, 255),
            "size": (658, 867),
        },
        {
            "template_path": "./templates-1-design/2-cabinet.png",
            "position": (825, 176),
            "size": (868, 1247),
        },
        {
            "template_path": "./templates-1-design/3-desktop.png",
            "position": (462, 268),
            "size": (1189 - 462, 1297 - 268),
        },
        {
            "template_path": "./templates-1-design/4-mac.png",
            "position": (1016, 114),
            "size": (1767 - 1016, 1200 - 114),
        },
        {
            "template_path": "./templates-1-design/5-wood-border.png",
            "position": (643, 293),
            "size": (1592 - 643, 1569 - 293),
        },
        {
            "template_path": "./templates-1-design/6-grey-border.png",
            "position": (439, 252),
            "size": (1555 - 439, 1745 - 252),
        },
        {
            "template_path": "./templates-1-design/7-black-border.png",
            "position": (422, 256),
            "size": (1576 - 422, 1750 - 256),
        },
    ],
}


def generate_mockup(template_conf: dict, design_path: str):
    """Generate mockup"""
    # Open the image and template files
    design = Image.open(design_path)
    template = Image.open(template_conf["template_path"])
    tab_size = template_conf["size"]
    position = template_conf["position"]

    # Paste the resized design onto the template at the specified position
    resized_design = resize_and_crop(design, *tab_size)
    template.paste(resized_design, position)

    return template


def resize_and_crop(image, size_x: int, size_y: int):
    """Resize and crop image."""
    target_ratio = size_x / size_y
    current_ratio = image.width / image.height
    if current_ratio > target_ratio:
        # Image is wider than aspect ratio, crop the sides
        new_width = int(image.height * target_ratio)
        left = (image.width - new_width) // 2
        right = left + new_width
        box = (left, 0, right, image.height)
    else:
        # Image is taller than aspect ratio, crop the top and bottom
        new_height = int(image.width / target_ratio)
        top = (image.height - new_height) // 2
        bottom = top + new_height
        box = (0, top, image.width, bottom)
    cropped_design = image.crop(box)

    # Resize the cropped design to 2/3 of its original size
    resized_design = cropped_design.resize((size_x, size_y))
    return resized_design


def add_text_to_image(image, text):

    margin = 50
    font_path = "./CS_Gordon/CS Gordon Vintage.otf"

    mask = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(mask)
    font = get_font_size(text, image.width - (margin * 2), font_path)

    # Set the text properties
    text_color = (255, 255, 255, 51)  # White color
    text_bbox = draw.textbbox((0, 0), text, font=font)

    # Calculate the text position
    text_position = (
        (image.width - text_bbox[2]) // 2,
        (image.height - text_bbox[3]) // 2,
    )

    draw.text(text_position, text, font=font, fill=text_color)

    combined = Image.alpha_composite(image, mask)
    return combined


def get_font_size(text: str, max_width: int, font_path: str):
    font_size = 1
    font = ImageFont.truetype(font_path, font_size)
    while font.getlength(text) < max_width:
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)
    return font


def generate_all_mockups_for_1_design(design_path: str, mockups_path: str):

    design_filename = design_path.split("/")[-1]
    design_name = os.path.splitext(design_filename)[0]
    print(f" [*] Generating design: {design_name}")

    design_mockups_dir_path = f"{mockups_path}/{design_name}"
    if not os.path.exists(design_mockups_dir_path):
        os.makedirs(design_mockups_dir_path)

    print("\t[*] Generating gif..")
    generate_video(design_path, f"{design_mockups_dir_path}/design_video.mp4")

    for template_conf in TEMPLATES_1_DESIGN["templates"]:
        mockup_filename = template_conf["template_path"].split("/")[-1]
        print(f"\t[*] Generating mockup: {mockup_filename}")
        mockup_path = f"{design_mockups_dir_path}/{mockup_filename}"
        mockup = generate_mockup(template_conf, design_path)
        mockup = add_text_to_image(mockup, "SIMAAKER SHOP")
        mockup.save(mockup_path)


def generate_video(input_path, output_path):

    image = Image.open(input_path)
    image = resize_and_crop(image, 2000, 2000)
    image = add_text_to_image(image.convert("RGBA"), "SIMAAKER SHOP")
    gif_path = f"{os.path.splitext(output_path)[0]}.gif"
    create_zoom_gif(image, gif_path, duration=100, step=1, frames=50)
    convert_gif_to_mp4(gif_path, output_path)


def convert_gif_to_mp4(gif_path, mp4_path):
    clip = mp.VideoFileClip(gif_path, verbose=False)
    clip.write_videofile(mp4_path, verbose=False)
    os.remove(gif_path)


def create_zoom_gif(image, output_gif_path, duration=200, step=1, frames=100):

    zoom_images = []
    for i in range(0, frames, step):
        tl = i
        br = image.width - i

        zoom_region = (tl, tl, br, br)
        zoom_image = image.crop(zoom_region).resize(image.size, resample=Image.LANCZOS)
        zoom_images.append(zoom_image)

    images = zoom_images  # + unzoom_images
    frame_duration = duration // len(images)
    # Save the frames as an animated GIF
    images[0].save(
        output_gif_path,
        save_all=True,
        append_images=images[1:],
        duration=frame_duration,
        loop=0,
    )


def main():

    design_dir_path = "./designs"
    mockup_dir_path = "./mockups"

    for design_filename in os.listdir(design_dir_path):
        design_path = f"{design_dir_path}/{design_filename}"
        generate_all_mockups_for_1_design(design_path, mockup_dir_path)


if __name__ == "__main__":
    main()
