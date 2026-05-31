#!/usr/bin/env python3
"""
Generate a single publication-quality figure using an image-generating model
via OpenRouter API.

Usage:
    python scripts/tools/generate_image.py "Your prompt here" --output path/to/output.png
"""

import os
import sys
import json
import base64
import re
import argparse
import requests

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_api_key():
    """Load OpenRouter API key from ~/.claude/apis.env"""
    env_path = os.path.expanduser("~/.claude/apis.env")
    if not os.path.exists(env_path):
        print(f"ERROR: API key file not found at {env_path}")
        sys.exit(1)
    with open(env_path) as f:
        for line in f:
            if line.startswith("OPENROUTER_API_KEY="):
                return line.strip().split("=", 1)[1]
    print("ERROR: OPENROUTER_API_KEY not found in apis.env")
    sys.exit(1)


def generate_image(prompt, output_path, model="openai/gpt-5-image"):
    """Generate an image from a text prompt and save to output_path."""
    api_key = load_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/closedloop-40hz-entrainment",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_tokens": 4096,
    }

    print(f"Model: {model}")
    print(f"Output: {output_path}")
    print(f"Prompt: {prompt[:150]}...")
    print("Generating image...")

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=180,
        )

        if resp.status_code != 200:
            print(f"ERROR {resp.status_code}: {resp.text[:500]}")
            sys.exit(1)

        data = resp.json()

        if "choices" not in data or len(data["choices"]) == 0:
            print(f"ERROR: No choices in response: {json.dumps(data)[:500]}")
            sys.exit(1)

        message = data["choices"][0].get("message", {})
        content = message.get("content", "")

        # Debug: show response structure
        print(f"  Content type: {type(content).__name__}")
        if isinstance(content, list):
            print(f"  Content parts: {len(content)}")
            for i, part in enumerate(content):
                if isinstance(part, dict):
                    print(f"    Part {i}: type={part.get('type')}, keys={list(part.keys())}")
                else:
                    print(f"    Part {i}: {type(part).__name__}, len={len(str(part))}")
        elif isinstance(content, str):
            print(f"  Content length: {len(content)}")
            if len(content) < 200:
                print(f"  Content: {content}")

        # Also check for OpenAI-native image response format (output field)
        output_parts = data["choices"][0].get("message", {}).get("output", None)
        if output_parts is None:
            # Sometimes the image data is at the top level of the response
            output_parts = data.get("output", None)
        if output_parts:
            print(f"  Found 'output' field: type={type(output_parts).__name__}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Format 0: Images in a top-level 'images' array on the message
        # (OpenAI gpt-image models via OpenRouter return this format)
        images = message.get("images", [])
        if images:
            print(f"  Found 'images' field with {len(images)} image(s)")
            for img_part in images:
                if isinstance(img_part, dict):
                    img_url = ""
                    if img_part.get("type") == "image_url":
                        img_url = img_part.get("image_url", {}).get("url", "")
                    elif "url" in img_part:
                        img_url = img_part["url"]
                    if img_url.startswith("data:image"):
                        b64_data = img_url.split(",", 1)[1]
                        img_bytes = base64.b64decode(b64_data)
                        with open(output_path, "wb") as f:
                            f.write(img_bytes)
                        print(f"SUCCESS: {output_path} ({len(img_bytes):,} bytes)")
                        return True
                    elif img_url.startswith("http"):
                        img_resp = requests.get(img_url, timeout=60)
                        with open(output_path, "wb") as f:
                            f.write(img_resp.content)
                        print(f"SUCCESS (URL): {output_path} ({len(img_resp.content):,} bytes)")
                        return True

        # Format 1: Content is a list with image parts (multimodal response)
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    ptype = part.get("type", "")
                    if ptype == "image_url":
                        url = part.get("image_url", {}).get("url", "")
                        if url.startswith("data:image"):
                            b64_data = url.split(",", 1)[1]
                            img_bytes = base64.b64decode(b64_data)
                            with open(output_path, "wb") as f:
                                f.write(img_bytes)
                            print(f"SUCCESS (data URL): {output_path} ({len(img_bytes):,} bytes)")
                            return True
                        elif url.startswith("http"):
                            img_resp = requests.get(url, timeout=60)
                            with open(output_path, "wb") as f:
                                f.write(img_resp.content)
                            print(f"SUCCESS (URL): {output_path} ({len(img_resp.content):,} bytes)")
                            return True
                    # OpenAI native image output format
                    elif ptype == "image" or "b64_json" in part or "b64" in part:
                        b64_data = part.get("b64_json") or part.get("b64") or part.get("data", "")
                        if b64_data:
                            img_bytes = base64.b64decode(b64_data)
                            with open(output_path, "wb") as f:
                                f.write(img_bytes)
                            print(f"SUCCESS (b64_json): {output_path} ({len(img_bytes):,} bytes)")
                            return True
                        img_url = part.get("url", "")
                        if img_url.startswith("http"):
                            img_resp = requests.get(img_url, timeout=60)
                            with open(output_path, "wb") as f:
                                f.write(img_resp.content)
                            print(f"SUCCESS (image URL): {output_path} ({len(img_resp.content):,} bytes)")
                            return True

        # Format 2: Content is a string with embedded base64
        if isinstance(content, str):
            b64_match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', content)
            if b64_match:
                img_bytes = base64.b64decode(b64_match.group(1))
                with open(output_path, "wb") as f:
                    f.write(img_bytes)
                print(f"SUCCESS (inline b64): {output_path} ({len(img_bytes):,} bytes)")
                return True

            url_match = re.search(r'(https?://[^\s"\']+\.(?:png|jpg|jpeg|webp))', content)
            if url_match:
                url = url_match.group(1)
                img_resp = requests.get(url, timeout=60)
                if img_resp.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"SUCCESS (URL): {output_path} ({len(img_resp.content):,} bytes)")
                    return True

            # Check for OpenAI-style image response in raw JSON
            if "url" in str(data):
                raw = json.dumps(data)
                url_match = re.search(r'"url"\s*:\s*"(https?://[^"]+)"', raw)
                if url_match:
                    url = url_match.group(1)
                    try:
                        img_resp = requests.get(url, timeout=60)
                        if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                            with open(output_path, "wb") as f:
                                f.write(img_resp.content)
                            print(f"SUCCESS (deep URL): {output_path} ({len(img_resp.content):,} bytes)")
                            return True
                    except Exception:
                        pass

            if len(content) < 500:
                print(f"Response (no image): {content[:300]}")
            else:
                print(f"Response is text ({len(content)} chars), no image data found.")

        # Last resort: search entire JSON response for any base64 image data
        raw_json = json.dumps(data)
        # Look for large b64 blocks that could be images
        b64_blocks = re.findall(r'[A-Za-z0-9+/]{1000,}={0,2}', raw_json)
        if b64_blocks:
            print(f"  Found {len(b64_blocks)} potential base64 block(s), trying largest...")
            b64_blocks.sort(key=len, reverse=True)
            for block in b64_blocks[:3]:
                try:
                    img_bytes = base64.b64decode(block)
                    # Check for PNG/JPEG magic bytes
                    if img_bytes[:4] in (b'\x89PNG', b'\xff\xd8\xff\xe0', b'\xff\xd8\xff\xe1'):
                        with open(output_path, "wb") as f:
                            f.write(img_bytes)
                        print(f"SUCCESS (raw b64): {output_path} ({len(img_bytes):,} bytes)")
                        return True
                except Exception:
                    continue

        # Debug: dump truncated raw response
        print(f"  Raw response (first 1000 chars): {raw_json[:1000]}")

        print("FAILED: No image data in response")
        return False

    except requests.exceptions.Timeout:
        print("ERROR: Request timed out (180s)")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a single image from a text prompt using OpenRouter API"
    )
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output file path (e.g., results/figures/ai_generated/my_figure.png)",
    )
    parser.add_argument(
        "--model", "-m",
        default="openai/gpt-5-image",
        help="Model to use (default: openai/gpt-5-image)",
    )

    args = parser.parse_args()
    success = generate_image(args.prompt, args.output, args.model)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
