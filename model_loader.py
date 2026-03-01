import os

import torch
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer, AutoModelForSequenceClassification


def load_tokenizer_and_model(hf_model: str, device: torch.device):
    """
    Intenta cargar un modelo/tokenizer en formato Transformers completo.
    Si falla, usa un fallback para repos que solo exponen un state_dict (.pt).
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(hf_model)
        model = AutoModelForSequenceClassification.from_pretrained(hf_model)
        model_source = f"transformers_repo:{hf_model}"
    except OSError:
        base_model = os.getenv("HF_BASE_MODEL", "distilbert-base-uncased")
        state_dict_file = os.getenv("HF_STATE_DICT_FILE", "distilbert_fast_fixed_labels.pt")

        tokenizer = AutoTokenizer.from_pretrained(base_model)
        model = AutoModelForSequenceClassification.from_pretrained(base_model, num_labels=2)

        state_path = hf_hub_download(repo_id=hf_model, filename=state_dict_file)
        state_dict = torch.load(state_path, map_location="cpu")
        model.load_state_dict(state_dict)
        model_source = f"state_dict:{hf_model}/{state_dict_file} base:{base_model}"

    model.to(device)
    model.eval()
    return tokenizer, model, model_source
