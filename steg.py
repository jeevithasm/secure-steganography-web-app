from PIL import Image

def text_to_binary(text):
    return ''.join(format(ord(i), '08b') for i in text)

def binary_to_text(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

# -------------------------------
# HIDE MESSAGE
# -------------------------------
def hide_message(image_path, message):
    img = Image.open(image_path)
    binary_msg = text_to_binary(message + "###END###")

    data_index = 0
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            pixel = list(pixels[x, y])

            for i in range(3):
                if data_index < len(binary_msg):
                    pixel[i] = pixel[i] & ~1 | int(binary_msg[data_index])
                    data_index += 1

            pixels[x, y] = tuple(pixel)

            if data_index >= len(binary_msg):
                output_path = "static/output.png"
                img.save(output_path)
                return output_path

# -------------------------------
# EXTRACT MESSAGE
# -------------------------------
def extract_message(image_path):
    img = Image.open(image_path)
    binary_data = ""
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            pixel = pixels[x, y]
            for i in range(3):
                binary_data += str(pixel[i] & 1)

    text = binary_to_text(binary_data)

    if "###END###" in text:
        return text.split("###END###")[0]
    return None

# -------------------------------
# DETECT MESSAGE
# -------------------------------
def detect_message(image_path):
    img = Image.open(image_path)
    binary_data = ""
    pixels = img.load()

    for y in range(img.height):
        for x in range(img.width):
            pixel = pixels[x, y]
            for i in range(3):
                binary_data += str(pixel[i] & 1)

    text = binary_to_text(binary_data)

    return "###END###" in text