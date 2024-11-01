#!/usr/bin/env bash

# fix segmentation fault reported in https://github.com/k2-fsa/icefall/issues/674
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

set -eou pipefail

nj=1
# run step 0 to step 5 by default
stage=-1
stop_stage=5

# Note: This script just prepare the minimal requirements that needed by a
# transducer training with bpe units.
#
# If you want to use ngram or nnlm, please continue running prepare_lm.sh after
# you succeed running this script.
#
# This script also contains the steps to generate phone based units, but they
# will not run automatically, you can generate the phone based units by
# bash prepare.sh --stage -1 --stop-stage -1
# bash prepare.sh --stage 6 --stop-stage 6


# We assume dl_dir (download dir) contains the following
# directories and files. If not, they will be downloaded
# by this script automatically.
#
#  - $dl_dir/basque_parliament
#      You can find BOOKS.TXT, dev_original.json, dev-s.json, etc, inside it.
#
#  - $dl_dir/musan
#      This directory contains the following directories downloaded from
#       http://www.openslr.org/17/
#
#     - music
#     - noise
#     - speech
#
# lm directory is not necessary for transducer training with bpe units, but it
# is needed by phone based modeling, you can download it by running
# bash prepare.sh --stage -1 --stop-stage -1
# then you can see the following files in the directory.
#  - $dl_dir/lm
#      This directory contains the following files downloaded from
#       http://www.openslr.org/resources/11
#
#        - 3-gram.pruned.1e-7.arpa.gz
#        - 3-gram.pruned.1e-7.arpa
#        - 4-gram.arpa.gz
#        - 4-gram.arpa
#        - librispeech-vocab.txt
#        - librispeech-lexicon.txt
#        - librispeech-lm-norm.txt.gz

dl_dir=$PWD/download

. shared/parse_options.sh || exit 1

# vocab size for sentence piece models.
# It will generate data/lang_bpe_xxx,
# data/lang_bpe_yyy if the array contains xxx, yyy
vocab_sizes=(
  5000
  2000
  1000
  500
  256 # Best for basque setup !
  150 # For short bash (prepare.sh) testing 
)

# ---------------------------------------------------------------------------- 

# All files generated by this script are saved in "data".
# You can safely remove "data" and rerun this script to regenerate it.
mkdir -p data

log() {
  # This function is from espnet
  local fname=${BASH_SOURCE[1]##*/}
  echo -e "$(date '+%Y-%m-%d %H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}

log "Running prepare.sh"
log " "

log "dl_dir: $dl_dir"
log " "

# ---------------------------------------------------------------------------- 

if [ $stage -le -1 ] && [ $stop_stage -ge -1 ]; then

  log "Stage -1: Downloading LM..."
  mkdir -p $dl_dir/lm

  if [ ! -e $dl_dir/lm/.done ]; then # Check if the LM is already downloaded
    ./local/download_lm.py --out-dir=$dl_dir/lm
    touch $dl_dir/lm/.done
  else # If the LM is already downloaded
    log "Stage -1: Librispeech LM is already downloaded"
  fi

  log " "

fi

# ---------------------------------------------------------------------------- 

if [ $stage -le 0 ] && [ $stop_stage -ge 0 ]; then

  log "Stage 0: Downloading data..."
  log "Stage 0: basque_parliament dataset already downloaded"
  
  if [ ! -d $dl_dir/musan ]; then # Check if musan is already downloaded
    lhotse download musan $dl_dir
  else # If musan is already downloaded
    log "Stage 0: musan dataset already downloaded"
  fi

  log " "

fi

# ---------------------------------------------------------------------------- 

if [ $stage -le 1 ] && [ $stop_stage -ge 1 ]; then

  log "Stage 1: Preparing Basque Parliament manifests..."

  if [ ! -e data/manifests/.basque_parliament.done ]; then # Check if basque_parliament is already prepared
    touch data/manifests/.basque_parliament.done
  else # If basque_parliament is already prepared
    log "Stage 1: basque_parliament manifests already prepared"
  fi

  log " "

fi

# ---------------------------------------------------------------------------- 

if [ $stage -le 2 ] && [ $stop_stage -ge 2 ]; then

  log "Stage 2: Preparing musan manifest..."

  if [ ! -e data/manifests/.musan.done ]; then
    lhotse prepare musan $dl_dir/musan data/manifests
    touch data/manifests/.musan.done
  else # If musan is already prepared
    log "Stage 2: musan manifests already prepared"
  fi

  log " "

fi

# ---------------------------------------------------------------------------- 

if [ $stage -le 3 ] && [ $stop_stage -ge 3 ]; then

  log "Stage 3: Computing fbank for basque_parliament..."

  mkdir -p data/fbank

  if [ ! -e data/fbank/.basque_parliament.done ]; then # Check if fbank for basque_parliament is already computed
    python3 ./local/compute_fbank_basqueP.py
    touch data/fbank/.basque_parliament.done
  else # If fbank for basque_parliament is already computed
    log "Stage 3: fbank for basque_parliament already computed"
  fi

  if [ ! -f data/fbank/validated_reduced_dev-s_test.jsonl.gz ]; then
    cat <(gunzip -c data/fbank/test.jsonl.gz) \
      <(gunzip -c data/fbank/dev-s.jsonl.gz) \
      <(gunzip -c data/fbank/validated_reduced_dev-s_test.jsonl.gz)
  fi
  
  if [ ! -e data/fbank/.basqueP-validated.done ]; then
    log "Validating data/fbank for basque parliament"
    parts=(
      "validated_reduced_dev-s_test"
      "test_original"
      "dev-s"
      # "dev",
      # "test_decoded_processed",
      # "test_decoded",
      # "test_original",
      # "test",
      # "train_clean_decoded_processed_reduced",
      # "train_clean_decoded_processed",
      # "train_clean_decoded",
      # "train_clean",
      # "validated_original",
      # "validated_reduced_dev-s_test",
      # "validated",
      # "validation_decoded_processed",
      # "validation_decoded",
      # "validation",
      # "short_test_decoded"
      # "short_test"
      # "short_train_clean_decoded"
      # "short_validation_decoded"
    )
    for part in ${parts[@]}; do
      python3 ./local/validate_manifest.py \
        data/fbank/basqueP_cuts_${part}.jsonl.gz
    done
    touch data/fbank/.basqueP-validated.done
  fi

  log " "

fi

# ---------------------------------------------------------------------------- 

if [ $stage -le 4 ] && [ $stop_stage -ge 4 ]; then
  log "Stage 4: Compute fbank for musan"
  mkdir -p data/fbank
  if [ ! -e data/fbank/.musan.done ]; then
    ./local/compute_fbank_musan.py
    touch data/fbank/.musan.done
  else
    log "Stage 4: fbank for musan already computed" 
  fi
  log " "
fi

# ---------------------------------------------------------------------------- 

if [ $stage -le 5 ] && [ $stop_stage -ge 5 ]; then
  log "Stage 5: Prepare BPE based lang"

  for vocab_size in ${vocab_sizes[@]}; do
    lang_dir=data/lang_bpe_${vocab_size}
    mkdir -p $lang_dir

    if [ ! -f $lang_dir/transcript_words.txt ]; then
      log "Stage 5: Generate data for BPE training"
      files=$(
        find "$dl_dir/basqueP/validated_reduced_dev-s_test" -name "*.trans.txt"
      )
      for f in ${files[@]}; do
        cat $f | cut -d " " -f 2-
      done > $lang_dir/transcript_words.txt
    fi

    if [ ! -f $lang_dir/bpe.model ]; then
      log "Stage 5: Training BPE model"
      ./local/train_bpe_model.py \
        --lang-dir $lang_dir \
        --vocab-size $vocab_size \
        --transcript $lang_dir/transcript_words.txt
    else
      log "Stage 5: BPE model already trained"
    fi
  done

  log " "
fi

# ---------------------------------------------------------------------------- 

if [ $stage -le 6 ] && [ $stop_stage -ge 6 ]; then
  log "Stage 6: Prepare phone based lang"
  lang_dir=data/lang_phone
  mkdir -p $lang_dir

  if [ ! -f $dl_dir/lm/librispeech-lexicon.txt ]; then
    log "Stage 6: No lexicon file in $dl_dir/lm, please run :"
    log "Stage 6: prepare.sh --stage -1 --stop-stage -1"
    exit -1
  fi

  if [ ! -f $lang_dir/lexicon.txt ]; then
    (echo '!SIL SIL'; echo '<SPOKEN_NOISE> SPN'; echo '<UNK> SPN'; ) |
      cat - $dl_dir/lm/librispeech-lexicon.txt |
      sort | uniq > $lang_dir/lexicon.txt
  fi

  if [ ! -f $lang_dir/L_disambig.pt ]; then
    ./local/prepare_lang.py --lang-dir $lang_dir
  fi

  if [ ! -f $lang_dir/L.fst ]; then
    log "Stage 6: Converting L.pt to L.fst"
    ./shared/convert-k2-to-openfst.py \
      --olabels aux_labels \
      $lang_dir/L.pt \
      $lang_dir/L.fst
  fi

  if [ ! -f $lang_dir/L_disambig.fst ]; then
    log "Stage 6: Converting L_disambig.pt to L_disambig.fst"
    ./shared/convert-k2-to-openfst.py \
      --olabels aux_labels \
      $lang_dir/L_disambig.pt \
      $lang_dir/L_disambig.fst
  fi
fi
