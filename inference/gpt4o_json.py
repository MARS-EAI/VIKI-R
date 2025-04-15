import os
import json
import base64
from openai import OpenAI
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from mathruler.grader import extract_boxed_content, grade_answer
import argparse
from tqdm import tqdm  # Import tqdm for progress bar
from concurrent.futures import ThreadPoolExecutor  # Import for parallel execution

# Load environment variables from .env file
load_dotenv()

# Constants
IMAGE_DIR = "/fs-computility/mabasic/zhouheng/RoboViki-R/data/images"
META_DATA_PATH = "/fs-computility/mabasic/zhouheng/RoboViki-R/data/meta_data.json"
SYSTEM_PROMPT_COT = (
    r'The image depicts an indoor scene. Analyze how many robots are present.' 
    r'You FIRST think about the reasoning process as an internal monologue and then provide the final answer. '
    r'The reasoning process MUST BE enclosed within <think> </think> tags. The final answer MUST BE put in \boxed{}. just a number'
)
SYSTEM_PROMPT = (
    r'The image depicts an indoor scene. How many robots are present.' 
    r'The final answer MUST BE put in \boxed{}. just a number'
)

# Initialize OpenAI client
client = OpenAI()

def encode_image(image_path):
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def load_metadata():
    """Load metadata from JSON file"""
    with open(META_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_gpt4o_response(image_path, system_prompt, model):
    """Get model response for an image"""
    base64_image = encode_image(image_path)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "system", 
                "content": system_prompt
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
    
def process_new_format_data(data, metadata, system_prompt, model):
    """Process new format data and calculate results"""
    img_file = data["images"][0]  # Get image path
    img_id = os.path.splitext(os.path.basename(img_file))[0]  # ID without extension
    
    ground_truth = metadata[int(img_id)]['robot_num']
    
    # Extract user question and assistant answer
    user_message = data["messages"][0]["content"]  # User question
    assistant_answer = data["messages"][1]["content"]  # Assistant answer
    
    # Get GPT-4o response
    response = get_gpt4o_response(img_file, system_prompt, model)

    if response:
        # Extract number from response
        predicted_count = extract_boxed_content(response)
        
        result = {
            "image_id": img_id,
            "ground_truth": ground_truth,
            "user_message": user_message,
            "assistant_answer": assistant_answer,
            "gpt4o_response": response,
            "extracted_count": predicted_count,
            "is_correct": predicted_count == str(ground_truth) if predicted_count is not None else False
        }
        
        return result

def main():
    # Load metadata
    metadata = load_metadata()
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Run robot counting inference with GPT models')
    parser.add_argument('--cot', action='store_true', help='Use Chain of Thought reasoning')
    parser.add_argument('--model', type=str, default='gpt-4o', help='Model to use (e.g., gpt-4o, gpt-4-vision-preview)')
    args = parser.parse_args()
    
    # Set system prompt based on COT flag
    system_prompt = SYSTEM_PROMPT_COT if args.cot else SYSTEM_PROMPT
    
    # Load dataset (assuming data file is in JSON format)
    with open('data/viki-count-test.json', 'r') as f:
        dataset = json.load(f)
    
    results = []
    
    # Extract image files
    image_files = [data["images"][0] for data in dataset]

    # Create a ThreadPoolExecutor to process images in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Wrap the image processing task with tqdm for a progress bar
        for result in tqdm(executor.map(lambda data: process_new_format_data(data, metadata, system_prompt, args.model), dataset), 
                           total=len(dataset), desc="Processing images", unit="image"):
            if result:
                results.append(result)

    # Calculate final statistics and save results
    correct_count = sum(1 for r in results if r["is_correct"])
    total_count = len(results)
    accuracy = correct_count / total_count if total_count > 0 else 0
    
    print(f"\nResults Summary:")
    print(f"Total images processed: {total_count}")
    print(f"Correct predictions: {correct_count}")
    print(f"Final Accuracy: {accuracy:.2%}")
    
    # Save results to a file
    output_dir = Path("/fs-computility/mabasic/zhouheng/RoboViki-R/inference/results")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    with open(output_dir / f"{args.model}_{args.cot}_results_{timestamp}.json", 'w', encoding='utf-8') as f:
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
