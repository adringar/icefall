# Enviroments

In this folder already set up enviroments for CUDA can be seen.

- Name: icefall_env{CUDA version}.yml

## How can to set it up?

```bash
conda env create -f {name_of_environment}.yml
```

If the above does not work...

## Manual set up for CUDA=12.1

```bash
conda create --name icefall_env121 python=3.9
```

```bash
conda activate icefall_env121
```

```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

```bash
pip install -U k2==1.24.4.dev20241030+cuda12.1.torch2.5.1 -f https://k2-fsa.github.io/k2/cuda.html
```

```bash
pip install git+https://github.com/lhotse-speech/lhotse
```

```bash
cd ..
```

```bash
pip install -r requirements.txt
```

