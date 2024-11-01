import os
import glob
import json
import gzip
import shutil

def remove_gz_files(manifests_dir):
    # Remove .jsonl.gz files except those starting with 'musan'
    gz_files = glob.glob(os.path.join(manifests_dir, '*.jsonl.gz'))
    for gz_file in gz_files:
        basename = os.path.basename(gz_file)
        if not basename.startswith('musan'):
            os.remove(gz_file)
            print(f"Removed: {gz_file}")

def compress_jsonl_files(manifests_dir):
    # Compress .jsonl files to .jsonl.gz
    jsonl_files = glob.glob(os.path.join(manifests_dir, '*.jsonl'))
    for jsonl_file in jsonl_files:
        basename = os.path.basename(jsonl_file)
        if not basename.startswith('musan'):
            gz_filename = jsonl_file + '.gz'
            with open(jsonl_file, 'rb') as f_in:
                with gzip.open(gz_filename, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"Compressed: {jsonl_file} -> {gz_filename}")

def update_audio_filepaths_in_place():

    manifests_dir = "/mnt/ahogpu_ldisk2/adriang/icefall/egs/basque_parliament_1_gttsehu/ASR/data/manifests"
    new_audio_base = "/mnt/ahogpu_ldisk2/adriang/icefall/egs/basque_parliament_1_gttsehu/ASR/dev/dataset/basque_parliament_1_gttsehu/eu"

    # First remove existing .gz files
    remove_gz_files(manifests_dir)

    # Get all JSONL files in the manifests directory
    jsonl_files = glob.glob(os.path.join(manifests_dir, '*.jsonl'))
    
    for jsonl_file in jsonl_files:
        if os.path.basename(jsonl_file).startswith('musan'):
            continue
            
        updated_lines = []
        with open(jsonl_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                if not line.strip():  # Skip empty lines
                    continue
                    
                data = json.loads(line.strip())
                
                # Check if this is a file with audio sources
                if 'sources' in data:
                    original_source = data['sources'][0]['source']
                    audio_filename = os.path.basename(original_source)
                    
                    # Determine folder name based on file extension
                    ext = os.path.splitext(audio_filename)[1]
                    folder_name = "wavs" if ext == ".wav" else "clips"
                    
                    # Construct the new source path
                    new_source = os.path.join(new_audio_base, folder_name, audio_filename)
                    
                    # Update the source in the data
                    data['sources'][0]['source'] = new_source
                
                # Add the updated (or unchanged) data to the list
                updated_lines.append(json.dumps(data, ensure_ascii=False) + '\n')
        
        # Overwrite the original JSONL file with updated content
        with open(jsonl_file, 'w', encoding='utf-8') as outfile:
            outfile.writelines(updated_lines)
        print(f"Updated {jsonl_file}")
    
    # Compress the updated files
    compress_jsonl_files(manifests_dir)

if __name__ == '__main__':
    update_audio_filepaths_in_place()