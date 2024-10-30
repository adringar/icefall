import json
import os
import jsonlines

def process_json(json_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    text_file = os.path.join(output_dir, 'text')
    wav_scp_file = os.path.join(output_dir, 'wav.scp')
    utt2spk_file = os.path.join(output_dir, 'utt2spk')

    with open(text_file, 'w') as text_f, open(wav_scp_file, 'w') as wav_scp_f, open(utt2spk_file, 'w') as utt2spk_f:
        with jsonlines.open(json_file) as reader:
            for item in reader:
                utt_id = f"{item['client_id']}_{os.path.basename(item['audio_filepath']).split('.')[0]}"
                text_f.write(f"{utt_id} {item['text']}\n")
                wav_scp_f.write(f"{utt_id} {item['audio_filepath']}\n")
                utt2spk_f.write(f"{utt_id} {item['client_id']}\n")

def main():

    base_dir = '/mnt/ahogpu_ldisk2/adriang/icefall_own/egs/basque_parliament_1_gttsehu/ASR/dataset/basque_parliament_1_gttsehu/eu/manifests'
    output_base = 'data'

    train_file = os.path.join(base_dir, 'short_train_clean_decoded.json')
    val_file = os.path.join(base_dir, 'short_validation_decoded.json')
    # test_file = os.path.join(base_dir, 'test_decoded.json')
    test_file = os.path.join(base_dir, 'short_test.json')

    print(f"Train file exists: {os.path.exists(train_file)}")
    print(f"Train file size: {os.path.getsize(train_file)} bytes")
    print()

    print(f"Validation file exists: {os.path.exists(val_file)}")
    print(f"Validation file size: {os.path.getsize(val_file)} bytes")
    print()

    print(f"Test file exists: {os.path.exists(test_file)}")
    print(f"Test file size: {os.path.getsize(test_file)} bytes")
    print()

    os.makedirs(output_base, exist_ok=True)

    # Process train data
    process_json(os.path.join(base_dir, 'train_clean_decoded.json'), os.path.join(output_base, 'train'))

    # Process dev data
    process_json(os.path.join(base_dir, 'validation_decoded.json'), os.path.join(output_base, 'dev'))

    # Process test data
    process_json(os.path.join(base_dir, 'test_decoded.json'), os.path.join(output_base, 'test'))

    # Create lexicon.txt
    os.makedirs(os.path.join(output_base, 'lang_char'), exist_ok=True)
    vocab = [' ', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
             'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'á', 'é', 'í', 'ñ', 'ó', 'ú', 'ü']

    with open(os.path.join(output_base, 'lang_char', 'lexicon.txt'), 'w') as f:
        for char in vocab:
            if char != ' ':
                f.write(f"{char} {char}\n")

if __name__ == "__main__":
    main()
