from openai import OpenAI

import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

base64_image = encode_image("test_2.jpg")



client = OpenAI()

prompt = "Erstelle ein fotorealistisches Bild des Kleidungsstücks aus dem Referenzbild, isoliert auf weißem Hintergrund."

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        }
    ],
    tools=[{"type": "image_generation"}],
)

# Token-Verbrauch anzeigen
if hasattr(response, 'usage'):
    print(f"\n--- Token-Verbrauch ---")
    print(f"Input Tokens: {response.usage.prompt_tokens}")
    print(f"Output Tokens: {response.usage.completion_tokens}")
    print(f"Gesamt Tokens: {response.usage.total_tokens}")
    print("----------------------\n")
else:
    print("Token-Informationen nicht verfügbar.")

# Extrahiere das generierte Bild
image_generation_calls = [
    output for output in response.output if output.type == "image_generation_call"
]

if image_generation_calls:
    image_base64 = image_generation_calls[0].result
    with open("freigestelltes_kleidungsstück.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
    print("Das Bild wurde erfolgreich gespeichert als 'freigestelltes_kleidungsstück.png'.")
else:
    print("Keine Bildgenerierung im Response gefunden.")
