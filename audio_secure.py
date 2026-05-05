import wave

DELIMITER = "###"

def encode_audio(input_path, output_path, message, password):
    message = password + ":" + message + DELIMITER

    song = wave.open(input_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    bits = ''.join(format(ord(i), '08b') for i in message)

    for i in range(len(bits)):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(bits[i])

    with wave.open(output_path, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(bytes(frame_bytes))

    song.close()


def decode_audio(input_path, password):
    song = wave.open(input_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    bits = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    chars = [chr(int(''.join(map(str, bits[i:i+8])), 2)) for i in range(0, len(bits), 8)]

    message = ''.join(chars)
    hidden = message.split(DELIMITER)[0]

    if ":" in hidden:
        stored_pass, msg = hidden.split(":", 1)
        if stored_pass == password:
            return msg

    return None