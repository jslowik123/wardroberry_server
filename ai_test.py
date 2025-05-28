from openai import OpenAI
from dotenv import load_dotenv
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

base64_image = encode_image("test_2.jpg")
load_dotenv()
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
    tools=[
        {
            "type": "image_generation",
            "quality": "high",  # Hypothetischer Parameter
             # Hypothetischer Parameter
        }
    ],
)

# Token-Verbrauch anzeigen
if hasattr(response, 'usage'):
    usage = response.usage
    print(f"\n--- Token-Verbrauch ---")
    print(f"Input Tokens: {usage.input_tokens}")
    print(f"Output Tokens: {usage.output_tokens}")
    print(f"Total Tokens: {usage.total_tokens}")
    
    # Zusätzliche Details falls verfügbar
    if hasattr(usage, 'input_tokens_details'):
        print(f"Cached Tokens: {usage.input_tokens_details.cached_tokens}")
    
    if hasattr(usage, 'output_tokens_details'):
        print(f"Reasoning Tokens: {usage.output_tokens_details.reasoning_tokens}")
    
    print("----------------------\n")
else:
    print("Token-Informationen nicht verfügbar.")

# Extrahiere das generierte Bild
image_generation_calls = [
    output for output in response.output if output.type == "image_generation_call"
]

if image_generation_calls:
    image_base64 = image_generation_calls[0].result
    with open("ergebnis.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
    print("Das Bild wurde erfolgreich gespeichert als 'ergebnis.png'.")
else:
    print("Keine Bildgenerierung im Response gefunden.")
