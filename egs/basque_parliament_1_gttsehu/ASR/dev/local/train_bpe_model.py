#!/usr/bin/env python3

import argparse
import os
from typing import List
from pathlib import Path
import sentencepiece as spm

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_text_files(data_dir: str) -> List[str]:
    """Get all text files from the data directory."""
    text_files = []
    for split in ['train', 'dev', 'test']:
        text_file = os.path.join(data_dir, split, 'text')
        if os.path.exists(text_file):
            text_files.append(text_file)
    return text_files

def train_bpe_model(text_files: List[str], bpe_model: str, vocab_size: int):
    """Train a BPE model using SentencePiece."""
    input_argument = ','.join(text_files)
    
    ensure_dir(bpe_model)

    spm.SentencePieceTrainer.train(
        input=input_argument,
        model_prefix=bpe_model.replace('.model', ''),
        vocab_size=vocab_size,
        character_coverage=1.0,
        model_type='bpe',
        input_sentence_size=10000000,
        shuffle_input_sentence=True,
        normalization_rule_name='nmt_nfkc_cf'
    )

def main():
    parser = argparse.ArgumentParser(description="Train a BPE model.")
    parser.add_argument('--data-dir', type=str, required=True, help='Directory containing the data')
    parser.add_argument('--bpe-model', type=str, required=True, help='Output BPE model file')
    parser.add_argument('--bpe-vocab-size', type=int, default=500, help='BPE vocabulary size') # 

    args = parser.parse_args()

    text_files = get_text_files(args.data_dir)
    if not text_files:
        print("No text files found in the data directory.")
        return

    print(f"Training BPE model with vocab size {args.bpe_vocab_size}")
    train_bpe_model(text_files, args.bpe_model, args.bpe_vocab_size)
    print(f"BPE model saved to {args.bpe_model}")

if __name__ == "__main__":
    main()
