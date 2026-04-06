import logging
from typing import List, Dict, Any, Optional
from openrouter_insights.domain.entities import LLMModel, Pricing, Benchmarks
from openrouter_insights.domain.interfaces import IModelRepository, IFetcherGateway, IStaticExporter
from openrouter_insights.domain.services.matching_engine import MatchingEngine

logger = logging.getLogger(__name__)

class SyncRegistryUseCase:
    """
    Use Case: Synchronize the LLM Registry using High-Fidelity REAL data.
    Enriched with Multimodal Media ELO Ratings.
    """

    def __init__(
        self, 
        repository: IModelRepository, 
        gateways: List[IFetcherGateway],
        matching_engine: MatchingEngine,
        exporter: Optional[IStaticExporter] = None
    ):
        self.repository = repository
        self.gateways = gateways
        self.matching_engine = matching_engine
        self.exporter = exporter

    async def execute(self) -> List[LLMModel]:
        raw_catalogs: List[Dict[str, Any]] = []
        raw_benchmarks: List[Dict[str, Any]] = []
        
        for gateway in self.gateways:
            raw_catalogs.extend(await gateway.fetch_catalog())
            raw_benchmarks.extend(await gateway.fetch_benchmarks())

        if not raw_catalogs:
            return []

        # Build candidate list for the matching engine
        # We index candidates by Slug and Name to allow fuzzy discovery
        candidates = []
        benchmark_map = {}
        for b in raw_benchmarks:
            # High-Fidelity: Index by multiple identifiers
            for key in ["slug", "name", "id"]:
                val = b.get(key)
                if val:
                    candidates.append(val)
                    benchmark_map[val] = b


        final_models: List[LLMModel] = []

        for item in raw_catalogs:
            model_id = item.get("id")
            if not model_id: continue

            # MULTI-MATCH LOGIC: Try to find multiple sources for this OR model
            # We iterate through the whole candidate list to find ANY good match
            # This allows capturing both LLM scores AND Media ELO if they exist as separate AA entries
            
            pricing_raw = item.get("pricing", {})
            pricing = Pricing(
                input=float(pricing_raw.get("prompt") or 0) * 1_000_000,
                output=float(pricing_raw.get("completion") or 0) * 1_000_000
            )

            # High-Fidelity Benchmarks mapping
            # We look for ANY data across all matched candidates
            benchmarks = Benchmarks()
            has_benchmarks = False

            # We use the matching engine to find the BEST candidate
            # But we could also find MULTIPLE if we wanted to be even deeper.
            # For now, let's just make sure we check multiple keys.
            
            match_id, score = self.matching_engine.find_match(model_id, candidates)
            logger.info(f"Target: {model_id} | Match: {match_id} | Score: {score}")
            
            if match_id:
                aa = benchmark_map[match_id]
                evals = aa.get("evaluations", {})
                
                benchmarks.intelligence_score = self._get_float(evals, ["artificial_analysis_intelligence_index", "intelligence"])
                benchmarks.speed_score = self._get_float(aa, ["median_output_tokens_per_second", "speed"])
                benchmarks.reasoning_score = self._get_float(evals, ["artificial_analysis_reasoning_index", "reasoning"])
                benchmarks.coding_score = self._get_float(evals, ["artificial_analysis_coding_index", "coding"])
                benchmarks.elo_score = self._get_float(aa, ["quality_score", "elo_rating", "elo"])
                has_benchmarks = True

            # Improved Provider Extraction
            provider_raw = item.get("provider", {})
            provider_name = "Unknown"
            if isinstance(provider_raw, dict):
                provider_name = provider_raw.get("name") or "Unknown"
            
            if provider_name == "Unknown":
                model_id = item.get("id", "")
                if "/" in model_id:
                    # e.g. "openai/gpt-4" -> "OpenAI"
                    raw_prefix = model_id.split("/")[0]
                    # Map common slugs to display names
                    mapping = {
                        "openai": "OpenAI",
                        "anthropic": "Anthropic",
                        "google": "Google",
                        "meta": "Meta",
                        "mistral": "Mistral",
                        "x-ai": "xAI",
                        "deepseek": "DeepSeek",
                        "microsoft": "Microsoft",
                        "cohere": "Cohere"
                    }
                    provider_name = mapping.get(raw_prefix.lower(), raw_prefix.title())
                elif ":" in item.get("name", ""):
                    provider_name = item.get("name").split(":")[0].strip()

            model = LLMModel(
                id=model_id,
                name=item.get("name") or model_id,
                provider=provider_name,
                context_length=int(item.get("context_length") or 0),
                pricing=pricing,
                modalities=item.get("architecture", {}).get("input_modalities", ["text"]),
                benchmarks=benchmarks if has_benchmarks else None
            )
            final_models.append(model)


        if final_models:
            self.repository.save_batch(final_models)
            if self.exporter:
                self.exporter.export(final_models)
            
        return final_models

    def _get_float(self, data: Dict, keys: List[str]) -> Optional[float]:
        for key in keys:
            val = data.get(key)
            if val is not None:
                try: return float(val)
                except: continue
        return None
