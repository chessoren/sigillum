.PHONY: run run-lite model offline-test test audit-self samples community clean

MODEL_URL = https://huggingface.co/Colby/apertus-v1.5-8b-text-Q4_K_M-GGUF/resolve/main/apertus-v1.5-8b-text-q4_k_m.gguf
MODEL     = models/apertus-v1.5-8b-text-q4_k_m.gguf

# Judges: `make run`. Uses LLM_BASE_URL / LLM_API_KEY / LLM_NAME when set,
# otherwise downloads Apertus v1.5 8B (GGUF, ~5 GB, build time only) and serves it locally.
run:
	@if [ -n "$$LLM_BASE_URL" ]; then \
	  echo "Sigillum -> Apertus at $$LLM_BASE_URL"; docker compose up --build sigillum; \
	else \
	  $(MAKE) model && echo "Sigillum -> local Apertus (llama.cpp)" && docker compose --profile local up --build; \
	fi

# Without any model: deterministic grades, template explanations.
run-lite:
	LLM_BASE_URL=http://127.0.0.1:9/v1 docker compose up --build sigillum

model: $(MODEL)
$(MODEL):
	mkdir -p models && curl -L --fail -o $(MODEL) $(MODEL_URL)

offline-test:
	docker compose build sigillum && docker compose --profile test run --rm offline-test

test:
	cd src && python3 -m unittest discover -s tests -v

audit-self:
	cd src && python3 -m sigillum audit .. --name sigillum

samples:
	./scripts_audit_samples.sh

community:
	python3 scripts/fetch_public_spaces.py /tmp/apertus-spaces && cd src && python3 -m sigillum community /tmp/apertus-spaces && rm -rf /tmp/apertus-spaces

clean:
	docker compose down --remove-orphans
