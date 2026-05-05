import cv2

# ================= ENCODE =================
def encode_video(input_path, output_path, message, password):

    secret = "###START###" + password + "||" + message + "###END###"

    with open(input_path, "rb") as f:
        video_data = f.read()

    with open(output_path, "wb") as f:
        f.write(video_data)
        f.write(secret.encode())

    print("✅ Encoding done")


# ================= DECODE =================
def decode_video(video_path, password):

    with open(video_path, "rb") as f:
        f.seek(-2000, 2)
        tail = f.read()

    decoded = tail.decode(errors="ignore")

    if "###START###" in decoded and "###END###" in decoded:
        secret = decoded.split("###START###")[1].split("###END###")[0]

        stored_pass, message = secret.split("||")

        if stored_pass == password:
            return message

    return None