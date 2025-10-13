# HyperLLM: Large Language Model-based Hypergraph Generation

HyperLLM is a novel framework for generating dynamic, attributed hypergraphs using Large Language Models (LLMs). It pioneers a Multi-Agent System (MAS) approach where different agents, powered by LLMs, collaborate to construct, evolve, and optimize hypergraphs that are both structurally sound and semantically coherent.

## Key Advantages

### 1. High Structural and Semantic Consistency
A significant challenge in graph machine learning is the scarcity of high-quality, labeled hypergraph datasets. HyperLLM addresses this by generating hypergraphs where nodes (entities) are endowed with rich semantic information (personas). The generation process ensures that the relationships (hyperedges) are not only structurally plausible but also semantically consistent with the attributes of the nodes involved. This creates datasets that are ideal for training and evaluating models on attributed hypergraphs.

### 2. First Framework for LLM-based Hypergraph Generation and Evolution
HyperLLM is the first work to leverage the power of modern LLMs for the complex task of hypergraph generation. Beyond static generation, it introduces a dynamic evolution process, allowing the hypergraph to change over time in a realistic manner, mimicking the behavior of real-world networks.

### 3. Interpretable Multi-Agent Framework
The project introduces an innovative multi-agent framework where each agent has a specialized role:
- **Generator Agent**: Creates new relationships based on semantic understanding.
- **Reviewer Agent**: Audits the quality and coherence of proposed relationships.
- **Remover Agent**: Prunes redundant or irrelevant connections.
- **Optimizer Agent**: Refines the global network structure.

This modular design, combined with a threshold model for decision-making, provides a high degree of interpretability and control over the generation process.

### 4. Domain-General Applicability
While the provided code uses social networks as a primary example, the HyperLLM framework is highly versatile and domain-agnostic. It can be easily adapted to generate a wide variety of hypergraphs, including:
- **Social Networks**: Modeling group interactions and communities.
- **Tagging Networks**: Simulating how users tag items on platforms like Stack Overflow or Ask Ubuntu.
- **Email Networks**: Representing multi-recipient email communications.
- **Scientific Co-authorship Networks**: Modeling research collaborations.

## Code Structure

The repository is organized into the following directories:

-   `Hypergraph-Generator/`: Contains the core logic for the multi-agent hypergraph generation. The main entry point and configuration file is `LLM_MAS_Hypergraph_Configuration.py`.
-   `Hypergraph-Entity/`: Includes scripts for generating the node personas and attributes (e.g., `entity_generator.py`).
-   `Hypergraph-Evaluation/`: Provides scripts in both Python and MATLAB for analyzing and evaluating the structural and semantic properties of the generated hypergraphs.
-   `Hypergraph-Ablation_Study/`: Contains code for various ablation experiments to test the contribution of each component of the MAS framework.
-   `Hypergraph-Datasets/`: Includes sample real-world hypergraph datasets that can be used as a reference for the generation process.
-   `Hypergraph-Result/`: Directory for storing output results.

## How to Use

### 1. Installation
Install the required Python packages:
```bash
pip install -r Hypergraph-Generator/requirements.txt
```

### 2. Configuration

**API Key and Base URL:**
-   Place your OpenAI API key in `Hypergraph-Generator/api-key.txt`.
-   **IMPORTANT**: The API base URL is not hardcoded. You must either set it as an environment variable or modify the source code directly.

    **Option 1: Environment Variable (Recommended)**
    ```bash
    export OPENAI_BASE_URL='https://api.openai.com/v1' 
    ```
    Replace the URL with your custom endpoint if needed.

    **Option 2: Edit the Code**
    In files like `LLM_MAS_Hypergraph_Configuration.py`, find the `BASE_URL_OPENAI` variable and replace the placeholder with your URL.

### 3. Running the Generator

The main generation script is `LLM_MAS_Hypergraph_Configuration.py`. It requires several command-line arguments to run, as all parameters must be set explicitly.

**Example Command:**
```bash
python Hypergraph-Generator/LLM_MAS_Hypergraph_Configuration.py \
    --personas Hypergraph-Generator/personas_10k.json \
    --config Hypergraph-Datasets/coauth-Geology-unique-hyperedges.txt \
    --output Hypergraph-Result/generated_hypergraph.txt \
    --groups_per_iter 10 \
    --max_members 8 \
    --iterations 50 \
    --model gpt-4-turbo
```

**Required Arguments:**
-   `--personas`: Path to the JSON file containing node personas.
-   `--config`: Path to a reference hypergraph dataset, which is used to model the desired hyperedge size distribution.
-   `--output`: Path for the final output file or directory.
-   `--groups_per_iter`: Number of hyperedges to attempt to generate in each iteration.
-   `--max_members`: The maximum number of members allowed in a single hyperedge.
-   `--iterations`: The number of evolution iterations to run.
-   `--model`: The specific LLM to use for the agents (e.g.,`claude-3-sonnet`).

### 4. Resuming a Run
If a generation process is interrupted, you can resume it from the last saved checkpoint by using the `--resume` flag and pointing it to the protected run directory created during the initial run.

```bash
python Hypergraph-Generator/LLM_MAS_Hypergraph_Configuration.py --resume Hypergraph-Result/MAS_Config_Run_coauth-Geology-unique-hyperedges_20231013_103000
```

## Citation
If you use HyperLLM in your research, please cite our paper:
```
[Citation details will be added here once the paper is published.]
```