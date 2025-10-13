import openai
import json
import argparse
import os
import random

# Load OpenAI API Key
def load_api_keys(filename="api-key.txt"):
    """Load OpenAI API Key"""
    with open(filename, "r") as f:
        lines = f.readlines()
    openai_key = lines[0].strip()
    return openai_key

openai_key = load_api_keys("api-key.txt")

# Setup OpenAI client
# IMPORTANT: Replace with your own API base URL
# Example: "https://api.openai.com/v1" or your custom endpoint
BASE_URL_OPENAI = os.environ.get("OPENAI_BASE_URL", "PLEASE_SET_YOUR_BASE_URL")

if BASE_URL_OPENAI == "PLEASE_SET_YOUR_BASE_URL":
    raise ValueError(
        "Please set OPENAI_BASE_URL environment variable or modify BASE_URL_OPENAI in the code.\n"
        "Example: export OPENAI_BASE_URL='https://api.openai.com/v1'"
    )

client = openai.OpenAI(api_key=openai_key, base_url=BASE_URL_OPENAI)


class LLMIterativeLocalHypergraph:
    def __init__(self, personas_file, output_file, num_groups=50, max_members_per_group=5, model="gpt-3.5-turbo"):
        """
        Iterative Local Method hypergraph generator
        :param personas_file: Personal data JSON file path
        :param output_file: Generated hypergraph storage path
        :param num_groups: Number of hyperedges to generate
        :param max_members_per_group: Maximum members per hyperedge
        :param model: Selected LLM model
        """
        self.personas_file = personas_file
        self.output_file = output_file
        self.num_groups = num_groups
        self.max_members_per_group = max_members_per_group
        self.model = model
        self.personas = self.load_personas()
        self.hyperedges = []

    def load_personas(self):
        """Load personas.json file"""
        with open(self.personas_file, "r") as f:
            data = json.load(f)
        return data

    def generate_hyperedge_with_llm(self, person_id, person_data):
        """
        Have LLM generate collaborators for this individual based on existing network info
        """
        existing_edges_text = "\n".join([" ".join(edge) for edge in self.hyperedges[-5:]])

        prompt = f"""
        You are a hypergraph generator. Your task is to create a collaboration group for an individual.

        Current network structure (partial hyperedges):
        {existing_edges_text}

        Individual's information:
        - ID: {person_id}
        - Gender: {person_data['gender']}
        - Race/Ethnicity: {person_data['race/ethnicity']}
        - Age: {person_data['age']}
        - Religion: {person_data['religion']}
        - Political Affiliation: {person_data['political affiliation']}

        Task:
        1. Refer to existing hyperedge structure, strengthen existing connections but avoid complete duplication.
        2. Select {random.randint(2, self.max_members_per_group - 1)} collaborators.
        3. Selected individuals may share common features (gender, race, religion, politics, etc.) with this individual.
        4. Appropriately introduce diversity to make the hypergraph more realistic.

        Output format:
        Output only selected individual IDs, space-separated, e.g.:
        "3 7 15 19"

        Note:
        - Output only IDs, no additional text.
        - Do not include own ID ({person_id}).
        """

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a hypergraph generator"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.7,
            )

            output = response.choices[0].message.content.strip()
            selected_ids = output.split()
            selected_ids = [pid for pid in selected_ids if pid in self.personas and pid != person_id]

            return [person_id] + selected_ids

        except openai.OpenAIError as e:
            print(f"OpenAI API call failed: {e}")
            return [person_id]

    def generate_hyperedges(self):
        """
        Iteratively generate hyperedges, each new individual refers to partial existing network structure
        """
        all_persons = list(self.personas.keys())

        for _ in range(self.num_groups):
            main_person = random.choice(all_persons)
            main_person_data = self.personas[main_person]

            selected_members = self.generate_hyperedge_with_llm(main_person, main_person_data)
            self.hyperedges.append(selected_members)

        return self.hyperedges

    def save_hypergraph(self):
        """
        Save hypergraph to file
        """
        output_dir = os.path.dirname(self.output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(self.output_file, "w") as f:
            for edge in self.hyperedges:
                f.write(" ".join(map(str, edge)) + "\n")
        print(f"✅ Hypergraph successfully saved to {self.output_file}")

    def run(self):
        """
        Run hypergraph generation
        """
        print("📌 Using LLM for **Iterative Local Method** hypergraph generation...")
        self.generate_hyperedges()
        self.save_hypergraph()
        print(f"✅ Generated {len(self.hyperedges)} hyperedges")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Iterative Local Hypergraph Generator")
    parser.add_argument("--personas", type=str, required=True, help="Individual data JSON file path")
    parser.add_argument("--output", type=str, required=True, help="Hypergraph output file")
    parser.add_argument("--groups", type=int, required=True, help="Number of hyperedges to generate")
    parser.add_argument("--max_members", type=int, required=True, help="Maximum members per hyperedge")
    parser.add_argument("--model", type=str, required=True, 
                        choices=['gpt-3.5-turbo', 'claude-3-sonnet', 'gpt-4-turbo'],
                        help="Select LLM model to use")

    args = parser.parse_args()

    generator = LLMIterativeLocalHypergraph(
        personas_file=args.personas,
        output_file=args.output,
        num_groups=args.groups,
        max_members_per_group=args.max_members,
        model=args.model
    )

    generator.run()
