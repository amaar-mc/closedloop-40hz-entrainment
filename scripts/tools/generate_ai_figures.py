#!/usr/bin/env python3
"""
Generate publication-quality conceptual figures for the research paper
using image-generating models via OpenRouter API.
"""

import os
import json
import base64
import requests
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "results", "figures", "ai_generated")
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(os.path.expanduser("~/.claude/apis.env")) as f:
    for line in f:
        if line.startswith("OPENROUTER_API_KEY="):
            API_KEY = line.strip().split("=", 1)[1]
            break

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/closedloop-40hz-entrainment",
}

# Image generation model
MODEL = "openai/gpt-5-image"

FIGURES = {
    "system_architecture_v1": (
        "Generate a clean, professional scientific pipeline diagram for a neuroscience research paper. "
        "Horizontal left-to-right flow on a white background. "
        "Seven connected stages as rounded rectangles with thin connecting arrows: "
        "Stage 1 'Patient EEG' (blue, small brain wave icon, text: 7 frontal channels, 250 Hz) -> "
        "Stage 2 'Preprocessing' (light blue, text: bandpass 0.5-80 Hz, notch, CAR) -> "
        "Stage 3 'EEGNet' (green, text: 1,457 params, R2=0.287) -> "
        "Stage 4 'Feature Extraction' (green, text: 73 causal features) -> "
        "Stage 5 'Causal TCN' (dark green, text: 31K params, 20s lookback) -> "
        "Stage 6 'Adaptive Controller' (orange, text: z-score +/- 0.5, 5s hysteresis) -> "
        "Stage 7 '40 Hz Audio Stimulation' (orange-red, speaker icon). "
        "A curved dashed feedback arrow from stage 7 back to stage 1 labeled 'Closed-Loop Feedback'. "
        "Modern flat design, no gradients, publication quality, clean vector-art style. "
        "Professional neuroscience journal figure. Wide landscape format."
    ),
    "system_architecture_v2": (
        "Create a publication-quality scientific diagram of a closed-loop brain-computer interface system. "
        "Clean white background, landscape orientation. "
        "Left: silhouette of a human head in profile with an EEG cap showing electrode positions. "
        "Center: a horizontal processing pipeline shown as connected rounded boxes: "
        "'Signal Processing' (bandpass filter), 'EEGNet (PAC Estimator)' (small neural net), "
        "'Feature Engineering (73D)' (matrix grid), 'Causal TCN (5s Forecast)' (dilated conv blocks), "
        "'Adaptive Controller' (decision logic). Use blue for signals, green for ML models, orange for control. "
        "Right: speaker icon emitting 40 Hz sound waves directed at the head. "
        "A large curved arrow completes the feedback loop from output back to the head. "
        "Label 'Closed-Loop 40 Hz Entrainment System' at top. "
        "Minimalist Nature/Science journal style, precise clean lines, no clutter."
    ),
    "brain_pac_concept_v1": (
        "Generate a scientific illustration showing phase-amplitude coupling (PAC) in the brain "
        "for a neuroscience research paper. Two-panel layout on white background. "
        "LEFT PANEL: A translucent human brain viewed from the front with the frontal cortex "
        "region highlighted in soft blue, showing where theta-gamma coupling is measured. "
        "Small dots indicate EEG electrode positions (Fp1, Fp2, F3, Fz, F4, F7, F8). "
        "RIGHT PANEL: Two overlapping neural oscillation waveforms. "
        "A slow theta wave (4-8 Hz) drawn as a large smooth sinusoid in deep navy blue. "
        "Fast gamma oscillations (38-42 Hz) as small rapid waves in gold/amber whose AMPLITUDE "
        "increases at the PEAK of the theta wave and decreases at the TROUGH. "
        "An annotation bracket showing 'Strong PAC = high Modulation Index'. "
        "Clean, precise, publication-quality medical illustration style. "
        "Color palette: navy blue, amber/gold, white. Suitable for Nature Neuroscience."
    ),
    "brain_pac_concept_v2": (
        "Create a professional neuroscience figure illustrating theta-gamma phase-amplitude coupling "
        "for Alzheimer's disease research. White background. "
        "TOP: An elegant top-down view of a human brain with 7 frontal EEG electrode positions "
        "marked as small blue circles on the prefrontal and frontal regions. "
        "BOTTOM: A detailed waveform diagram. A large slow sinusoidal wave (theta, 4-8 Hz) in blue "
        "serves as the carrier. Nested within it, small fast oscillations (gamma, 40 Hz) in orange "
        "are shown with their amplitude envelope clearly following the theta phase: "
        "gamma bursts are LARGER at theta peaks and SMALLER at theta troughs. "
        "Label: 'Modulation Index (MI) = coupling strength'. "
        "Show two states side by side: 'Strong Entrainment (high MI)' and 'Weak Entrainment (low MI)'. "
        "Professional, minimalist, academic journal illustration."
    ),
    "closedloop_vs_fixed_v1": (
        "Generate a two-panel comparison diagram for a research paper on brain stimulation. "
        "White background, landscape format. "
        "Both panels share a wavy line representing brain coupling strength (PAC) that rises and falls. "
        "LEFT PANEL - 'Fixed Schedule (Open-Loop)': "
        "Regular evenly-spaced green/teal bars represent stimulation periods, delivered on a rigid timer. "
        "Red X marks show stimulation during HIGH coupling (wasted - patient doesn't need it). "
        "Red circle marks show LOW coupling periods with NO stimulation (missed opportunity). "
        "Efficiency label: '45% alignment'. "
        "RIGHT PANEL - 'Predictive Closed-Loop (Ours)': "
        "Stimulation bars are concentrated ONLY during low-PAC dips. "
        "Green checkmarks show correct targeting of low-coupling windows. "
        "A small 'TCN predicts 5-10s ahead' annotation with a forward-looking arrow. "
        "Efficiency label: '72% alignment'. "
        "Clean flat design, publication quality, suitable for a journal graphical abstract."
    ),
    "closedloop_vs_fixed_v2": (
        "Create a scientific infographic comparing open-loop vs closed-loop 40 Hz brain stimulation "
        "for an Alzheimer's disease research paper. Clean white background. "
        "PANEL A 'Current Approach': A brain receiving regularly timed sound pulses (fixed 40s ON/20s OFF). "
        "A sine wave beneath shows brain coupling going up and down, but stimulation ignores it. "
        "Many pulses hit during strong coupling (unnecessary). Red highlights for waste. "
        "PANEL B 'Our Approach': Same brain but connected to an AI chip icon (neural network). "
        "The AI monitors the coupling wave and PREDICTS when it will drop. "
        "Stimulation pulses are precisely timed to land during coupling dips. "
        "Green highlights for good targeting. Arrow labeled '5-10s prediction window'. "
        "Results: '72.1% alignment vs 64.5% reactive, 91% of oracle'. "
        "Modern, clean, professional scientific figure style. Teal and coral color scheme."
    ),
    "horizon_inflection_v1": (
        "Generate a clean scientific concept diagram for a research paper illustrating the "
        "'prediction horizon inflection point' at 3 seconds. White background. "
        "X-axis: 'Prediction Horizon (seconds)' from 1 to 10. "
        "Y-axis: 'Prediction Accuracy (R-squared)' from -0.4 to 0.8. "
        "A dashed horizontal line at R2=0 (the 'no skill' boundary). "
        "RED declining curve: 'Baselines (Persistence, Ridge)' starts high at 1s (~0.8), "
        "crosses zero at ~3s, then goes deeply negative by 5-10s (~-0.3). "
        "GREEN stable curve: 'Causal TCN (ours)' starts slightly lower at 1s (~0.7), "
        "but stays POSITIVE at 5-10s (~0.25), maintaining a +0.5 margin over baselines. "
        "A vertical dashed line at 3 seconds labeled 'Inflection Point'. "
        "LEFT zone (1-3s) shaded light gray, labeled 'Simple methods work'. "
        "RIGHT zone (3-10s) shaded light green, labeled 'Only TCN succeeds'. "
        "Publication quality, clear labels, Nature journal style chart."
    ),
}


def generate_image(name, prompt):
    """Generate an image using a chat-based image model on OpenRouter."""
    print(f"\n{'='*50}")
    print(f"Generating: {name}")
    print(f"Prompt: {prompt[:120]}...")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_tokens": 4096,
    }

    try:
        resp = requests.post(CHAT_URL, headers=HEADERS, json=payload, timeout=180)

        if resp.status_code != 200:
            print(f"  ERROR {resp.status_code}: {resp.text[:300]}")
            return False

        data = resp.json()

        # Parse response - image models return content with inline images
        if "choices" not in data or len(data["choices"]) == 0:
            print(f"  ERROR: No choices in response")
            return False

        message = data["choices"][0].get("message", {})
        content = message.get("content", "")

        # Check for different image formats in the response

        # Format 1: Content is a list with image parts (multimodal response)
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    if part.get("type") == "image_url":
                        url = part.get("image_url", {}).get("url", "")
                        if url.startswith("data:image"):
                            # Base64 data URL
                            b64_data = url.split(",", 1)[1]
                            img_bytes = base64.b64decode(b64_data)
                            out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
                            with open(out_path, "wb") as f:
                                f.write(img_bytes)
                            print(f"  SUCCESS (data URL): {out_path} ({len(img_bytes):,} bytes)")
                            return True
                        elif url.startswith("http"):
                            img_resp = requests.get(url, timeout=60)
                            out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
                            with open(out_path, "wb") as f:
                                f.write(img_resp.content)
                            print(f"  SUCCESS (URL): {out_path} ({len(img_resp.content):,} bytes)")
                            return True

        # Format 2: Content is a string with embedded base64
        if isinstance(content, str):
            # Check for base64 image data
            import re
            b64_match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', content)
            if b64_match:
                img_bytes = base64.b64decode(b64_match.group(1))
                out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                print(f"  SUCCESS (inline b64): {out_path} ({len(img_bytes):,} bytes)")
                return True

            # Check for image URL
            url_match = re.search(r'(https?://[^\s"\']+\.(?:png|jpg|jpeg|webp))', content)
            if url_match:
                url = url_match.group(1)
                img_resp = requests.get(url, timeout=60)
                if img_resp.status_code == 200:
                    out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
                    with open(out_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"  SUCCESS (URL): {out_path} ({len(img_resp.content):,} bytes)")
                    return True

            # Check for OpenAI-style image response in the raw JSON
            if "url" in str(data):
                # Dig through the full response
                raw = json.dumps(data)
                url_match = re.search(r'"url"\s*:\s*"(https?://[^"]+)"', raw)
                if url_match:
                    url = url_match.group(1)
                    try:
                        img_resp = requests.get(url, timeout=60)
                        if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                            out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
                            with open(out_path, "wb") as f:
                                f.write(img_resp.content)
                            print(f"  SUCCESS (deep URL): {out_path} ({len(img_resp.content):,} bytes)")
                            return True
                    except:
                        pass

            # If content is text only, the model couldn't generate an image
            if len(content) < 500:
                print(f"  Response (no image): {content[:300]}")
            else:
                print(f"  Response is text ({len(content)} chars), no image data found.")

        print(f"  FAILED: No image data in response")
        return False

    except requests.exceptions.Timeout:
        print(f"  ERROR: Request timed out (180s)")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    print("=" * 60)
    print("AI Figure Generation for Research Paper")
    print(f"Model: {MODEL}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Figures: {len(FIGURES)}")
    print("=" * 60)

    results = {}
    for name, prompt in FIGURES.items():
        success = generate_image(name, prompt)
        results[name] = success
        time.sleep(3)  # Rate limit

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, success in results.items():
        status = "OK" if success else "FAILED"
        print(f"  [{status}] {name}")

    succeeded = sum(1 for v in results.values() if v)
    print(f"\n{succeeded}/{len(results)} generated. Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
