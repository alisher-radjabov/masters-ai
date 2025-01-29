import openai
import os

def generate_images(prompt, num_images=9):
    """Generates images using OpenAI's DALL·E API."""
    openai.api_key = "YOUR_OPENAI_API_KEY" 
    
    images = []
    for i in range(num_images):
        print(f"Generating image {i+1}...")
        response = openai.Image.create(
            prompt=f"{prompt} - variation {i+1}", 
            n=1,
            size="1024x1024"
        )
        
        image_url = response["data"][0]["url"]
        images.append(image_url)
        save_image(image_url, f"image_{i+1}.png")
        
    print("Image generation complete!")
    return images

def save_image(url, filename):
    """Downloads and saves an image from a URL."""
    import requests
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Saved: {filename}")
    else:
        print(f"Failed to download {filename}")

if __name__ == "__main__":
    user_prompt = input("Enter your prompt for image generation: ")
    images = generate_images(user_prompt)
    print("Generated images:")
    for img in images:
        print(img)
