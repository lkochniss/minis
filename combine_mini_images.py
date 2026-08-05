import os
from PIL import Image

def combine_images(input_dir, output_dir):
    # Iterate over subfolders in input_dir
    for folder_name in os.listdir(input_dir):
        folder_path = os.path.join(input_dir, folder_name)
        if os.path.isdir(folder_path):
            image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not image_files:
                continue

            # Open images
            images = [Image.open(os.path.join(folder_path, f)) for f in image_files]

            # Find min height to resize all images to same height
            min_height = min(img.height for img in images)
            
            # Resize all images to min_height
            resized_images = []
            for img in images:
                width = int(img.width * (min_height / img.height))
                resized_images.append(img.resize((width, min_height)))

            # Calculate total width and max height for the final image
            total_width = sum(img.width for img in resized_images)
            
            # Create new image
            new_image = Image.new('RGB', (total_width, min_height))

            # Paste images side-by-side
            x_offset = 0
            for img in resized_images:
                new_image.paste(img, (x_offset, 0))
                x_offset += img.width

            # Save the result
            output_filename = f"{folder_name}.jpg"
            new_image.save(os.path.join(output_dir, output_filename))
            print(f"Created: {output_filename}")

if __name__ == "__main__":
    input_base = "batch_incoming"
    output_base = "incoming"
    combine_images(input_base, output_base)
