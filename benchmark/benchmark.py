import time
from pathlib import Path

import jiwer
import pandas as pd
from rich.console import Console
from rich.table import Table

from speech2caret.speech_to_text import SpeechToText

# --- Configuration ---
# Add any Hugging Face model names you want to test here
MODELS_TO_BENCHMARK = [
    "openai/whisper-tiny.en",
    "openai/whisper-base.en",
    "openai/whisper-small.en",
]

# Path to your test audio and the correct transcription
AUDIO_FILE_PATH = Path(__file__).parent.parent / "tests/data/jfk.flac"
GROUND_TRUTH_TRANSCRIPTION = "And so my fellow Americans, ask not what your country can do for you, ask what you can do for your country."


def run_benchmark():
    """
    Loads, runs, and times different speech-to-text models,
    then prints a comparison table.
    """
    console = Console()
    console.print(f"🎤 Starting benchmark with audio: [cyan]{AUDIO_FILE_PATH.name}[/cyan]")
    console.print(f"📝 Ground Truth: \"{GROUND_TRUTH_TRANSCRIPTION}\"")

    results = []

    for model_name in MODELS_TO_BENCHMARK:
        console.print(f"\n[bold yellow]Benchmarking: {model_name}[/bold yellow]")

        # 1. Time the model loading
        with console.status("[bold green]Loading model...[/bold green]"):
            start_time = time.perf_counter()
            stt = SpeechToText(model_name=model_name)
            load_time = time.perf_counter() - start_time

        # 2. Time the transcription
        with console.status("[bold green]Transcribing audio...[/bold green]"):
            start_time = time.perf_counter()
            transcription = stt.transcribe(AUDIO_FILE_PATH)
            transcribe_time = time.perf_counter() - start_time

        # 3. Calculate Word Error Rate (WER)
        error_rate = jiwer.wer(GROUND_TRUTH_TRANSCRIPTION, transcription)

        results.append(
            {
                "Model": model_name,
                "Load Time (s)": f"{load_time:.2f}",
                "Transcribe Time (s)": f"{transcribe_time:.2f}",
                "WER (%)": f"{error_rate * 100:.2f}",
                "Transcription": transcription,
            }
        )
        console.print(
            f"✅ [green]Done.[/green] Load: {load_time:.2f}s, Transcribe: {transcribe_time:.2f}s, WER: {error_rate * 100:.2f}%")
        console.print(f"   [dim]Hypothesis: \"{transcription}\"[/dim]")

    # 4. Display results in a table
    console.print("\n\n--- [bold]Benchmark Results[/bold] ---")
    df = pd.DataFrame(results)

    # To display the full transcription text in the table
    pd.set_option('display.max_colwidth', None)
    print(df)


if __name__ == "__main__":
    # For a prettier table output, you can install rich and pandas
    run_benchmark()
