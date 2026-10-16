"""Curated registry of network destinations.

Each entry maps a domain suffix to who operates it, under which jurisdiction,
and what role it plays. The registry is data, not network code: Sigillum never
contacts these hosts. It is deliberately public and editable — a wrong or
missing entry is a bug anyone can fix with a pull request.

Jurisdiction codes:
  LOCAL  — the machine itself or the private network (no data leaves)
  CH     — operated in Switzerland, under Swiss jurisdiction
  EU     — operated in the European Union / EEA
  US     — operated by a US company (CLOUD Act applies, whatever the region)
  CN, CA — other foreign jurisdictions
  GLOBAL — anycast CDN, location not controllable by the deployer
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass

REGISTRY_VERSION = "2026.10.16"


@dataclass(frozen=True)
class Host:
    suffix: str
    operator: str
    jurisdiction: str
    category: str  # llm-closed, llm-open, analytics, telemetry, cdn, fonts, tunnel, storage, hosting, auth, swiss-infra, docs
    carries_content: bool = False  # does user content (prompts, documents) travel there?


_H = Host
HOSTS: tuple[Host, ...] = (
    # --- Closed-model LLM APIs -------------------------------------------
    _H("api.openai.com", "OpenAI", "US", "llm-closed", True),
    _H("openai.azure.com", "Microsoft Azure OpenAI", "US", "llm-closed", True),
    _H("api.anthropic.com", "Anthropic", "US", "llm-closed", True),
    _H("generativelanguage.googleapis.com", "Google Gemini", "US", "llm-closed", True),
    _H("aiplatform.googleapis.com", "Google Vertex AI", "US", "llm-closed", True),
    _H("api.x.ai", "xAI", "US", "llm-closed", True),
    _H("api.perplexity.ai", "Perplexity", "US", "llm-closed", True),
    _H("api.cohere.ai", "Cohere", "CA", "llm-closed", True),
    _H("api.cohere.com", "Cohere", "CA", "llm-closed", True),
    _H("api.deepseek.com", "DeepSeek", "CN", "llm-closed", True),
    _H("dashscope.aliyuncs.com", "Alibaba Cloud", "CN", "llm-closed", True),
    _H("bedrock-runtime", "Amazon Bedrock", "US", "llm-closed", True),
    _H("api.mistral.ai", "Mistral AI", "EU", "llm-closed", True),
    # --- Hosted inference for open-weight models (foreign) ---------------
    _H("api-inference.huggingface.co", "Hugging Face Inference", "US", "llm-open", True),
    _H("router.huggingface.co", "Hugging Face Inference Providers", "US", "llm-open", True),
    _H("inference.huggingface.co", "Hugging Face Inference", "US", "llm-open", True),
    _H("endpoints.huggingface.cloud", "Hugging Face Endpoints", "US", "llm-open", True),
    _H("api.together.xyz", "Together AI", "US", "llm-open", True),
    _H("api.groq.com", "Groq", "US", "llm-open", True),
    _H("api.fireworks.ai", "Fireworks AI", "US", "llm-open", True),
    _H("openrouter.ai", "OpenRouter", "US", "llm-open", True),
    _H("api.replicate.com", "Replicate", "US", "llm-open", True),
    _H("api.deepinfra.com", "DeepInfra", "US", "llm-open", True),
    _H("hf.space", "Hugging Face Spaces", "US", "llm-open", True),
    # --- Swiss infrastructure ---------------------------------------------
    _H("cscs.ch", "CSCS (Swiss National Supercomputing Centre)", "CH", "swiss-infra", True),
    _H("swissai.cscs.ch", "Swiss AI Initiative (CSCS)", "CH", "swiss-infra", True),
    _H("infomaniak.com", "Infomaniak", "CH", "swiss-infra", True),
    _H("infomaniak.ch", "Infomaniak", "CH", "swiss-infra", True),
    _H("exoscale.com", "Exoscale", "CH", "swiss-infra", True),
    _H("swisscom.com", "Swisscom", "CH", "swiss-infra", True),
    _H("swisscom.ch", "Swisscom", "CH", "swiss-infra", True),
    _H("phoeniqs.com", "Phoeniqs", "CH", "swiss-infra", True),
    _H("admin.ch", "Swiss Confederation", "CH", "swiss-infra", False),
    _H("ethz.ch", "ETH Zurich", "CH", "swiss-infra", False),
    _H("epfl.ch", "EPFL", "CH", "swiss-infra", False),
    # --- Analytics & tracking --------------------------------------------
    _H("google-analytics.com", "Google Analytics", "US", "analytics"),
    _H("analytics.google.com", "Google Analytics", "US", "analytics"),
    _H("googletagmanager.com", "Google Tag Manager", "US", "analytics"),
    _H("doubleclick.net", "Google Ads", "US", "analytics"),
    _H("segment.io", "Segment (Twilio)", "US", "analytics"),
    _H("segment.com", "Segment (Twilio)", "US", "analytics"),
    _H("mixpanel.com", "Mixpanel", "US", "analytics"),
    _H("amplitude.com", "Amplitude", "US", "analytics"),
    _H("eu.posthog.com", "PostHog (EU cloud)", "EU", "analytics"),
    _H("eu.i.posthog.com", "PostHog (EU cloud)", "EU", "analytics"),
    _H("posthog.com", "PostHog", "US", "analytics"),
    _H("plausible.io", "Plausible", "EU", "analytics"),
    _H("hotjar.com", "Hotjar", "EU", "analytics"),
    _H("clarity.ms", "Microsoft Clarity", "US", "analytics"),
    _H("vercel-insights.com", "Vercel Analytics", "US", "analytics"),
    _H("va.vercel-scripts.com", "Vercel Analytics", "US", "analytics"),
    _H("cloudflareinsights.com", "Cloudflare Web Analytics", "US", "analytics"),
    _H("api.gradio.app", "Gradio usage analytics", "US", "telemetry"),
    _H("usage.vllm.ai", "vLLM usage stats", "US", "telemetry"),
    _H("data.streamlit.io", "Streamlit usage stats", "US", "telemetry"),
    # --- Error tracking, observability, LLM ops ---------------------------
    _H("de.sentry.io", "Sentry (EU region)", "EU", "telemetry", True),
    _H("sentry.io", "Sentry", "US", "telemetry", True),
    _H("datadoghq.eu", "Datadog (EU)", "EU", "telemetry", True),
    _H("datadoghq.com", "Datadog", "US", "telemetry", True),
    _H("smith.langchain.com", "LangSmith", "US", "telemetry", True),
    _H("api.wandb.ai", "Weights & Biases", "US", "telemetry", True),
    _H("cloud.langfuse.com", "Langfuse Cloud (EU)", "EU", "telemetry", True),
    _H("us.cloud.langfuse.com", "Langfuse Cloud (US)", "US", "telemetry", True),
    _H("api.honeycomb.io", "Honeycomb", "US", "telemetry", True),
    # --- CDNs and fonts ----------------------------------------------------
    _H("fonts.googleapis.com", "Google Fonts", "US", "fonts"),
    _H("fonts.gstatic.com", "Google Fonts", "US", "fonts"),
    _H("ajax.googleapis.com", "Google Hosted Libraries", "US", "cdn"),
    _H("cdn.jsdelivr.net", "jsDelivr", "GLOBAL", "cdn"),
    _H("unpkg.com", "unpkg", "GLOBAL", "cdn"),
    _H("cdnjs.cloudflare.com", "cdnjs (Cloudflare)", "US", "cdn"),
    _H("code.jquery.com", "jQuery CDN", "US", "cdn"),
    _H("cdn.tailwindcss.com", "Tailwind Play CDN", "US", "cdn"),
    _H("kit.fontawesome.com", "Font Awesome", "US", "cdn"),
    _H("use.fontawesome.com", "Font Awesome", "US", "cdn"),
    _H("esm.sh", "esm.sh", "GLOBAL", "cdn"),
    _H("cdn.skypack.dev", "Skypack", "GLOBAL", "cdn"),
    # --- Tunnels (expose a local app through a foreign relay) --------------
    _H("gradio.live", "Gradio share links", "US", "tunnel", True),
    _H("ngrok.io", "ngrok", "US", "tunnel", True),
    _H("ngrok-free.app", "ngrok", "US", "tunnel", True),
    _H("ngrok.app", "ngrok", "US", "tunnel", True),
    _H("trycloudflare.com", "Cloudflare Tunnel", "US", "tunnel", True),
    _H("loca.lt", "localtunnel", "US", "tunnel", True),
    # --- Storage, databases, hosting ---------------------------------------
    _H("amazonaws.com", "Amazon Web Services", "US", "storage", True),
    _H("storage.googleapis.com", "Google Cloud Storage", "US", "storage", True),
    _H("firebaseio.com", "Google Firebase", "US", "storage", True),
    _H("firestore.googleapis.com", "Google Firestore", "US", "storage", True),
    _H("blob.core.windows.net", "Microsoft Azure Storage", "US", "storage", True),
    _H("supabase.co", "Supabase", "US", "storage", True),
    _H("pinecone.io", "Pinecone", "US", "storage", True),
    _H("mongodb.net", "MongoDB Atlas", "US", "storage", True),
    _H("vercel.app", "Vercel", "US", "hosting", True),
    _H("netlify.app", "Netlify", "US", "hosting", True),
    _H("herokuapp.com", "Heroku (Salesforce)", "US", "hosting", True),
    # --- Auth ----------------------------------------------------------------
    _H("auth0.com", "Auth0 (Okta)", "US", "auth", True),
    _H("clerk.com", "Clerk", "US", "auth", True),
    _H("accounts.google.com", "Google Sign-In", "US", "auth", True),
    # --- Model hub (downloads, not content) ---------------------------------
    _H("huggingface.co", "Hugging Face Hub", "US", "model-hub"),
    _H("hf.co", "Hugging Face Hub", "US", "model-hub"),
    _H("ollama.com", "Ollama registry", "US", "model-hub"),
    # --- Documentation / code hosting (references, rarely runtime) ----------
    _H("github.com", "GitHub (Microsoft)", "US", "docs"),
    _H("githubusercontent.com", "GitHub (Microsoft)", "US", "docs"),
    _H("pypi.org", "Python Package Index", "US", "docs"),
    _H("npmjs.org", "npm registry", "US", "docs"),
    _H("npmjs.com", "npm registry", "US", "docs"),
    _H("docker.io", "Docker Hub", "US", "docs"),
    _H("docker.com", "Docker Hub", "US", "docs"),
    _H("devpost.com", "Devpost", "US", "docs"),
    _H("wikipedia.org", "Wikipedia", "US", "docs"),
    _H("example.com", "IANA example domain", "LOCAL", "docs"),
    _H("docs.streamlit.io", "Streamlit documentation", "US", "docs"),
    _H("discuss.streamlit.io", "Streamlit forum", "US", "docs"),
    _H("gradio.app", "Gradio website", "US", "docs"),
    _H("vite.dev", "Vite documentation", "GLOBAL", "docs"),
    _H("vuejs.org", "Vue documentation", "GLOBAL", "docs"),
    _H("json.schemastore.org", "JSON Schema Store", "GLOBAL", "docs"),
    _H("aclanthology.org", "ACL Anthology", "GLOBAL", "docs"),
    _H("arxiv.org", "arXiv", "US", "docs"),
    _H("upload.wikimedia.org", "Wikimedia Commons (media)", "US", "cdn"),
    _H("via.placeholder.com", "Placeholder image service", "US", "cdn"),
    _H("api.publicai.co", "Public AI Inference Utility (operator jurisdiction not verified)", "UNKNOWN", "llm-open", True),
    _H("example.org", "IANA example domain", "LOCAL", "docs"),
    _H("w3.org", "W3C", "GLOBAL", "docs"),
    _H("schema.org", "schema.org", "GLOBAL", "docs"),
)

# Hosts whose names are placeholders, loopback or private service names.
_LOCAL_NAMES = {"localhost", "host.docker.internal", "0.0.0.0", "::1", "[::1]"}

FOREIGN = {"US", "EU", "CN", "CA", "GLOBAL", "UNKNOWN"}


def _is_private_ip(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified


def classify(host: str) -> Host:
    """Return the registry entry for a host name (never touches the network)."""
    h = host.lower().strip().rstrip(".")
    h = re.sub(r":\d+$", "", h)
    if h in _LOCAL_NAMES or _is_private_ip(h) or "." not in h:
        # bare names like "apertus" or "llm" are Docker/K8s service names
        return Host(h, "Local machine or private network", "LOCAL", "local")
    if h.endswith(".local") or h.endswith(".internal") or h.endswith(".lan"):
        return Host(h, "Private network", "LOCAL", "local")
    best: Host | None = None
    for entry in HOSTS:
        s = entry.suffix
        if h == s or h.endswith("." + s) or (s == "bedrock-runtime" and h.startswith("bedrock-runtime")):
            if best is None or len(s) > len(best.suffix):
                best = entry
    if best:
        return best
    if h.endswith(".ch") or h.endswith(".swiss"):
        return Host(h, "Swiss domain (TLD heuristic — operator not verified)", "CH", "swiss-tld", True)
    return Host(h, "Unknown operator", "UNKNOWN", "unknown", True)


def is_foreign(jurisdiction: str) -> bool:
    return jurisdiction in FOREIGN
