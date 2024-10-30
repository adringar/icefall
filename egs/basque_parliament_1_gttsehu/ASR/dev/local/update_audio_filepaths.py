import os
import glob
import json
import argparse

def update_audio_filepaths_in_place(manifests_dir, new_audio_dir):
    # Ensure the directories are absolute paths
    manifests_dir = os.path.abspath(manifests_dir)
    new_audio_dir = os.path.abspath(new_audio_dir)

    # Get all JSON files in the manifests directory
    json_files = glob.glob(os.path.join(manifests_dir, '*.json'))

    for json_file in json_files:
        # Read all lines and update the audio_filepaths
        updated_lines = []
        with open(json_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                data = json.loads(line.strip())

                # Extract the audio filename from the original audio_filepath
                original_audio_filepath = data['audio_filepath']
                audio_filename = os.path.basename(original_audio_filepath)

                # Construct the new audio_filepath
                new_audio_filepath = os.path.join(new_audio_dir, audio_filename)

                # Update the audio_filepath in the data
                data['audio_filepath'] = new_audio_filepath

                # Add the updated data to the list
                updated_lines.append(json.dumps(data, ensure_ascii=False) + '\n')

        # Overwrite the original JSON file with updated content
        with open(json_file, 'w', encoding='utf-8') as outfile:
            outfile.writelines(updated_lines)

        print(f"Updated {json_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update audio_filepaths in JSON files in place.')
    parser.add_argument('--manifests_dir', type=str, required=True,
                        help='Directory containing the manifest JSON files.')
    parser.add_argument('--new_audio_dir', type=str, required=True,
                        help='New directory where the audio files are located.')

    args = parser.parse_args()
    update_audio_filepaths_in_place(args.manifests_dir, args.new_audio_dir)
