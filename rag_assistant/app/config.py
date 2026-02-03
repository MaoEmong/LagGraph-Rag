from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "rag_assistant"
    env: str = "local"
    openai_api_key: str = ""
    openai_base_url: str = ""
    openai_timeout_sec: float = 30.0
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_batch_size: int = 32
    ocr_enabled: bool = False
    ocr_lang: str = "kor+eng"
    ocr_dpi: int = 200
    ocr_max_pages: int = 0
    ocr_min_text_len: int = 100
    reranker_on: bool = False
    reranker_mode: str = "off"  # off | auto | always
    rerank_top_k: int = 20
    reranker_model: str = "none"
    reranker_timeout_sec: float = 10.0
    reranker_score_threshold: float = -1.0
    reranker_distance_threshold: float = 0.6
    reranker_batch_size: int = 16
    db_enabled: bool = False
    db_adapter: str = "mock"
    db_url: str = ""
    db_row_limit: int = 100
    db_timeout_sec: float = 5.0
    db_max_filters: int = 10
    db_max_joins: int = 5
    db_max_group_by: int = 5
    db_max_metrics: int = 5
    db_max_order_by: int = 3
    db_max_select: int = 5
    db_denylist_keywords: str = "drop,delete,update,insert,alter,truncate"
    db_plan_model: str = "gpt-4o-mini"
    db_plan_temperature: float = 0.0
    db_plan_max_output_tokens: int = 256
    temperature: float = 0.2
    max_output_tokens: int = 512
    top_k: int = 5
    log_path: str = "./logs"
    chroma_path: str = "./data/chroma"
    docstore_path: str = "./data/docstore.sqlite"
    checkpoint_path: str = "./data/checkpoints.sqlite"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
