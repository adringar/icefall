import os
import json
import glob

def process_jsonl_files(jsonl_dir, output_base_dir):
    specific_parts = ["validated_reduced_dev-s_test", "dev-s", "test"]
    
    patterns = [
        os.path.join(jsonl_dir, f"basqueP_supervisions_{part}*.jsonl") for part in specific_parts
    ]
    
    jsonl_files = []
    for pattern in patterns:
        jsonl_files.extend(glob.glob(pattern))
    
    print(f"Found {len(jsonl_files)} JSONL files")
    
    for jsonl_file in jsonl_files:
        file_name = os.path.basename(jsonl_file)
        subdir_name = file_name.replace("basqueP_supervisions_", "").replace(".jsonl", "")
        print(f"Processing file: {file_name}")
        print(f"Subdirectory name: {subdir_name}")
        
        with open(jsonl_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    
                    recording_id = data['recording_id']
                    speaker_id = data.get('speaker', 'unknown_speaker')
                    text = data.get('text', '')
                    
                    # Parse the recording_id
                    parts = recording_id.split('_')
                    if len(parts) < 4:
                        print(f"Warning: Unexpected recording_id format in file {file_name}, line {line_num}: {recording_id}")
                        continue
                    
                    session = parts[0]
                    date = parts[1]
                    sequence_number = parts[2]
                    timestamps = '_'.join(parts[3:])
                    
                    # Create directory structure
                    dir_path = os.path.join(output_base_dir, subdir_name, speaker_id, f"{session}_{date}_{sequence_number}")
                    os.makedirs(dir_path, exist_ok=True)
                    
                    # Create and write to transcript file
                    transcript_file = os.path.join(dir_path, f"{speaker_id}-{session}_{date}_{sequence_number}.trans.txt")
                    with open(transcript_file, 'a') as tf:
                        tf.write(f"{speaker_id}-{session}_{date}_{sequence_number}-{timestamps} {text}\n")
                
                except KeyError as e:
                    print(f"KeyError in file {file_name}, line {line_num}: {e}")
                    print(f"Data: {data}")
                except json.JSONDecodeError:
                    print(f"Invalid JSON in file {file_name}, line {line_num}")
                except Exception as e:
                    print(f"Unexpected error in file {file_name}, line {line_num}: {e}")
        
        print(f"Processed {jsonl_file}")
        print()

# Set the paths
jsonl_dir = "/mnt/ahogpu_ldisk2/adriang/icefall_own/egs/basque_parliament_1_gttsehu/ASR/data/manifests"
output_base_dir = "/mnt/ahogpu_ldisk2/adriang/icefall_own/egs/basque_parliament_1_gttsehu/ASR/download/basqueP"

# Run the processing function
process_jsonl_files(jsonl_dir, output_base_dir)
print("Processing complete!")