import os
import json
import base64
from openai import OpenAI
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from mathruler.grader import extract_boxed_content, grade_answer
from tqdm import tqdm  # Import tqdm for progress bar
from concurrent.futures import ThreadPoolExecutor  # Import for parallel execution
import re
# Load environment variables from .env file
load_dotenv()

# Constants
IMAGE_DIR = "/fs-computility/mabasic/zhouheng/RoboViki-R/data/images"
META_DATA_PATH = "/fs-computility/mabasic/zhouheng/RoboViki-R/data/meta_data.json"
SYSTEM_PROMPT_COT = (
    r'The image depicts an indoor scene. Analyze how many robots are present.' 
    r'You FIRST think about the reasoning process as an internal monologue and then provide the final answer. '
    r'The reasoning process MUST BE enclosed within <think> </think> tags. The final answer MUST BE put in \boxed{}.'
)
SYSTEM_PROMPT = (
    r'The image depicts an indoor scene. How many robots are present.' 
    r'The final answer MUST BE put in \boxed{}.'
)

# Initialize OpenAI client
client = OpenAI(api_key="EMPTY",base_url="http://0.0.0.0:8000/v1")

def encode_image(image_path):
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def load_metadata():
    """Load metadata from JSON file"""
    with open(META_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_gpt4o_response(image_path):
    """Get GPT-4o response for an image"""
    base64_image = encode_image(image_path)
    
    try:
        response = client.chat.completions.create(
            model="/fs-computility/mabasic/zhouheng/Qwen2.5-VL-7B-Instruct",
            messages=[{
                "role": "system", 
                "content": SYSTEM_PROMPT
            }, {
                "role": "user", 
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting response for {image_path}: {e}")
        return None

def process_image(img_file, metadata, results):
    """Process each image and compute its result"""
    img_path = os.path.join(IMAGE_DIR, img_file)
    img_id = os.path.splitext(img_file)[0]  # Remove file extension to get ID
         
    ground_truth = metadata[int(img_id)]['robot_num']
    
    # Get GPT-4o response
    response = get_gpt4o_response(img_path)

    if response:
        # Extract number from response
        predicted_count = extract_boxed_content(response)
        if predicted_count==None:
            match = re.search(r"Final Answer: (\d+)", response)
            if match:
                predicted_count = match.group(1)

        result = {
            "image_id": img_id,
            "ground_truth": ground_truth,
            "model_response": response,
            "extracted_count": predicted_count,
            "is_correct": predicted_count == str(ground_truth) if predicted_count is not None else False
        }
        
        results.append(result)
        
        # Print accuracy after each image processing
        correct_count = sum(1 for r in results if r["is_correct"])
        total_count = len(results)
        accuracy = correct_count / total_count if total_count > 0 else 0
        print(f"Image: {img_id}, Ground Truth: {ground_truth}, Predicted: {predicted_count}")
        print(f"Accuracy: {accuracy:.2%}")
        print("-------------------")

def main():
    # Load metadata
    metadata = load_metadata()
    
    # Get all image files
    image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    results = []
    
    # Use ThreadPoolExecutor to process images in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Wrap the image processing task with tqdm for a progress bar
        for _ in tqdm(executor.map(lambda img_file: process_image(img_file, metadata, results), image_files), 
                      total=len(image_files), desc="Processing images", unit="image"):
            pass
        
    # Calculate final statistics
    correct_count = sum(1 for r in results if r["is_correct"])
    total_count = len(results)
    accuracy = correct_count / total_count if total_count > 0 else 0
    
    print(f"\nResults Summary:")
    print(f"Total images processed: {total_count}")
    print(f"Correct predictions: {correct_count}")
    print(f"Final Accuracy: {accuracy:.2%}")
    
    # Save results to file
    output_dir = Path("/fs-computility/mabasic/zhouheng/RoboViki-R/inference/results")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    with open(output_dir / f"qwen7b_results_{timestamp}.json", 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total": total_count,
                "correct": correct_count,
                "accuracy": accuracy
            },
            "results": results
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
