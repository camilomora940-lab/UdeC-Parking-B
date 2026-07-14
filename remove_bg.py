from PIL import Image

def remove_black_background(img_path, out_path, tolerance=40):
    img = Image.open(img_path).convert("RGBA")
    data = img.getdata()
    
    new_data = []
    for item in data:
        # Check if pixel is dark (near black)
        # We can also check if it's grayscale to avoid deleting dark colored pixels
        if item[0] < tolerance and item[1] < tolerance and item[2] < tolerance:
            # Calculate alpha based on how dark it is (anti-aliasing smooth edge)
            # if max(item[:3]) == 0: alpha = 0
            # but simple threshold is fine for now
            new_data.append((item[0], item[1], item[2], 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(out_path, "PNG")

remove_black_background('assets/logo.png', 'assets/logo_transparent.png')
print("Image processed")
