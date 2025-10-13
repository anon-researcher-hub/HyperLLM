# Hypergraph Generator Configuration Guide

## Environment Setup

### Required Environment Variables

Before running any generator script, you **MUST** set the following environment variable:

```bash
# For Linux/Mac
export OPENAI_BASE_URL="https://api.openai.com/v1"

# For Windows PowerShell
$env:OPENAI_BASE_URL="https://api.openai.com/v1"

# For Windows CMD
set OPENAI_BASE_URL=https://api.openai.com/v1
```

Replace `https://api.openai.com/v1` with your actual API endpoint URL.

**Important**: The code will raise an error if this environment variable is not set, preventing accidental exposure of your API endpoint.

## Required Parameters

All generator scripts now **require** explicit parameters. No default values are provided to ensure you configure each run appropriately.

### LLM_Iterative_Hypergraph.py

Required arguments:
- `--personas`: Individual data JSON file path
- `--output`: Hypergraph output file
- `--groups`: Number of hyperedges to generate
- `--max_members`: Maximum members per hyperedge
- `--model`: LLM model (choices: gpt-3.5-turbo, claude-3-sonnet, gpt-4-turbo)

Example:
```bash
python LLM_Iterative_Hypergraph.py \
  --personas personas1000.json \
  --output output/hypergraph.txt \
  --groups 50 \
  --max_members 5 \
  --model gpt-3.5-turbo
```

### LLM_Global_Hypergraph.py & LLM_Independent_Hypergraph.py

Required arguments:
- `--name`: Dataset name
- `--num_nodes`: Total number of nodes
- `--k`: Number of hyperedges per new node
- `--randomness`: Randomness factor
- `--version`: Correlation type
- `--model`: AI model (choices: gpt-4-turbo, gpt-3.5-turbo, claude-3-opus, claude-3-sonnet)
- `--type`: Hypergraph type (choices: social, chemical, research, default)
- `--size_distribution_directory`: Directory for size distribution file
- `--simplex_per_node_directory`: Directory for simplex per node distribution file
- `--file_name`: Output file name
- `--output_directory`: Output directory

Example:
```bash
python LLM_Global_Hypergraph.py \
  --name my_dataset \
  --num_nodes 100 \
  --k 3 \
  --randomness 0.5 \
  --version non-correlated \
  --model gpt-3.5-turbo \
  --type social \
  --size_distribution_directory size_dist \
  --simplex_per_node_directory simplex_dist \
  --file_name output_graph \
  --output_directory output
```

## Security Notes

1. **Never commit** your API key (`api-key.txt`) to version control
2. **Never hardcode** your API base URL in the code
3. Use environment variables for all sensitive configuration
4. Each script will fail immediately if required configuration is missing

## Troubleshooting

### Error: "PLEASE_SET_YOUR_BASE_URL"
- Set the `OPENAI_BASE_URL` environment variable before running
- Or modify `BASE_URL_OPENAI` directly in the code (not recommended)

### Error: Missing required argument
- Check that you've provided all required command-line arguments
- Use `--help` flag to see all required parameters


