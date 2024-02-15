import torch
import yaml
import argparse
from transformers import pipeline
from datasets import load_dataset
import time


def load_config(config_file):
    try:
        with open(config_file, "r") as stream:
            config = yaml.safe_load(stream)
        return config
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing config file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Read configuration from transcribe_config YAML file"
    )
    parser.add_argument("config_file", help="Path to YAML config file")

    args = parser.parse_args()
    config_file = args.config_file
    config = load_config(config_file)

    if config:
        model_size = config["model"]["size"]
        model_device = config["model"]["device"]
        model_chunk_length = int(config["model"]["chunk_length"])
        model_batch_size = int(config["model"]["batch_size"])
        audio_path = config["audio"]["path"]
        save_loc = config["transcript"]["save_loc"]

        print("Model Size:", model_size)
        print("Model Device:", model_device)
        print("Chunk Length:", model_chunk_length)
        print("Batch Size", model_batch_size)
        print("Audio Path:", audio_path)
        print("---------------")

    model_names = {
        "tiny": "openai/whisper-tiny.en",
        "base": "openai/whisper-base.en",
        "small": "openai/whisper-small.en",
        "medium": "openai/whisper-medium.en",
        "large": "openai/whisper-large",
        "large_v2": "openai/whisper-large-v2",
    }

    model = model_names[model_size]

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        chunk_length_s=model_chunk_length,
        device=model_device,
    )
    start_time = time.time()

    transcript = pipe(audio_path, batch_size=model_batch_size, return_timestamps=True)[
        "chunks"
    ]

    end_time = time.time()
    total_time = end_time - start_time
    print("Generation Complete. Time to Generate:", str(total_time))
    print("Saving Transcript to", save_loc)
    with open(save_loc, "w") as f:
        for chunk in transcript:
            f.write("%s\n" % chunk)
    print("Save Complete")


if __name__ == "__main__":
    main()
