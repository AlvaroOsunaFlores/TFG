import os

import torch
from huggingface_hub import hf_hub_download
from transformers import AutoConfig, AutoTokenizer, AutoModelForSequenceClassification


def _load_from_transformers_repo(hf_model: str):
    tokenizer = AutoTokenizer.from_pretrained(hf_model)
    model = AutoModelForSequenceClassification.from_pretrained(hf_model)
    model_source = f"transformers_repo:{hf_model}"
    return tokenizer, model, model_source


def _load_from_state_dict_fallback(hf_model: str):
    base_model = os.getenv("HF_BASE_MODEL", "distilbert-base-uncased")
    state_dict_file = os.getenv("HF_STATE_DICT_FILE", "distilbert_fast_fixed_labels.pt")

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    config = AutoConfig.from_pretrained(base_model, num_labels=2)
    model = AutoModelForSequenceClassification.from_config(config)

    state_path = hf_hub_download(repo_id=hf_model, filename=state_dict_file)
    state_dict = torch.load(state_path, map_location="cpu")

    if isinstance(state_dict, dict) and "state_dict" in state_dict and isinstance(state_dict["state_dict"], dict):
        state_dict = state_dict["state_dict"]

    try:
        model.load_state_dict(state_dict)
    except RuntimeError:
        # Soporta checkpoints guardados con DataParallel ("module.*")
        cleaned_state_dict = {
            (k[7:] if k.startswith("module.") else k): v for k, v in state_dict.items()
        }
        model.load_state_dict(cleaned_state_dict)

    model_source = f"state_dict:{hf_model}/{state_dict_file} base:{base_model}"
    return tokenizer, model, model_source


def load_tokenizer_and_model(hf_model: str, device: torch.device):
    """
    Intenta cargar un modelo/tokenizer en formato Transformers completo.
    Si falla, usa un fallback para repos que solo exponen un state_dict (.pt).
    """
    try:
        tokenizer, model, model_source = _load_from_transformers_repo(hf_model)
    except Exception:
        try:
            tokenizer, model, model_source = _load_from_state_dict_fallback(hf_model)
        except Exception as fallback_error:
            raise RuntimeError(
                "No se pudo cargar el modelo ni como repositorio Transformers ni como state_dict fallback."
            ) from fallback_error

    model.to(device)
    model.eval()
    return tokenizer, model, model_source
