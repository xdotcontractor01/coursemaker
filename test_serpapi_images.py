"""
Test Script for SerpAPI Image Extraction
Tests whether SerpAPI can fetch and download images successfully
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# ==================== CONFIGURATION ====================
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')

if not SERPAPI_KEY:
    print("ERROR: SERPAPI_KEY not found in environment")
    print("Please set it in your .env file: SERPAPI_KEY='your-key-here'")
    exit(1)

# Create temp directory for test images
TEMP_DIR = Path('./temp_serpapi_test')
TEMP_DIR.mkdir(exist_ok=True)

print("="*80)
print("SERPAPI IMAGE EXTRACTION TEST")
print("="*80)
print(f"API Key: {SERPAPI_KEY[:10]}...{SERPAPI_KEY[-4:]}")
print(f"Output directory: {TEMP_DIR.absolute()}")
print("\n")

# ==================== HELPER FUNCTIONS ====================

def search_images_serpapi(query, num_images=5):
    """
    Search for images using SerpAPI Google Images
    
    Args:
        query: Search query string
        num_images: Number of images to fetch (default: 5)
    
    Returns:
        List of image URLs
    """
    print(f"[INFO] Searching for: '{query}'")
    print(f"[INFO] Requesting {num_images} images...")
    
    try:
        # SerpAPI endpoint for Google Images
        url = "https://serpapi.com/search"
        
        params = {
            'engine': 'google_images',
            'q': query,
            'api_key': SERPAPI_KEY,
            'num': num_images,
            'ijn': 0  # Page number (0 = first page)
        }
        
        print(f"[INFO] Making API request to SerpAPI...")
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] API request failed with status code: {response.status_code}")
            print(f"[ERROR] Response: {response.text[:500]}")
            return []
        
        data = response.json()
        
        # Check for errors in response
        if 'error' in data:
            print(f"[ERROR] SerpAPI returned error: {data['error']}")
            return []
        
        # Extract image URLs from results
        images_results = data.get('images_results', [])
        
        if not images_results:
            print(f"[WARNING] No images found in response")
            print(f"[DEBUG] Response keys: {list(data.keys())}")
            return []
        
        print(f"[SUCCESS] Found {len(images_results)} image results")
        
        # Extract image URLs (try both 'original' and 'thumbnail')
        image_urls = []
        for i, img in enumerate(images_results[:num_images]):
            # Prefer original, fallback to thumbnail
            url = img.get('original') or img.get('thumbnail')
            if url:
                image_urls.append(url)
                title = img.get('title', 'No title')
                print(f"  [{i+1}] {title[:60]}...")
                print(f"      URL: {url[:80]}...")
        
        return image_urls
        
    except requests.exceptions.Timeout:
        print(f"[ERROR] Request timed out after 30 seconds")
        return []
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return []


def download_image(url, output_path, timeout=15):
    """
    Download an image from URL to output_path
    
    Args:
        url: Image URL
        output_path: Path to save image
        timeout: Request timeout in seconds
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"[INFO] Downloading: {url[:80]}...")
        
        # Set a user agent to avoid blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        
        if response.status_code != 200:
            print(f"[ERROR] Download failed with status code: {response.status_code}")
            return False
        
        # Save image
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Verify file was created and has content
        if not output_path.exists() or output_path.stat().st_size == 0:
            print(f"[ERROR] Downloaded file is empty or missing")
            return False
        
        size_kb = output_path.stat().st_size / 1024
        print(f"[SUCCESS] Downloaded: {output_path.name} ({size_kb:.2f} KB)")
        return True
        
    except requests.exceptions.Timeout:
        print(f"[ERROR] Download timed out after {timeout} seconds")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Download failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error during download: {e}")
        return False


def test_search_and_download(query, num_images=5):
    """
    Test complete workflow: search and download images
    
    Args:
        query: Search query
        num_images: Number of images to download
    
    Returns:
        List of successfully downloaded file paths
    """
    print("\n" + "-"*80)
    print(f"TEST: '{query}'")
    print("-"*80)
    
    # Search for images
    image_urls = search_images_serpapi(query, num_images=num_images)
    
    if not image_urls:
        print(f"[FAILED] No images found for query: {query}")
        return []
    
    print(f"\n[INFO] Attempting to download {len(image_urls)} images...")
    time.sleep(1)  # Brief pause between API calls
    
    # Download each image
    downloaded_files = []
    for i, url in enumerate(image_urls):
        # Determine file extension from URL
        ext = '.jpg'  # Default
        if '.png' in url.lower():
            ext = '.png'
        elif '.jpeg' in url.lower():
            ext = '.jpeg'
        elif '.webp' in url.lower():
            ext = '.webp'
        
        # Create filename
        safe_query = "".join(c if c.isalnum() else "_" for c in query)
        filename = f"{safe_query}_{i+1}{ext}"
        output_path = TEMP_DIR / filename
        
        # Download
        if download_image(url, output_path):
            downloaded_files.append(output_path)
        else:
            print(f"[WARNING] Skipping image {i+1}")
        
        # Small delay between downloads
        time.sleep(0.5)
    
    print(f"\n[RESULT] Successfully downloaded {len(downloaded_files)}/{len(image_urls)} images")
    return downloaded_files


# ==================== RUN TESTS ====================

def main():
    """Run image extraction tests"""
    
    all_downloaded = []
    
    # Test 1: Bridge construction images
    print("\n" + "="*80)
    print("TEST 1: Bridge Construction")
    print("="*80)
    files = test_search_and_download("bridge construction beams", num_images=3)
    all_downloaded.extend(files)
    
    # Test 2: Structural steel images
    print("\n" + "="*80)
    print("TEST 2: Structural Steel")
    print("="*80)
    files = test_search_and_download("steel beam welding construction", num_images=3)
    all_downloaded.extend(files)
    
    # Test 3: Technical diagram
    print("\n" + "="*80)
    print("TEST 3: Technical Diagrams")
    print("="*80)
    files = test_search_and_download("bridge bearing technical diagram", num_images=3)
    all_downloaded.extend(files)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total images downloaded: {len(all_downloaded)}")
    print(f"Output directory: {TEMP_DIR.absolute()}")
    print("\nDownloaded files:")
    
    total_size = 0
    for file in all_downloaded:
        size = file.stat().st_size
        total_size += size
        print(f"  - {file.name} ({size/1024:.2f} KB)")
    
    print(f"\nTotal size: {total_size/1024:.2f} KB")
    
    if len(all_downloaded) > 0:
        print("\n[SUCCESS] SerpAPI image extraction is working!")
        print(f"\nTo view images, open: {TEMP_DIR.absolute()}")
        
        # Try to open folder (Windows)
        try:
            import subprocess
            subprocess.run(['explorer', str(TEMP_DIR.absolute())], check=False)
            print("[INFO] Opening folder in Windows Explorer...")
        except:
            pass
        
        return 0
    else:
        print("\n[FAILED] No images were downloaded")
        print("\nPossible issues:")
        print("1. Invalid SERPAPI_KEY - Check your .env file")
        print("2. API quota exceeded - Check your SerpAPI dashboard")
        print("3. Network connectivity issues")
        print("4. Image URLs are inaccessible")
        print("\nTo get a valid API key:")
        print("1. Go to https://serpapi.com/")
        print("2. Sign up for a free account")
        print("3. Get your API key from https://serpapi.com/manage-api-key")
        print("4. Add it to your .env file: SERPAPI_KEY='your-key-here'")
        return 1


if __name__ == "__main__":
    exit(main())

