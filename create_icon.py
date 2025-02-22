from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a new image with a transparent background
    size = (256, 256)
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a circle background
    circle_color = (13, 71, 161, 255)  # Dark blue
    draw.ellipse([20, 20, size[0]-20, size[1]-20], fill=circle_color)
    
    # Draw the "SC" text
    text_color = (255, 255, 255, 255)  # White
    text = "SC"
    
    # Use a default font if custom font not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 120)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw the text
    draw.text(text_position, text, font=font, fill=text_color)
    
    # Save in different sizes
    sizes = [(256, 256), (128, 128), (64, 64), (32, 32)]
    icon_dir = "/usr/share/icons/solacecrypt"
    
    # Create directory if it doesn't exist
    os.makedirs(icon_dir, exist_ok=True)
    
    for s in sizes:
        resized = image.resize(s, Image.Resampling.LANCZOS)
        resized.save(f"{icon_dir}/solacecrypt_{s[0]}.png")
    
    # Save main icon
    image.save(f"{icon_dir}/icon.png")

if __name__ == "__main__":
    create_icon() 