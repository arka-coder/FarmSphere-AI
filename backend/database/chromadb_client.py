"""
FarmSphere AI — ChromaDB Client
Manages vector collections for RAG: ICAR docs, community knowledge, crop manuals.
Uses PersistentClient — stores data in ./chroma_data/ with no server required.
"""
import logging
import os
from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)

# ── Client singleton ─────────────────────────────────────────────────────────

_client: Optional[chromadb.PersistentClient] = None

# Persist data next to this file: backend/chroma_data/
_CHROMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chroma_data")


def get_chroma_client() -> chromadb.PersistentClient:
    """Return a singleton PersistentClient that saves data to disk."""
    global _client
    if _client is None:
        os.makedirs(_CHROMA_PATH, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=_CHROMA_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info("ChromaDB persistent store ready at: %s", os.path.abspath(_CHROMA_PATH))
    return _client


# ── Collection names ─────────────────────────────────────────────────────────

COLLECTIONS = {
    "icar_docs": "icar_agricultural_documents",
    "crop_manuals": "crop_cultivation_manuals",
    "community": "community_farmer_knowledge",
    "disease_refs": "plant_disease_references",
    "schemes": "government_schemes",
}


def get_collection(name: str):
    client = get_chroma_client()
    col_name = COLLECTIONS.get(name, name)
    return client.get_or_create_collection(
        name=col_name,
        metadata={"hnsw:space": "cosine"},
    )


# ── Ingestion ────────────────────────────────────────────────────────────────

def ingest_documents(
    collection_name: str,
    documents: list[str],
    metadatas: list[dict],
    ids: list[str],
    embeddings: Optional[list[list[float]]] = None,
) -> int:
    col = get_collection(collection_name)
    kwargs = dict(documents=documents, metadatas=metadatas, ids=ids)
    if embeddings:
        kwargs["embeddings"] = embeddings
    col.upsert(**kwargs)
    logger.info("Ingested %d docs into collection '%s'", len(documents), collection_name)
    return len(documents)


# ── Retrieval ────────────────────────────────────────────────────────────────

def query_collection(
    collection_name: str,
    query_texts: list[str],
    n_results: int = 5,
    where: Optional[dict] = None,
) -> dict:
    col = get_collection(collection_name)
    kwargs = dict(
        query_texts=query_texts,
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    if where:
        kwargs["where"] = where
    try:
        results = col.query(**kwargs)
        return results
    except Exception as e:
        logger.error("ChromaDB query failed: %s", e)
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}


# ── Seed Demo Data ───────────────────────────────────────────────────────────

DEMO_ICAR_DOCS = [
    {
        "id": "icar_tomato_blight_001",
        "text": (
            "Early Blight of Tomato (Alternaria solani): Early blight appears as small, "
            "dark brown spots on lower leaves, surrounded by yellow halos. Spots enlarge to "
            "1-2 cm with concentric rings (target-board pattern). Severe infection causes "
            "defoliation. Management: Use resistant varieties, apply Mancozeb 0.2% or "
            "Copper oxychloride 0.3% at 10-day intervals. Remove infected leaves. Avoid "
            "overhead irrigation. Crop rotation recommended."
        ),
        "metadata": {"crop": "tomato", "disease": "early_blight", "source": "ICAR Tomato Disease Manual", "language": "en"},
    },
    {
        "id": "icar_tomato_late_blight_001",
        "text": (
            "Late Blight of Tomato (Phytophthora infestans): Water-soaked lesions on leaves "
            "that turn brown to black. White sporulation visible on underside in humid conditions. "
            "Can destroy entire field within days. Management: Apply Metalaxyl + Mancozeb 0.2%, "
            "Dimethomorph 0.1%. Ensure good drainage. Plant certified disease-free seedlings."
        ),
        "metadata": {"crop": "tomato", "disease": "late_blight", "source": "ICAR Plant Pathology Guide", "language": "en"},
    },
    {
        "id": "icar_wheat_rust_001",
        "text": (
            "Yellow Rust / Stripe Rust of Wheat (Puccinia striiformis): Yellow-orange pustules "
            "arranged in stripes on leaves and stems. Highly favored by cool, moist conditions "
            "(10-15°C). Management: Grow resistant varieties (HD 2967, PBW 621). Apply "
            "Propiconazole 0.1% at first appearance. Early sowing reduces risk."
        ),
        "metadata": {"crop": "wheat", "disease": "yellow_rust", "source": "ICAR Wheat Crop Guide", "language": "en"},
    },
    {
        "id": "icar_rice_blast_001",
        "text": (
            "Rice Blast (Magnaporthe oryzae): Diamond-shaped lesions with grey centers and "
            "brown margins on leaves. Also affects neck and nodes (neck rot). Most destructive "
            "rice disease worldwide. Management: Tricyclazole 0.06%, Carbendazim 0.1%. "
            "Balanced nitrogen fertilization. Silicon application improves resistance."
        ),
        "metadata": {"crop": "rice", "disease": "blast", "source": "ICAR Rice Production Manual", "language": "en"},
    },
    {
        "id": "icar_fertilizer_tomato_001",
        "text": (
            "Fertilizer Recommendation for Tomato: Apply FYM 25 t/ha at planting. "
            "Basal dose: N:P:K = 75:50:50 kg/ha. Top dressing: 75 kg N/ha in 2 splits "
            "at 30 and 60 days after transplanting. Micronutrients: Boron 1 kg/ha improves "
            "fruit set. Zinc 25 kg ZnSO4/ha if deficient."
        ),
        "metadata": {"crop": "tomato", "type": "fertilizer", "source": "ICAR Tomato Cultivation Guide", "language": "en"},
    },
    {
        "id": "pm_kisan_scheme_001",
        "text": (
            "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi): Provides income support of "
            "Rs 6000/year to all landholding farmer families. Amount released in 3 equal "
            "installments of Rs 2000 each. Eligibility: Farmer families with cultivable "
            "land. Exclusions: Income tax payers, professionals, retired government employees. "
            "Application: PM-KISAN portal or CSC centers. Documents: Aadhaar, bank account, land records."
        ),
        "metadata": {"type": "scheme", "scheme_name": "PM-KISAN", "source": "Government of India", "language": "en"},
    },
    {
        "id": "pmfby_scheme_001",
        "text": (
            "PMFBY (Pradhan Mantri Fasal Bima Yojana): Crop insurance scheme. Premium: "
            "2% for Kharif, 1.5% for Rabi, 5% for commercial crops. Coverage: Natural "
            "calamities, pests, diseases. Claim settlement within 2 months. Enrollment "
            "through banks at time of crop loan. Can also enroll without loan through CSC."
        ),
        "metadata": {"type": "scheme", "scheme_name": "PMFBY", "source": "Ministry of Agriculture", "language": "en"},
    },
    {
        "id": "organic_farming_001",
        "text": (
            "Organic Pest Management: Neem-based pesticides (Azadirachtin) effective against "
            "a wide range of pests. Prepare neem oil spray: 5 ml neem oil + 1 ml soap per liter water. "
            "Trichoderma viride for soil-borne diseases. Panchagavya (cow dung, urine, milk, curd, ghee) "
            "improves plant immunity. Crop rotation and intercropping reduce pest pressure naturally."
        ),
        "metadata": {"type": "organic", "source": "ICAR Organic Farming Guide", "language": "en"},
    },
]


def seed_demo_data():
    """Seed ChromaDB with demo ICAR documents for the hackathon."""
    docs = [d["text"] for d in DEMO_ICAR_DOCS]
    metas = [d["metadata"] for d in DEMO_ICAR_DOCS]
    ids = [d["id"] for d in DEMO_ICAR_DOCS]
    ingest_documents("icar_docs", docs, metas, ids)
    logger.info("Demo ICAR data seeded into ChromaDB.")
