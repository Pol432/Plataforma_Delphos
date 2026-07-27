"""
inference/train_model.py
------------------------
Generates synthetic training data and trains the TaskEvaluationModel.

Run:
    python inference/train_model.py
    python inference/train_model.py --epochs 20 --samples 2000

Saves checkpoint to: checkpoints/task_eval_model.ckpt
Saves training log  to: logs/training.json
"""

import sys
import json
import time
import argparse
import numpy as np
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
_HERE      = Path(__file__).resolve().parent
_PROJ_ROOT = _HERE.parent.parent.parent
sys.path.insert(0, str(_HERE.parent))

import mindspore as ms
import mindspore.nn as nn
from mindspore import Tensor

ms.set_context(mode=ms.PYNATIVE_MODE)

from inference.mindspore_model  import TaskEvaluationModel, get_embedder, CKPT_PATH
from inference.text_inference   import extract_skills_from_text
from skill_taxonomy             import SKILL_INDEX, NUM_SKILLS, SKILL_NAMES


# ── Synthetic training corpus ──────────────────────────────────────────────
# Each entry: (text, ground_truth_skills)
# Ground truth is sparse — only skills directly evidenced by the text.

TRAINING_TEMPLATES = [
    # ── Python / Data Science ─────────────────────────────────────────────
    ("Desarrollé un script en Python para automatizar el procesamiento de datos de ventas usando pandas y numpy. Generé visualizaciones con matplotlib y exporté reportes automáticos.",
     {"python": 85, "pandas": 82, "numpy": 78, "analisis_datos": 80, "visualizacion_datos": 72, "resolucion_problemas": 70}),

    ("Construí un pipeline de machine learning en Python con scikit-learn para predecir churn de clientes. Incluye feature engineering, validación cruzada y métricas de evaluación.",
     {"python": 88, "machine_learning": 85, "estadistica": 75, "analisis_datos": 82, "evaluacion_modelos": 78, "ingenieria_features": 80}),

    ("Entrené una red neuronal con TensorFlow para clasificación de imágenes. Usé transfer learning con ResNet50 y logré 94% de accuracy. Gestioné el experimento con MLflow.",
     {"deep_learning": 88, "tensorflow": 85, "vision_computacional": 82, "python": 80, "evaluacion_modelos": 78, "mlops": 65}),

    ("Analicé un dataset de 500k filas con pandas y SQL avanzado. Identifiqué patrones de comportamiento de usuarios usando análisis estadístico y visualicé los hallazgos en Tableau.",
     {"analisis_datos": 88, "sql_avanzado": 82, "pandas": 85, "estadistica": 78, "visualizacion_datos": 85, "tableau": 82}),

    ("Implementé un modelo de NLP para análisis de sentimientos en reseñas de clientes usando BERT y HuggingFace. El modelo procesa 10k reseñas diarias en producción.",
     {"nlp": 90, "deep_learning": 82, "python": 85, "machine_learning": 78, "mlops": 70}),

    ("Desarrollé modelos de series temporales para forecasting de demanda usando ARIMA y Prophet. Reduje el error de predicción un 23% respecto al modelo anterior.",
     {"series_temporales": 88, "estadistica": 82, "python": 80, "analisis_datos": 85, "evaluacion_modelos": 78}),

    # ── Web Development ───────────────────────────────────────────────────
    ("Construí una aplicación web full-stack con React y Node.js. Implementé autenticación JWT, API REST con Express y base de datos PostgreSQL. Desplegué en AWS con Docker.",
     {"react": 88, "nodejs": 85, "rest_api": 82, "docker": 78, "aws": 75, "diseno_bases_datos": 70, "javascript": 88}),

    ("Desarrollé una landing page responsive con HTML5, CSS3 y JavaScript vanilla. Optimicé el Core Web Vitals y logré 95/100 en Google PageSpeed.",
     {"html_css": 88, "javascript": 78, "diseno_responsivo": 85, "seo": 68, "atencion_al_detalle": 72}),

    ("Migré una aplicación monolítica Django a microservicios con FastAPI y Docker Compose. Implementé CI/CD con GitHub Actions y tests automatizados con pytest.",
     {"django": 82, "python": 88, "docker": 85, "ci_cd": 82, "arquitectura_sistemas": 78, "pruebas_software": 75, "rest_api": 80}),

    ("Construí una API GraphQL con Node.js y Apollo Server. Diseñé el schema, implementé resolvers, paginación y caché con Redis. Documenté con Postman.",
     {"graphql": 88, "nodejs": 85, "javascript": 82, "diseno_bases_datos": 70, "rest_api": 72, "documentacion_tecnica": 65}),

    # ── DevOps / Cloud ────────────────────────────────────────────────────
    ("Configuré infraestructura en AWS usando Terraform. Implementé VPC, ECS para contenedores Docker, RDS para PostgreSQL y CloudWatch para monitoreo.",
     {"aws": 90, "terraform": 88, "docker": 85, "kubernetes": 70, "diseno_bases_datos": 72, "linux": 75}),

    ("Diseñé e implementé un pipeline CI/CD completo con Jenkins y GitHub Actions. Incluye tests unitarios, análisis de código estático, build de imágenes Docker y despliegue automático.",
     {"ci_cd": 92, "docker": 85, "git": 82, "pruebas_software": 78, "automatizacion_qa": 80, "linux": 72}),

    ("Administré clústeres de Kubernetes en producción con 50+ microservicios. Implementé Helm charts, auto-scaling, health checks y rollback automático.",
     {"kubernetes": 92, "docker": 88, "aws": 75, "arquitectura_sistemas": 82, "linux": 78}),

    # ── Design / UX ───────────────────────────────────────────────────────
    ("Diseñé la experiencia completa de una app móvil de delivery: investigación con usuarios, mapas de empatía, flujos, wireframes en Figma y pruebas de usabilidad.",
     {"diseno_ux": 90, "investigacion_usuarios": 88, "wireframing": 85, "prototipado": 82, "mapas_empatia": 80, "figma": 85, "pruebas_usuario": 78}),

    ("Creé el design system completo de una fintech: componentes UI en Figma, tokens de diseño, documentación para devs y guidelines de accesibilidad WCAG 2.1.",
     {"diseno_ui": 92, "figma": 90, "documentacion_tecnica": 75, "diseno_visual": 85, "branding": 70, "atencion_al_detalle": 82}),

    ("Rediseñé el flujo de onboarding de una app SaaS. Conduje 15 entrevistas con usuarios, analicé heatmaps, propuse mejoras y validé con A/B testing. Reduje la tasa de abandono un 34%.",
     {"diseno_ux": 92, "investigacion_usuarios": 90, "ab_testing": 85, "analisis_datos": 72, "pruebas_usuario": 88, "customer_journey": 82}),

    ("Diseñé la identidad visual completa de una startup: logo, paleta de colores, tipografía, iconografía y manual de marca. Trabajé en Figma e Illustrator.",
     {"branding": 92, "diseno_grafico": 88, "diseno_logo": 85, "teoria_color": 82, "tipografia": 80, "figma": 75, "creatividad": 85}),

    ("Desarrollé prototipos interactivos de alta fidelidad para una app de salud. Conduje pruebas con 20 usuarios y documenté insights para el equipo de desarrollo.",
     {"prototipado": 90, "wireframing": 82, "pruebas_usuario": 88, "diseno_ux": 85, "documentacion_tecnica": 68, "empatia": 72}),

    # ── Content / Marketing ───────────────────────────────────────────────
    ("Gestioné la estrategia de contenido para redes sociales de una marca de moda. Crecí la audiencia de Instagram de 5k a 45k en 6 meses con contenido orgánico.",
     {"contenido_redes": 92, "marketing": 88, "creatividad": 82, "copywriting": 78, "estrategia_negocio": 72, "marketing_redes": 90}),

    ("Escribí artículos de blog optimizados para SEO en el nicho de tecnología. Logré posicionamiento en top 3 de Google para 12 keywords con alto volumen.",
     {"seo_writing": 90, "seo": 85, "blog_writing": 88, "copywriting": 78, "investigacion_mercado": 68}),

    ("Produje y edité 50+ videos para YouTube sobre programación. Creé guiones, grabé tutoriales, edité en Premiere Pro y diseñé thumbnails en Photoshop.",
     {"edicion_video": 90, "guion": 82, "contenido_redes": 78, "copywriting": 70, "diseno_grafico": 68, "storytelling": 75}),

    # ── Leadership / Management ───────────────────────────────────────────
    ("Lideré un equipo de 8 desarrolladores en la migración de un sistema legado a microservicios. Gestioné el roadmap, las ceremonias ágiles y la comunicación con stakeholders.",
     {"liderazgo": 90, "gestion_equipos": 88, "metodologia_agile": 85, "scrum": 82, "gestion_stakeholders": 80, "planificacion_proyectos": 85}),

    ("Como Product Manager lancé una feature de pagos en cuotas que incrementó la conversión un 28%. Coordiné diseño, ingeniería y legal. Definí métricas y OKRs.",
     {"gestion_producto": 92, "estrategia_negocio": 82, "analisis_datos": 75, "gestion_stakeholders": 85, "planificacion_proyectos": 80, "toma_decisiones": 78}),

    ("Facilité talleres de Design Thinking con equipos de hasta 30 personas para resolver problemas de negocio. Usé metodologías como How Might We, SCAMPER y prototipado rápido.",
     {"design_thinking": 92, "facilitacion": 90, "creatividad": 85, "innovacion": 82, "comunicacion_verbal": 78, "liderazgo": 72}),

    ("Implementé metodología Scrum en un equipo de 12 personas. Conduje daily standups, sprint planning, retrospectivas y demos. Mejoré la velocidad del equipo un 40%.",
     {"scrum": 92, "metodologia_agile": 88, "liderazgo": 80, "comunicacion_verbal": 78, "gestion_equipos": 82, "mejora_procesos": 80}),

    # ── Business / Analysis ───────────────────────────────────────────────
    ("Realicé análisis de mercado para lanzamiento de producto en Latinoamérica. Incluye análisis competitivo, encuestas a 200 usuarios, proyecciones financieras y go-to-market.",
     {"investigacion_mercado": 92, "analisis_competitivo": 88, "analisis_financiero": 78, "estrategia_negocio": 82, "pensamiento_analitico": 80}),

    ("Desarrollé modelo financiero en Excel para proyecciones de una startup en Serie A. Incluye P&L, flujo de caja, análisis de escenarios y métricas SaaS (MRR, churn, LTV).",
     {"analisis_financiero": 92, "excel_avanzado": 88, "estrategia_negocio": 80, "pensamiento_analitico": 82, "estadistica": 72}),

    ("Diseñé e implementé estrategia de email marketing con HubSpot. Segmenté base de 50k contactos, personalicé secuencias y logré tasa de apertura del 38% vs 21% promedio del sector.",
     {"email_marketing": 92, "hubspot": 85, "marketing": 82, "analisis_datos": 72, "copywriting": 75}),

    # ── Security / Testing ────────────────────────────────────────────────
    ("Realicé auditoría de seguridad web a una aplicación financiera. Identifiqué vulnerabilidades OWASP Top 10, documenté hallazgos y propuse remediaciones. Usé Burp Suite y OWASP ZAP.",
     {"ciberseguridad": 92, "seguridad_web": 90, "documentacion_tecnica": 72, "pensamiento_analitico": 78, "atencion_al_detalle": 82}),

    ("Implementé suite de pruebas automatizadas con Selenium y pytest. Cubrí 85% del código con tests unitarios e integración. Integré al pipeline CI/CD.",
     {"automatizacion_qa": 92, "pruebas_software": 88, "python": 80, "ci_cd": 75, "atencion_al_detalle": 82}),

    # ── Database ──────────────────────────────────────────────────────────
    ("Diseñé e implementé el esquema de base de datos de una plataforma educativa con PostgreSQL. Optimicé queries lentas con índices y reduje tiempos de respuesta un 70%.",
     {"diseno_bases_datos": 92, "postgresql": 88, "sql_avanzado": 85, "pensamiento_sistemico": 75, "atencion_al_detalle": 78}),

    ("Migré base de datos de MySQL a MongoDB para un sistema de catálogo. Diseñé el modelo de documentos, implementé índices y configuré replica set para alta disponibilidad.",
     {"diseno_bases_datos": 88, "mongodb": 85, "arquitectura_sistemas": 78, "pensamiento_analitico": 72}),
]


def build_skill_vector(skill_dict: dict[str, float]) -> np.ndarray:
    """Convert {slug: score} → ordered 200-dim numpy array."""
    vec = np.zeros(NUM_SKILLS, dtype=np.float32)
    for slug, score in skill_dict.items():
        idx = SKILL_INDEX.get(slug)
        if idx is not None:
            vec[idx] = float(score)
    return vec


def generate_dataset(
    num_samples: int,
    augment: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build X (embeddings) and y (skill vectors) training arrays.

    Augmentation: repeats templates with small Gaussian noise on embeddings
    to simulate variation without needing more labeled data.
    """
    embedder = get_embedder()
    print(f"  Embedding {len(TRAINING_TEMPLATES)} templates...")

    texts    = [t[0] for t in TRAINING_TEMPLATES]
    labels   = [t[1] for t in TRAINING_TEMPLATES]

    base_embs   = embedder.encode(texts, normalize_embeddings=True,
                                  show_progress_bar=False)           # (N, 384)
    base_labels = np.array([build_skill_vector(l) for l in labels])  # (N, 200)

    if not augment or num_samples <= len(TRAINING_TEMPLATES):
        return base_embs[:num_samples], base_labels[:num_samples]

    # Augment by repeating with noise
    X_list, y_list = [base_embs], [base_labels]
    rng = np.random.default_rng(42)

    while sum(len(x) for x in X_list) < num_samples:
        noise = rng.normal(0, 0.015, base_embs.shape).astype(np.float32)
        noisy = base_embs + noise
        # Re-normalize
        norms = np.linalg.norm(noisy, axis=1, keepdims=True)
        noisy = noisy / np.maximum(norms, 1e-8)
        X_list.append(noisy)
        y_list.append(base_labels)

    X = np.vstack(X_list)[:num_samples]
    y = np.vstack(y_list)[:num_samples]
    return X.astype(np.float32), y.astype(np.float32)


def train(
    num_samples: int = 1500,
    epochs:      int = 15,
    batch_size:  int = 32,
    lr:          float = 0.001,
):
    print("=" * 55)
    print("  Training TaskEvaluationModel")
    print("=" * 55)

    # ── Build dataset ──────────────────────────────────────────────────
    print("\n[1/4] Generating training data...")
    X, y = generate_dataset(num_samples)
    print(f"  Dataset shape: X={X.shape}, y={y.shape}")

    # Train / val split (90/10)
    split   = int(len(X) * 0.9)
    X_train, X_val = X[:split], X[split:]
    y_train, y_val = y[:split], y[split:]
    print(f"  Train: {len(X_train)} | Val: {len(X_val)}")

    # ── Build model ────────────────────────────────────────────────────
    print("\n[2/4] Initialising model...")
    model     = TaskEvaluationModel()
    loss_fn   = nn.MSELoss()
    optimizer = nn.Adam(model.trainable_params(), learning_rate=lr)

    # ── Training loop ──────────────────────────────────────────────────
    print(f"\n[3/4] Training for {epochs} epochs (batch={batch_size})...")
    history = []

    def forward_fn(x_batch, y_batch):
        pred = model(x_batch)
        return loss_fn(pred, y_batch)

    grad_fn = ms.value_and_grad(forward_fn, None, optimizer.parameters)

    for epoch in range(1, epochs + 1):
        model.set_train(True)
        t0          = time.time()
        epoch_loss  = 0.0
        steps       = 0
        indices     = np.random.permutation(len(X_train))

        for start in range(0, len(X_train), batch_size):
            batch_idx = indices[start: start + batch_size]
            xb = Tensor(X_train[batch_idx], ms.float32)
            yb = Tensor(y_train[batch_idx], ms.float32)
            loss, grads = grad_fn(xb, yb)
            optimizer(grads)
            epoch_loss += float(loss.asnumpy())
            steps += 1

        # Validation loss
        model.set_train(False)
        val_loss = float(
            loss_fn(
                model(Tensor(X_val, ms.float32)),
                Tensor(y_val, ms.float32)
            ).asnumpy()
        )

        avg_train = epoch_loss / steps
        elapsed   = time.time() - t0
        history.append({"epoch": epoch, "train_loss": avg_train, "val_loss": val_loss})

        if epoch % 3 == 0 or epoch == 1 or epoch == epochs:
            print(f"  Epoch {epoch:>3}/{epochs}  "
                  f"train={avg_train:.2f}  val={val_loss:.2f}  "
                  f"({elapsed:.1f}s)")

    # ── Save checkpoint ────────────────────────────────────────────────
    print("\n[4/4] Saving checkpoint...")
    CKPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ms.save_checkpoint(model, str(CKPT_PATH))
    print(f"  ✓ Saved: {CKPT_PATH}")

    # ── Save training log ──────────────────────────────────────────────
    log_dir = _PROJ_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "training.json"
    log_data = {
        "timestamp":   time.strftime("%Y-%m-%dT%H:%M:%S"),
        "num_samples": num_samples,
        "epochs":      epochs,
        "batch_size":  batch_size,
        "lr":          lr,
        "final_train_loss": history[-1]["train_loss"],
        "final_val_loss":   history[-1]["val_loss"],
        "history":     history,
    }
    log_path.write_text(json.dumps(log_data, indent=2))
    print(f"  ✓ Log:  {log_path}")

    # ── Quick sanity check ─────────────────────────────────────────────
    print("\n── Sanity check ──────────────────────────────────────")
    model.set_train(False)
    test_text = ("Desarrollé un modelo de machine learning con Python "
                 "y scikit-learn para predecir precios de casas.")
    from inference.mindspore_model import embed_text
    emb    = embed_text(test_text)
    pred   = model(Tensor(emb[np.newaxis, :], ms.float32)).asnumpy()[0]
    top5   = sorted(
        ((SKILL_NAMES[i], pred[i]) for i in range(NUM_SKILLS)),
        key=lambda x: -x[1]
    )[:5]
    print(f"  Text: \"{test_text[:55]}...\"")
    print("  Top 5 predictions:")
    for slug, score in top5:
        print(f"    {slug}: {score:.1f}")

    print("\n✓ Training complete")
    return history


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=1500,
                        help="Training samples (default: 1500)")
    parser.add_argument("--epochs",  type=int, default=15,
                        help="Training epochs (default: 15)")
    parser.add_argument("--lr",      type=float, default=0.001,
                        help="Learning rate (default: 0.001)")
    parser.add_argument("--batch",   type=int, default=32,
                        help="Batch size (default: 32)")
    args = parser.parse_args()

    train(
        num_samples=args.samples,
        epochs=args.epochs,
        lr=args.lr,
        batch_size=args.batch,
    )
