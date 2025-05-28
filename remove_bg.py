from rembg import remove
from PIL import Image

# Pfade definieren
input_path = 'test_2.jpg'  # Ersetze durch den Pfad zu deinem Bild
output_path = 'output.png'  # Ersetze durch den gewünschten Ausgabepfad

# Bild öffnen
input_image = Image.open(input_path)

# Hintergrund entfernen
output_image = remove(input_image)

# Optional: Neutralen Hintergrund hinzufügen (z. B. weiß)
background = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
final_image = Image.alpha_composite(background, output_image)

# Bild speichern
final_image.save(output_path)
