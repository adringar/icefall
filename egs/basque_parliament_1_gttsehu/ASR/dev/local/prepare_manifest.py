import os
import glob
import json
import soundfile as sf  # You may need to install this package
from tqdm import tqdm   # You may need to install this package
import argparse

def process_files(manifests_dir):
    # Get all JSON files starting with 'basqueP' in the manifests directory
    json_files = glob.glob(os.path.join(manifests_dir, 'basqueP*.json'))

    all_files = os.listdir(manifests_dir)
    print(f"All files in the directory:\n{all_files}\n")

    print(f"Found JSON files {json_files}\n")

    # Use tqdm to show progress over JSON files
    for json_file in tqdm(json_files, desc='Processing JSON files'):
        # Extract base filename without extension
        base_filename = os.path.basename(json_file)
        filename_without_ext = os.path.splitext(base_filename)[0]

        # Prepare output filenames
        supervisions_filename = os.path.join(
            manifests_dir, filename_without_ext.replace('basqueP', 'basqueP_supervisions') + '.jsonl'
        )
        recordings_filename = os.path.join(
            manifests_dir, filename_without_ext.replace('basqueP', 'basqueP_recordings') + '.jsonl'
        )

        # Open output files
        with open(supervisions_filename, 'w', encoding='utf-8') as supervisions_file, \
             open(recordings_filename, 'w', encoding='utf-8') as recordings_file:

            # Keep track of recordings to avoid duplicates
            recordings_set = set()

            # Read the input JSON file line by line
            with open(json_file, 'r', encoding='utf-8') as infile:
                # Optionally, get the total number of lines for tqdm
                num_lines = sum(1 for _ in open(json_file, 'r', encoding='utf-8'))
                infile.seek(0)  # Reset file pointer to the beginning

                # Use tqdm to show progress over lines in the JSON file
                for line in tqdm(infile, desc=f'Processing lines in {base_filename}', total=num_lines):
                    data = json.loads(line.strip())

                    audio_filepath = data['audio_filepath']
                    text = data['text']
                    client_id = data['client_id']
                    duration = data['duration']

                    # Extract the filename without extension to use as 'id'
                    audio_filename = os.path.basename(audio_filepath)
                    audio_id = os.path.splitext(audio_filename)[0]

                    # Prepare the supervision entry
                    supervision_entry = {
                        'id': audio_id,
                        'recording_id': audio_id,
                        'start': 0.0,
                        'duration': duration,
                        'channel': 0,
                        'text': text,
                        'language': 'eu',
                        'speaker': client_id
                    }

                    # Write the supervision entry
                    supervisions_file.write(json.dumps(supervision_entry, ensure_ascii=False) + '\n')

                    # Prepare the recording entry only if we haven't processed this recording before
                    if audio_id not in recordings_set:
                        try:
                            # Read audio file to get sampling_rate and num_samples
                            with sf.SoundFile(audio_filepath) as audio_file:
                                sampling_rate = audio_file.samplerate
                                num_samples = len(audio_file)
                        except Exception as e:
                            print(f"Error reading {audio_filepath}: {e}")
                            continue

                        recording_entry = {
                            'id': audio_id,
                            'sources': [
                                {
                                    'type': 'file',
                                    'channels': [0],
                                    'source': audio_filepath
                                }
                            ],
                            'sampling_rate': sampling_rate,
                            'num_samples': num_samples,
                            'duration': duration,
                            'channel_ids': [0]
                        }

                        # Write the recording entry
                        recordings_file.write(json.dumps(recording_entry, ensure_ascii=False) + '\n')
                        recordings_set.add(audio_id)

        print(f"Processed {json_file}. Generated {supervisions_filename} and {recordings_filename}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process JSON files to generate supervisions and recordings.')
    parser.add_argument('--manifests_dir', type=str, required=True,
                        help='Directory containing the manifest JSON files.')

    args = parser.parse_args()
    print(f"Processing files in {args.manifests_dir}\n")

    process_files(args.manifests_dir)
