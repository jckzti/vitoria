import json
import os
import requests
import time

def download_flag(iso_code):
    iso_code = iso_code.lower()
    url = f"https://flagcdn.com/w320/{iso_code}.png"
    save_path = os.path.join("assets", "flags", f"{iso_code}.png")
    
    if os.path.exists(save_path):
        return True
        
    print(f"Downloading {iso_code} from {url}...")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"Saved {save_path}")
            return True
        else:
            print(f"Failed to download {iso_code}: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {iso_code}: {e}")
        return False

def main():
    if not os.path.exists(os.path.join("assets", "flags")):
        os.makedirs(os.path.join("assets", "flags"))

    with open('custom.geo.json', encoding='utf-8') as f:
        data = json.load(f)

    for feature in data['features']:
        props = feature['properties']
        name = props.get('name')
        
        # Collect candidates
        candidates = []
        if 'iso_a2' in props and props['iso_a2'] != -99 and props['iso_a2'] != "-99":
            candidates.append(str(props['iso_a2']))
        if 'iso_a2_eh' in props and props['iso_a2_eh'] != -99 and props['iso_a2_eh'] != "-99":
            candidates.append(str(props['iso_a2_eh']))
        if 'wb_a2' in props and props['wb_a2'] != -99 and props['wb_a2'] != "-99":
            candidates.append(str(props['wb_a2']))
            
        # Try to ensure at least one flag exists for this country
        found = False
        for code in candidates:
            code = code.lower()
            if os.path.exists(os.path.join("assets", "flags", f"{code}.png")):
                found = True
                break
        
        if not found and candidates:
            print(f"Flag missing for {name}. Candidates: {candidates}")
            # Try to download for the first valid candidate
            for code in candidates:
                if download_flag(code):
                    found = True
                    break
            
            if not found:
                print(f"Could not find/download flag for {name}")
                
        time.sleep(0.1) # Be nice to the server

if __name__ == "__main__":
    main()
