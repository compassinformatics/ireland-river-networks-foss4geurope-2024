"""
https://stackoverflow.com/questions/73235958/merging-images-in-python-pil-to-produce-animated-gifs
https://www.libvips.org/install.html
https://github.com/libvips/build-win64-mxe/releases/tag/v8.15.2
https://github.com/libvips/build-win64-mxe/releases/download/v8.15.2/vips-dev-w64-web-8.15.2.zip

C:\VirtualEnvs\misc\Scripts\activate.ps1
pip install pyvips
pip install imageio

$env:PATH="D:\Tools\vips-dev-w64-web-8.15.2\vips-dev-8.15\bin;" + $env:PATH

vips.exe copy ./images/epa-networks2.png ./images/x.png

cd D:\GitHub\ireland-river-networks-foss4geurope-2024
python scripts/transition.py

"""

import pyvips
import imageio.v3 as iio
import os


def create_gif(input_folder, output_gif, fps, loop=0):
    """Create a GIF from a series of PNG images."""
    images = []
    for file_name in sorted(os.listdir(input_folder)):
        if file_name.endswith(".png"):
            file_path = os.path.join(input_folder, file_name)
            images.append(iio.imread(file_path))

    # Save the images as a GIF
    iio.imwrite(output_gif, images, fps=fps, loop=loop)  # 0 = indefinitely
    print(f"Saved GIF: {output_gif}")


def blend_images(image1, image2, alpha):
    """Blend two images with a given alpha."""
    return (image1 * (1 - alpha) + image2 * alpha).cast("uchar")


def ensure_rgb(image):
    """Ensure the image has 3 bands (RGB)."""
    if image.bands == 1:
        # Convert grayscale to RGB by duplicating the single band
        image = image.bandjoin([image, image])
    elif image.bands == 2:
        # Handle 2-band images by adding a third band
        image = image.bandjoin([image[1]])
    elif image.bands > 3:
        # Reduce to 3 bands if there are more
        image = image[:3]
    elif image.bands < 3:
        # Convert to RGB
        image = image.colourspace("srgb")
    return image


def create_transition(image1_path, image2_path, num_steps, output_prefix):
    """Create a transition from one image to another."""
    # Load the images
    image1 = pyvips.Image.new_from_file(image1_path)
    # don't use access='sequential' or you will get a pngload: out of order read at line 701 error
    image2 = pyvips.Image.new_from_file(image2_path)

    # Ensure images are the same size
    if image1.width != image2.width or image1.height != image2.height:
        raise ValueError("Images must have the same dimensions")

    # Ensure images have the same format and 3 bands
    image1 = ensure_rgb(image1)
    image2 = ensure_rgb(image2)

    print(f"Image1 bands: {image1.bands}, Image2 bands: {image2.bands}")

    # Generate intermediate images
    for i in range(num_steps):
        alpha = i / (num_steps - 1)
        blended_image = blend_images(image1, image2, alpha)

        # Ensure the blended image is in a suitable format for saving
        blended_image = blended_image.copy()

        output_path = f"{output_prefix}_{i:03d}.png"
        blended_image.write_to_file(output_path)
        print(f"Saved {output_path}")


def network_comparison():
    image1_path = "./images/epa-networks.png"
    image2_path = "./images/prime2-networks.png"
    num_steps = 10
    output_prefix = "./images/networks/frame"

    create_transition(image1_path, image2_path, num_steps, output_prefix)

    # Example usage
    input_folder = "./images/networks/"
    output_gif = "./images/transition.gif"
    fps = 3  # frames per second

    create_gif(input_folder, output_gif, fps)


def landscape():
    image1_path = "./images/landscape.png"
    image2_path = "./images/prime2-landscape.png"
    num_steps = 15
    output_prefix = "./images/landscape/frame"

    create_transition(image1_path, image2_path, num_steps, output_prefix)

    # Example usage
    input_folder = "./images/landscape/"
    output_gif = "./images/landscape.gif"
    fps = 5

    create_gif(input_folder, output_gif, fps, loop=1)


landscape()