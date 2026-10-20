from sentence_transformers import SentenceTransformer
from functools import lru_cache
from pdfrag.config import settings
@lru_cache(maxsize=1)
def get_transfomer_model()->SentenceTransformer:
    transformer=SentenceTransformer(model_name_or_path=settings.EMBEDDING_MODEL)
    return transformer

def embed_texts(texts:list[str],batch_size:int=32)->list[list[float]]:
    model=get_transfomer_model()
    vectors=model.encode(inputs=texts,
                               batch_size=batch_size,
                               convert_to_numpy=True,show_progress_bar=len(texts)>200,
                               normalize_embeddings=True,)
    return vectors.tolist()
def embed_query(query:str)->list[float]:
    vector=embed_texts([query])
    return vector[0]
