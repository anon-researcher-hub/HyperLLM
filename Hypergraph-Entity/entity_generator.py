"""
Entity generator for labeled nodes used by hypergraph construction.

Modes:
- personas: generate from US statistics (no LLM). Reuses existing personas JSON structure.
- drug/reactant/ecommerce/general: call LLM to synthesize structured entities per template.

Outputs JSON dict keyed by string IDs: {"0": {...}, "1": {...}}
"""

import os
import json
import argparse
from typing import Dict, Any, List
from openai import OpenAI
import random


def load_api_key(api_key_file: str) -> str:
    """Read first non-empty API Key line, avoid multi-line illegal header errors"""
    candidate_paths = [
        api_key_file,
        os.path.join('Hypergraph-Generator', api_key_file),
        os.path.join(os.path.dirname(__file__), '..', api_key_file),
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        return line
    raise FileNotFoundError(f'API key file not found: {api_key_file}')


def load_personas(personas_path: str) -> Dict[str, Any]:
    with open(personas_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def call_llm(client: OpenAI, model: str, system_prompt: str, user_prompt: str, max_tokens: int = 800, temperature: float = 0.7) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content


def ensure_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    # try direct parse
    try:
        return json.loads(text)
    except Exception:
        # attempt to extract code block
        if '```' in text:
            parts = text.split('```')
            for part in parts:
                part = part.strip()
                if part.startswith('{') and part.endswith('}'):
                    return json.loads(part)
        # best-effort: trim to first '{' and last '}'
        if '{' in text and '}' in text:
            try:
                s = text[text.find('{'): text.rfind('}')+1]
                return json.loads(s)
            except Exception:
                pass
        raise ValueError('LLM did not return valid JSON')


TEMPLATES: Dict[str, Dict[str, Any]] = {
    "drug": {
        "system": "You are a pharmacology data expert. Produce realistic drug entity profiles in strict JSON.",
        "fields": ["drug_name", "chemical_class", "primary_use", "mechanism_of_action", "common_side_effects", "abuse_category"],
        "batch_fmt": (
            "Generate {n} realistic drug profiles. Return a JSON object mapping string IDs to objects with fields: "
            "drug_name, chemical_class, primary_use, mechanism_of_action, common_side_effects (list of 2-5)."
        ),
    },
    "reactant": {
        "system": "You are a biochemistry expert. Produce biological reactant profiles in strict JSON.",
        "fields": ["reactant_name", "reactant_type", "cellular_location", "key_pathways"],
        "batch_fmt": (
            "Generate {n} biological reactant profiles (metabolites or proteins). Return JSON id->object with: "
            "reactant_name, reactant_type, cellular_location, key_pathways (list of 1-3)."
        ),
    },
    "ecommerce": {
        "system": "You are an e-commerce data specialist. Produce heterogeneous profiles in strict JSON.",
        "fields": ["user_profile", "item_profile", "brand_profile", "category_profile"],
        "batch_fmt": (
            "Generate {n} entities as a JSON id->object. Each object contains: "
            "user_profile: {user_id, interests: [2-3]}, item_profile: {item_name, price_range}, "
            "brand_profile: {brand_name}, category_profile: {category_name}."
        ),
    },
    "general": {
        "system": "You are a data synthesizer. Produce coherent entities in strict JSON.",
        "fields": ["name", "attributes"],
        "batch_fmt": (
            "Generate {n} general-purpose entities. Return JSON id->object with fields: name (string), attributes (object of 3-6 key: value)."
        ),
    },
}


def build_single_prompt(entity_type: str) -> str:
    if entity_type == 'drug':
        return (
            "Generate exactly ONE drug profile in strict JSON with keys: "
            "drug_name (string), chemical_class (string), primary_use (string), "
            "mechanism_of_action (string), common_side_effects (array of 2-5 short strings), "
            "abuse_category (string).\n"
            "Guidelines:\n"
            "- Vary drug_name across pharmacological classes (e.g., opioids, stimulants, benzodiazepines, cannabinoids, hallucinogens, antibiotics, antihypertensives, antidiabetics, statins).\n"
            "- If applicable, set abuse_category to one of: opioid, stimulant, benzodiazepine, cannabinoid, hallucinogen, sedative, inhalant, dissociative, none.\n"
            "- Ensure internal consistency between class and mechanism_of_action.\n"
            "- Avoid duplicates; prefer diverse, real-world plausible entries (brand or generic).\n"
            "Return ONLY the JSON object. No code fences, no explanations."
        )
    if entity_type == 'reactant':
        return (
            "Generate exactly ONE biological reactant profile as a JSON object with keys: "
            "reactant_name (string), reactant_type (string), cellular_location (string), key_pathways (array of 1-3 short strings).\n"
            "Return ONLY the JSON object. No code fences, no explanations."
        )
    if entity_type == 'ecommerce':
        return (
            "Generate exactly ONE e-commerce heterogeneous entity as a JSON object with keys: "
            "user_profile (object: user_id string, interests array of 2-3 short strings), "
            "item_profile (object: item_name string, price_range string), "
            "brand_profile (object: brand_name string), "
            "category_profile (object: category_name string).\n"
            "Return ONLY the JSON object. No code fences, no explanations."
        )
    # general
    return (
        "Generate exactly ONE general-purpose entity as a JSON object with keys: "
        "name (string), attributes (object with 3-6 key:value pairs of short strings).\n"
        "Return ONLY the JSON object. No code fences, no explanations."
    )


def prompt_until_json(client: OpenAI, model: str, system_prompt: str, user_prompt: str, retries: int = 3) -> Dict[str, Any]:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            text = call_llm(client, model, system_prompt, user_prompt, max_tokens=400, temperature=0.7)
            return ensure_json(text)
        except Exception as e:
            last_err = e
    raise last_err


def generate_entities(entity_type: str, n: int, model: str, api_key_file: str, base_url: str, personas_path: str = None) -> Dict[str, Any]:
    if entity_type == 'personas':
        if not personas_path:
            raise ValueError('personas_path is required when entity_type=personas')
        return load_personas(personas_path)

    if entity_type not in TEMPLATES:
        raise ValueError(f'Unsupported entity_type: {entity_type}')

    api_key = load_api_key(api_key_file)
    client = OpenAI(api_key=api_key, base_url=base_url)

    tpl = TEMPLATES[entity_type]
    system_prompt = tpl['system']
    single_prompt = build_single_prompt(entity_type)

    out: Dict[str, Any] = {}
    seen_names = set()
    for i in range(n):
        try:
            obj = prompt_until_json(client, model, system_prompt, single_prompt, retries=3)
            key_for_dup = None
            if entity_type == 'drug':
                key_for_dup = str(obj.get('drug_name', '')).strip().lower()
                if key_for_dup and key_for_dup in seen_names:
                    obj['drug_name'] = f"{obj.get('drug_name','')} ({random.choice(['ER','XR','SR','Generic','Alt'])})"
                if key_for_dup:
                    seen_names.add(key_for_dup)
            out[str(i)] = obj
            print(f"[{i+1}/{n}] ✅ Generated successfully")
        except Exception as e:
            print(f"[{i+1}/{n}] ❌ Generation failed: {e}. Using last successful object as placeholder")
            if out:
                out[str(i)] = json.loads(json.dumps(list(out.values())[-1]))
            else:
                out[str(i)] = {}
    return out


def main():
    parser = argparse.ArgumentParser(description='Generate labeled entities for hypergraph nodes')
    parser.add_argument('--entity_type', type=str, required=True, help='personas | drug | reactant | ecommerce | general')
    parser.add_argument('--n', type=int, default=1000, help='number of entities to generate')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo', help='LLM model used when entity_type != personas')
    parser.add_argument('--api_key_file', type=str, default='api-key.txt', help='API key file')
    parser.add_argument('--base_url', type=str, default='https://api.aigc369.com/v1', help='OpenAI-compatible base url')
    parser.add_argument('--personas_path', type=str, default='Hypergraph-Generator/personas1000.json', help='path to personas json when entity_type=personas')
    parser.add_argument('--output', type=str, default='entities.json', help='output json path')
    args = parser.parse_args()

    data = generate_entities(args.entity_type, args.n, args.model, args.api_key_file, args.base_url, args.personas_path)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f'[OK] Saved {len(data)} entities to {args.output}')


if __name__ == '__main__':
    main()

