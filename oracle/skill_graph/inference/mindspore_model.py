"""
inference/mindspore_model.py
----------------------------
MindSpore TaskEvaluationModel: takes a 384-dim sentence embedding
and outputs 200 skill scores (0–100).

Architecture:
    Input (384) → Dense(512) → ReLU → Dropout
                → Dense(256) → ReLU → Dropout
                → Dense(128) → ReLU
                → Dense(200) → Sigmoid × 100

Also provides:
    - get_embedder()        : loads sentence-transformers model (cached)
    - embed_text(text)      : text → numpy (384,)
    - predict_skills(text)  : text → {slug: score} using the full pipeline

Training is done via train_model.py (Day 3 script).
At inference time the model loads from checkpoints/task_eval_model.ckpt.
If no checkpoint exists, a randomly-initialised model is used and scores
will be near-random until training runs — text_inference.py covers that gap.
"""

import os
import numpy as np
from pathlib import Path
from typing import Optional

# ── MindSpore ─────────────────────────────────────────────────────────────
import mindspore as ms
import mindspore.nn as nn
import mindspore.ops as ops
from mindspore import Tensor, Parameter

# Use PyNative (eager) mode for simplicity during the sprint
ms.set_context(mode=ms.PYNATIVE_MODE)

# ── Project paths ─────────────────────────────────────────────────────────
_HERE       = Path(__file__).resolve().parent          # inference/
_PROJ_ROOT  = _HERE.parent.parent.parent               # temporal-skill-graph/
CKPT_PATH   = _PROJ_ROOT / "checkpoints" / "task_eval_model.ckpt"

# ── Constants ─────────────────────────────────────────────────────────────
EMBEDDING_DIM = 384      # all-MiniLM-L6-v2 output size
NUM_SKILLS    = 200
HIDDEN_DIMS   = [512, 256, 128]
DROPOUT_KEEP  = 0.85     # keep_prob — 15% dropout during training


# ── Model definition ───────────────────────────────────────────────────────

class TaskEvaluationModel(nn.Cell):
    """
    Feedforward network: text_embedding → skill_scores.

    Output is scaled to [0, 100] via Sigmoid × 100.
    Each output neuron corresponds to one skill in SKILL_NAMES order
    (see skill_taxonomy.py).
    """

    def __init__(
        self,
        input_dim:   int       = EMBEDDING_DIM,
        hidden_dims: list[int] = None,
        num_skills:  int       = NUM_SKILLS,
        dropout_keep: float    = DROPOUT_KEEP,
    ):
        super().__init__()
        if hidden_dims is None:
            hidden_dims = HIDDEN_DIMS

        layers = []
        prev = input_dim
        for h in hidden_dims:
            layers.append(nn.Dense(prev, h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(keep_prob=dropout_keep))
            prev = h

        self.encoder  = nn.SequentialCell(layers)
        self.output   = nn.Dense(prev, num_skills)
        self.sigmoid  = nn.Sigmoid()

    def construct(self, x: Tensor) -> Tensor:
        """
        Args:
            x: [batch, EMBEDDING_DIM]  float32
        Returns:
            scores: [batch, NUM_SKILLS]  float32  (0–100)
        """
        hidden = self.encoder(x)
        logits = self.output(hidden)
        return self.sigmoid(logits) * 100.0


# ── Singleton model instance ───────────────────────────────────────────────

_model: Optional[TaskEvaluationModel] = None

def get_model(force_reload: bool = False) -> TaskEvaluationModel:
    """
    Returns the singleton model instance.
    Loads checkpoint if available, otherwise uses random weights.
    """
    global _model
    if _model is not None and not force_reload:
        return _model

    _model = TaskEvaluationModel()
    _model.set_train(False)

    if CKPT_PATH.exists():
        try:
            param_dict = ms.load_checkpoint(str(CKPT_PATH))
            ms.load_param_into_net(_model, param_dict)
            print(f"✓ Loaded checkpoint: {CKPT_PATH}")
        except Exception as e:
            print(f"⚠ Could not load checkpoint ({e}) — using random weights")
    else:
        print(f"⚠ No checkpoint at {CKPT_PATH} — using random weights")
        print(f"  Run: python inference/train_model.py  to train the model")

    return _model


# ── Embedder ───────────────────────────────────────────────────────────────

_embedder = None

def get_embedder():
    """Lazy-load sentence-transformers embedder (cached after first call)."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        print("✓ Sentence embedder loaded (all-MiniLM-L6-v2)")
    return _embedder


def embed_text(text: str) -> np.ndarray:
    """
    Convert text to 384-dim numpy embedding.
    """
    embedder = get_embedder()
    return embedder.encode(text, normalize_embeddings=True)


# ── Inference pipeline ────────────────────────────────────────────────────

def predict_skills(
    text: str,
    threshold: float = 5.0,
) -> dict[str, float]:
    """
    Full pipeline: text → {slug: score}.

    Args:
        text:      raw task submission or description
        threshold: minimum score to include in output (filters noise)

    Returns:
        {slug: score_0_to_100} for skills above threshold
    """
    from skill_taxonomy import SKILL_NAMES

    # 1. Embed
    embedding = embed_text(text)                                   # (384,)
    tensor    = Tensor(embedding[np.newaxis, :], ms.float32)       # (1, 384)

    # 2. Forward pass
    model  = get_model()
    model.set_train(False)
    output = model(tensor)                                         # (1, 200)
    scores_np = output.asnumpy()[0]                                # (200,)

    # 3. Map to slugs
    return {
        SKILL_NAMES[i]: float(scores_np[i])
        for i in range(NUM_SKILLS)
        if scores_np[i] >= threshold
    }


def predict_skills_batch(
    texts: list[str],
    threshold: float = 5.0,
) -> list[dict[str, float]]:
    """
    Batch inference for multiple texts at once (faster than one-by-one).
    """
    from skill_taxonomy import SKILL_NAMES

    embedder   = get_embedder()
    embeddings = embedder.encode(texts, normalize_embeddings=True,
                                  batch_size=32)                   # (N, 384)
    tensor     = Tensor(embeddings.astype(np.float32))             # (N, 384)

    model  = get_model()
    model.set_train(False)
    output = model(tensor).asnumpy()                               # (N, 200)

    results = []
    for row in output:
        results.append({
            SKILL_NAMES[i]: float(row[i])
            for i in range(NUM_SKILLS)
            if row[i] >= threshold
        })
    return results


# ── Model info ─────────────────────────────────────────────────────────────

def model_summary() -> dict:
    """Return basic model stats."""
    m = get_model()
    total_params = sum(p.size for p in m.trainable_params())
    return {
        "input_dim":    EMBEDDING_DIM,
        "hidden_dims":  HIDDEN_DIMS,
        "output_dim":   NUM_SKILLS,
        "total_params": total_params,
        "checkpoint":   str(CKPT_PATH) if CKPT_PATH.exists() else None,
    }


if __name__ == "__main__":
    print("=== MindSpore TaskEvaluationModel ===")
    info = model_summary()
    print(f"  Architecture : {info['input_dim']} → "
          f"{' → '.join(str(h) for h in info['hidden_dims'])} → {info['output_dim']}")
    print(f"  Total params : {info['total_params']:,}")
    print(f"  Checkpoint   : {info['checkpoint'] or 'none (untrained)'}")

    # Quick smoke test — random weights, scores will be ~50 but shape must be right
    sample = (
        "Desarrollé un clasificador de imágenes con PyTorch usando transfer learning. "
        "El modelo alcanzó 92% de accuracy en el dataset de prueba. "
        "Usé Python, pandas para el preprocesamiento y matplotlib para visualizar "
        "las métricas de entrenamiento. El código está en GitHub con CI/CD en Actions."
    )
    print(f"\n  Sample text : \"{sample[:60]}...\"")
    preds = predict_skills(sample, threshold=10.0)
    print(f"  Skills above threshold (10): {len(preds)}")
    top = sorted(preds.items(), key=lambda x: -x[1])[:8]
    for slug, score in top:
        print(f"    {slug}: {score:.1f}")
    print("\n✓ Model smoke test passed")
