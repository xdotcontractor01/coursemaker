"""
Step 5: Download Images
Downloads images from SerpAPI based on suggestions
Validates each image to ensure it's not corrupted
"""

import json
import time
import requests
from shared import *

def validate_image(filepath):
    """Validate that an image file is not corrupted"""
    try:
        from PIL import Image
        with Image.open(filepath) as img:
            img.verify()  # Verify it's a valid image
        # Re-open to check it can be read (verify() doesn't catch all issues)
        with Image.open(filepath) as img:
            img.load()  # Actually load the image data
        return True
    except Exception as e:
        print_error(f"Image validation failed: {e}")
        return False

def main():
    """Download images using SerpAPI"""
    print_step(5, "Download Images")
    
    try:
        # Read image suggestions
        suggestions_file = TEST_DIR / 'images.json'
        if not suggestions_file.exists():
            print_error("Images suggestions file not found. Run step_04 first.")
            return 1
        
        suggestions = json.loads(suggestions_file.read_text())
        
        if not suggestions:
            print_info("No image suggestions, skipping download")
            # Create empty downloaded.json
            downloaded_file = TEST_DIR / 'downloaded_images.json'
            downloaded_file.write_text('{}')
            return 0
        
        if not SERPAPI_KEY:
            print_error("SERPAPI_KEY not configured")
            print_info("Skipping image downloads")
            downloaded_file = TEST_DIR / 'downloaded_images.json'
            downloaded_file.write_text('{}')
            return 0
        
        print_info(f"Processing {len(suggestions)} image suggestions")
        
        # Create images directory
        images_dir = TEST_DIR / 'images'
        images_dir.mkdir(exist_ok=True)
        
        downloaded = {}
        
        for i, sugg in enumerate(suggestions):
            slide_no = sugg.get('slide_no')
            query = sugg.get('query', '')
            layout = sugg.get('layout', 'background_only')
            
            print_info(f"Downloading image for slide {slide_no}: '{query}'")
            
            try:
                # Search SerpAPI
                serpapi_url = "https://serpapi.com/search"
                params = {
                    'engine': 'google_images',
                    'q': query,
                    'api_key': SERPAPI_KEY,
                    'num': 2  # Get 2 results as backup
                }
                
                response = requests.get(serpapi_url, params=params, timeout=30)
                if response.status_code != 200:
                    print_error(f"SerpAPI request failed: {response.status_code}")
                    continue
                
                data = response.json()
                images_results = data.get('images_results', [])
                
                if not images_results:
                    print_error(f"No images found for query: {query}")
                    continue
                
                # Try to download first result
                for img_result in images_results[:2]:  # Try first 2
                    img_url = img_result.get('original') or img_result.get('thumbnail')
                    if not img_url:
                        continue
                    
                    # Download image
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        img_response = requests.get(img_url, headers=headers, timeout=15, stream=True)
                        
                        if img_response.status_code == 200:
                            # Save image
                            ext = '.jpg'
                            if '.png' in img_url.lower():
                                ext = '.png'
                            
                            filename = f"slide_{slide_no}_image{ext}"
                            filepath = images_dir / filename
                            
                            with open(filepath, 'wb') as f:
                                for chunk in img_response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            
                            if filepath.exists() and filepath.stat().st_size > 0:
                                # Validate the image is not corrupted
                                if validate_image(filepath):
                                    downloaded[slide_no] = {
                                        'path': str(filepath),
                                        'layout': layout,
                                        'query': query
                                    }
                                    size_kb = filepath.stat().st_size / 1024
                                    print_success(f"Downloaded {filename} ({size_kb:.2f} KB) - validated OK")
                                    break  # Successfully downloaded and validated
                                else:
                                    print_error(f"Downloaded image is corrupted, trying next result...")
                                    filepath.unlink()  # Delete corrupted file
                                    continue
                        
                    except Exception as e:
                        print_error(f"Failed to download image: {e}")
                        continue
                
                time.sleep(1)  # Be respectful to API
                
            except Exception as e:
                print_error(f"Error processing slide {slide_no}: {e}")
                continue
        
        # Save downloaded images metadata
        downloaded_file = TEST_DIR / 'downloaded_images.json'
        downloaded_file.write_text(json.dumps(downloaded, indent=2))
        print_info(f"Downloaded metadata saved to: {downloaded_file}")
        
        print_success(f"Downloaded {len(downloaded)} images successfully")
        return 0
        
    except Exception as e:
        print_error(f"Failed to download images: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

