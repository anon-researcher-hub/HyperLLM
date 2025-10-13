import openai
import argparse
import os


# API Key
def load_api_keys(filename="api-key.txt"):
    """Load OpenAI API Key"""
    with open(filename, "r") as f:
        lines = f.readlines()
    openai_key = lines[0].strip()
    return openai_key


# Load API Key
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

# Create OpenAI client
client = openai.OpenAI(api_key=openai_key, base_url=BASE_URL_OPENAI)


class HyperGraphGenerator:

    def __init__(self, args):
        self.name = args.name
        self.num_nodes = args.num_nodes
        self.k = args.k
        self.randomness = args.randomness
        self.version = args.version
        self.type = args.type
        self.model = args.model
        self.size_distribution_directory = args.size_distribution_directory
        self.simplex_per_node_directory = args.simplex_per_node_directory
        self.file_name = args.file_name
        self.output_directory = args.output_directory

    def create_prompt(self):
        """Generate different prompts based on hypergraph type"""
        base_prompt = f"""You are a hypergraph generator. Generate a hypergraph that satisfies the following properties:
    1. The hypergraph contains exactly {self.num_nodes} nodes, numbered from 1 to {self.num_nodes}.
    2. Each new node forms {self.k} hyperedges, following the preferential attachment rule.
    3. The randomness factor ({self.randomness}) controls the deviation from preferential attachment.
    4. The output must be a list of hyperedges, one per line, formatted as follows:
    5. 10. No additional text, explanation, or formatting is needed—only the list of hyperedges. The hyperedges should be formatted as follows:
   - Example:

    1 2
    3 4 5
    6 7 8
    9 10
    11 12 13 19
    14 15
    16 17
    14 15 18
    15 17 19 20
    """

        if self.type == "social":
            return base_prompt + """5. The size of each hyperedge varies, with small hyperedges (size 2-8) being frequent and larger hyperedges (size 5-20) appearing occasionally.
    6. No additional text, explanation, or formatting is needed—only the list of hyperedges.
    """
        elif self.type == "chemical":
            return base_prompt + """5. Each hyperedge represents a chemical reaction, with small hyperedges (size 2 or 5) being common for simple reactions and larger hyperedges (size 4-7) for complex reactions.
    6. No additional text, explanation, or formatting is needed—only the list of hyperedges.
    """
        elif self.type == "research":
            return base_prompt + """5. Each hyperedge represents a collaboration between researchers, with small hyperedges (size 2 or 4) being common for individual collaborations and larger hyperedges (size 4-7) for group projects.
    6. No additional text, explanation, or formatting is needed—only the list of hyperedges.
    """
        else:
            return base_prompt + """The size of each hyperedge varies to reflect real-world hypernetworks.
    6. No additional text, explanation, or formatting is needed—only the list of hyperedges.
    """

    def generate_hypergraph(self):
        """Generate hypergraph using selected large model"""
        prompt = self.create_prompt()

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a hypergraph generator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4096,
                temperature=0.7,
            )

            hypergraph_data = response.choices[0].message.content
            return hypergraph_data

        except openai.OpenAIError as e:
            print(f"OpenAI API call failed: {e}")
            return None

    def save_hypergraph(self, hypergraph_data):
        """Save hypergraph data to specified file"""
        if not hypergraph_data:
            print("Hypergraph generation failed, no data to save.")
            return

        output_path = os.path.join(self.output_directory, f"{self.file_name}.txt")
        os.makedirs(self.output_directory, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(hypergraph_data)

        print(f"Hypergraph successfully saved at {output_path}")


def arg_parse():
    """Command line parameter parsing"""
    parser = argparse.ArgumentParser(description="Hypergraph Generator Parameters")

    parser.add_argument('--name', dest='name', required=True, help='Dataset name')
    parser.add_argument('--num_nodes', dest='num_nodes', type=int, required=True, help='Total number of nodes')
    parser.add_argument('--k', dest='k', type=int, required=True, help='Number of hyperedges per new node')
    parser.add_argument('--randomness', dest='randomness', type=float, required=True, help='Randomness factor')
    parser.add_argument('--version', dest='version', required=True, help='Correlation type')
    parser.add_argument('--model', dest='model', required=True,
                       choices=['gpt-4-turbo', 'gpt-3.5-turbo', 'claude-3-opus', 'claude-3-sonnet'],
                       help='Choose the AI model to use')
    parser.add_argument('--type', dest='type', required=True,
                       choices=['social', 'chemical', 'research', 'default'],
                       help='Type of hypergraph to generate')
    parser.add_argument('--size_distribution_directory', dest='size_distribution_directory',
                       required=True, help='Directory for size distribution file')
    parser.add_argument('--simplex_per_node_directory', dest='simplex_per_node_directory',
                       required=True, help='Directory for simplex per node distribution file')
    parser.add_argument('--file_name', dest='file_name', required=True, help='Output file name')
    parser.add_argument('--output_directory', dest='output_directory', required=True, help='Output directory')

    return parser.parse_args()


def main():
    """Main function: initialize generator and generate hypergraph"""
    args = arg_parse()
    generator = HyperGraphGenerator(args)
    hypergraph_data = generator.generate_hypergraph()
    generator.save_hypergraph(hypergraph_data)
    print(f"Hypergraph generation completed: {args.file_name}")


if __name__ == '__main__':
    main()

