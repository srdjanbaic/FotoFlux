from PIL import Image, ImageDraw
from rembg import new_session, remove

print("Kreiranje test slike...", flush=True)

image = Image.new("RGB", (320, 320), "white")
draw = ImageDraw.Draw(image)
draw.ellipse((80, 40, 240, 280), fill="red")

print("Ucitavanje U2-Net AI modela...", flush=True)
session = new_session("u2net")

print("Pokretanje AI segmentacije...", flush=True)

mask = remove(
    image,
    session=session,
    only_mask=True,
    post_process_mask=True
)

print("Rezultat:", type(mask).__name__)
print("Dimenzije:", mask.size)

assert mask.size == image.size

print("U2NET AI TEST USPESAN!")
