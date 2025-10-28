"""
Download Hebrew LLM Models
===========================
Script to download and prepare Hebrew models for Zero Agent
Based on research from hebrew_llm_research.md
"""

import os
import subprocess
import sys

HEBREW_MODELS = {
    "dictalm": {
        "hf_repo": "dicta-il/dictalm2.0",
        "name": "DictaLM 2.0",
        "size": "7B",
        "description": "State-of-the-art Hebrew LLM, 96%+ accuracy"
    },
    "hebrew-mistral": {
        "hf_repo": "yam-peleg/Hebrew-Mistral-7B-v0.1",
        "name": "Hebrew-Mistral-7B",
        "size": "7B",
        "description": "Mistral fine-tuned for Hebrew"
    },
    "zion": {
        "hf_repo": "Sic ariusSicariiStuff/Zion_Alpha",
        "name": "Zion Alpha",
        "size": "7B",
        "description": "World record SNLI 84.05"
    }
}

def check_huggingface_cli():
    """Check if huggingface-cli is installed"""
    try:
        subprocess.run(["huggingface-cli", "--version"], 
                      check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] huggingface-cli not found!")
        print("[FIX] Install with: pip install -U huggingface_hub")
        return False

def download_model(model_key):
    """Download model from HuggingFace"""
    model_info = HEBREW_MODELS.get(model_key)
    if not model_info:
        print(f"[ERROR] Unknown model: {model_key}")
        print(f"Available: {list(HEBREW_MODELS.keys())}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Downloading: {model_info['name']}")
    print(f"Repo: {model_info['hf_repo']}")
    print(f"Size: {model_info['size']}")
    print(f"{'='*60}\n")
    
    # Create models directory
    os.makedirs("models/hebrew", exist_ok=True)
    
    # Download using HuggingFace CLI
    cmd = [
        "huggingface-cli",
        "download",
        model_info['hf_repo'],
        "--local-dir", f"models/hebrew/{model_key}",
        "--local-dir-use-symlinks", "False"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n[SUCCESS] {model_info['name']} downloaded!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Download failed: {e}")
        return False

def convert_to_gguf(model_key):
    """Convert model to GGUF format for Ollama"""
    print(f"\n[INFO] Converting {model_key} to GGUF...")
    print("[NOTE] This requires llama.cpp - skipping for now")
    print("[ACTION] Use the model directly with HuggingFace Transformers")
    return True

def create_ollama_modelfile(model_key):
    """Create Ollama Modelfile for the Hebrew model"""
    model_info = HEBREW_MODELS.get(model_key)
    model_path = f"models/hebrew/{model_key}"
    
    modelfile_content = f"""# {model_info['name']} - Ollama Modelfile

FROM {model_path}

TEMPLATE \"\"\"{{{{ if .System }}}}{{{{ .System }}}}

{{{{ end }}}}{{{{ if .Prompt }}}}שאלה: {{{{ .Prompt }}}}
תשובה: {{{{ end }}}}\"\"\"

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_predict 2048

SYSTEM \"\"\"
אתה Zero Agent, עוזר AI חכם המתמחה בעברית.
ענה תמיד בעברית תקנית וברורה.
\"\"\"
"""
    
    modelfile_path = f"models/hebrew/{model_key}.Modelfile"
    with open(modelfile_path, "w", encoding="utf-8") as f:
        f.write(modelfile_content)
    
    print(f"[SUCCESS] Created Modelfile: {modelfile_path}")
    return modelfile_path

def main():
    print("\n" + "="*60)
    print("Hebrew LLM Model Downloader for Zero Agent")
    print("="*60)
    
    if not check_huggingface_cli():
        return 1
    
    print("\nAvailable Models:")
    for key, info in HEBREW_MODELS.items():
        print(f"  [{key}] {info['name']} - {info['description']}")
    
    print("\n[RECOMMENDATION] Start with 'dictalm' (DictaLM 2.0)")
    print("[NOTE] ~14GB download for 7B model\n")
    
    model_key = input("Enter model key to download (or 'all'): ").strip().lower()
    
    if model_key == "all":
        models_to_download = list(HEBREW_MODELS.keys())
    else:
        models_to_download = [model_key]
    
    for model in models_to_download:
        success = download_model(model)
        if success:
            create_ollama_modelfile(model)
        else:
            print(f"[ERROR] Failed to download {model}")
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Convert to GGUF (optional): Use llama.cpp")
    print("2. Import to Ollama: ollama create hebrew -f models/hebrew/dictalm.Modelfile")
    print("3. Test: ollama run hebrew 'מה זה Python?'")
    print("4. Update api_server.py to use 'hebrew' model")
    print("="*60 + "\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())




