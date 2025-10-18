# Usage Examples | 使用示例 | 사용 예제

## Example 1: Basic Hypergraph Generation

### English

**Scenario**: Generate a hypergraph with 1000 personas using a real-world configuration

**Steps**:
1. Start the GUI: `python main.py`
2. Select language: English
3. Go to "Parameters" tab:
   - Config File: Select `Real_Hyperedges-CS.txt` from `Hypergraph-Datasets/`
   - Personas File: Select `personas1000.json` from `Hypergraph-Generator/`
   - Iterations: 10
   - Groups per iteration: 5
   - Max members: 5
   - Model: gpt-4
4. Go to "Hypergraph Modeling" tab
5. Click "Start Generation"
6. Monitor progress in real-time
7. Wait for completion
8. Find results in generated run directory

**Expected Output**:
- A new directory: `MAS_Config_Run_Real_Hyperedges-CS_YYYYMMDD_HHMMSS/`
- Final hypergraph: `final_hypergraph.txt`
- Iteration snapshots in `iteration_snapshots/`
- Checkpoints in `checkpoints/`
- Analysis data in `analysis/`

---

### 中文

**场景**: 使用真实世界配置生成包含1000个节点的超图

**步骤**:
1. 启动GUI: `python main.py`
2. 选择语言: 中文
3. 进入"参数配置"标签页:
   - 配置文件: 从 `Hypergraph-Datasets/` 选择 `Real_Hyperedges-CS.txt`
   - 节点文件: 从 `Hypergraph-Generator/` 选择 `personas1000.json`
   - 演化轮数: 10
   - 每轮超边数: 5
   - 最大成员数: 5
   - 模型: gpt-4
4. 进入"超图建模"标签页
5. 点击"开始生成"
6. 实时监控进度
7. 等待完成
8. 在生成的运行目录中查找结果

**预期输出**:
- 新目录: `MAS_Config_Run_Real_Hyperedges-CS_YYYYMMDD_HHMMSS/`
- 最终超图: `final_hypergraph.txt`
- 迭代快照位于 `iteration_snapshots/`
- 检查点位于 `checkpoints/`
- 分析数据位于 `analysis/`

---

### 한국어

**시나리오**: 실제 구성을 사용하여 1000개의 페르소나가 있는 하이퍼그래프 생성

**단계**:
1. GUI 시작: `python main.py`
2. 언어 선택: 한국어
3. "매개변수" 탭으로 이동:
   - 구성 파일: `Hypergraph-Datasets/`에서 `Real_Hyperedges-CS.txt` 선택
   - 페르소나 파일: `Hypergraph-Generator/`에서 `personas1000.json` 선택
   - 반복 횟수: 10
   - 반복당 그룹: 5
   - 최대 멤버: 5
   - 모델: gpt-4
4. "하이퍼그래프 모델링" 탭으로 이동
5. "생성 시작" 클릭
6. 실시간 진행 상황 모니터링
7. 완료 대기
8. 생성된 실행 디렉토리에서 결과 찾기

**예상 출력**:
- 새 디렉토리: `MAS_Config_Run_Real_Hyperedges-CS_YYYYMMDD_HHMMSS/`
- 최종 하이퍼그래프: `final_hypergraph.txt`
- 반복 스냅샷: `iteration_snapshots/`
- 체크포인트: `checkpoints/`
- 분석 데이터: `analysis/`

---

## Example 2: Resume Interrupted Generation

### English

**Scenario**: Your generation was interrupted and you want to continue from where it stopped

**Steps**:
1. Start the GUI
2. Go to "Parameters" tab
3. Find "Resume Directory" field
4. Click "Browse" and select the interrupted run directory
   - Look for directories starting with `MAS_Config_Run_`
   - Select the one with the timestamp of your interrupted run
5. Other parameters will be loaded automatically from the checkpoint
6. Go to "Hypergraph Modeling" tab
7. Click "Start Generation"
8. The process will resume from the last checkpoint

**Tips**:
- Check `interruption_info.json` in the run directory to see progress
- Latest checkpoint is automatically selected
- Original configuration is preserved

---

## Example 3: Generate Personas with Demographics

### English

**Scenario**: Create a new set of personas based on US demographics

**Steps**:
1. Go to "Entity Generation" tab
2. Select generation method: "Statistical (Demographics)"
3. Set number of personas: 5000
4. Click "Browse" for output file and choose location (e.g., `personas5000.json`)
5. Click "Generate Personas"
6. Wait for completion
7. Use the generated file in hypergraph generation

**Output**: A JSON file with personas having realistic demographic distributions

---

## Example 4: Evaluate Generated Hypergraph

### English

**Scenario**: Analyze the structure and properties of your generated hypergraph

**Steps**:
1. Go to "Evaluation" tab
2. Click "Browse" and select your hypergraph file (e.g., `final_hypergraph.txt`)
3. Choose evaluation type:
   - **Basic Statistics**: Quick overview (nodes, edges, avg size)
   - **Structural Counts**: Detailed structural analysis
   - **Clustering Coefficient**: Community structure analysis
   - **Spectral Similarity**: Compare with reference hypergraph
   - **Motif Analysis**: Find recurring patterns
4. Click the corresponding button
5. View results in the results panel
6. Results can be copied or saved for further analysis

**Evaluation Options**:

| Type | Purpose | Output |
|------|---------|--------|
| Basic Statistics | Overview | Node/edge counts, sizes |
| Structural Counts | Detailed structure | Various structural metrics |
| Clustering | Community detection | Clustering coefficients |
| Spectral | Similarity analysis | Spectral properties |
| Motif | Pattern discovery | Common motifs |

---

## Example 5: Custom Agent Configuration

### English

**Scenario**: Fine-tune agent behavior for specific research needs

**Steps**:
1. Go to "Parameters" tab
2. Scroll to "Agent Parameters" section
3. For each agent, adjust:
   - **Temperature**: 
     - Lower (0.1-0.3) = More deterministic, consistent
     - Higher (0.7-1.0) = More creative, diverse
   - **Max Tokens**: 
     - Increase for more detailed reasoning
     - Decrease for faster execution

**Example Configurations**:

**Conservative (High Quality)**:
- Generator: Temperature 0.3, Max Tokens 150
- Reviewer: Temperature 0.2, Max Tokens 200
- Remover: Temperature 0.3, Max Tokens 150
- Optimizer: Temperature 0.3, Max Tokens 200

**Exploratory (High Diversity)**:
- Generator: Temperature 0.9, Max Tokens 100
- Reviewer: Temperature 0.5, Max Tokens 150
- Remover: Temperature 0.6, Max Tokens 200
- Optimizer: Temperature 0.7, Max Tokens 250

---

## Example 6: Batch Processing Multiple Configurations

### English

**Scenario**: Generate multiple hypergraphs with different configurations

**Steps**:
1. Create a list of configurations:
   ```
   Config 1: personas1000.json + Real_Hyperedges-CS.txt
   Config 2: personas5000.json + Real_Hyperedges-CS.txt
   Config 3: personas1000.json + custom_hyperedges.txt
   ```

2. For each configuration:
   - Set parameters in GUI
   - Start generation
   - Wait for completion
   - Save results with descriptive names

3. Compare results using evaluation tools

**Tip**: Use different model versions (gpt-3.5-turbo, gpt-4) to compare quality vs. cost

---

## Common Workflows

### Research Workflow

```
1. Generate Personas (Entity Generation)
   ↓
2. Configure Generation (Parameters)
   ↓
3. Run Generation (Hypergraph Modeling)
   ↓
4. Monitor Progress (Real-time)
   ↓
5. Evaluate Results (Evaluation)
   ↓
6. Compare with Real Data (Spectral/Motif)
   ↓
7. Iterate with Different Configurations
```

### Production Workflow

```
1. Load Existing Personas
   ↓
2. Set Conservative Parameters
   ↓
3. Start Generation with Checkpointing
   ↓
4. (If interrupted) Resume from Checkpoint
   ↓
5. Run Basic Evaluations
   ↓
6. Export for Downstream Applications
```

### Experimentation Workflow

```
1. Generate Multiple Persona Sets
   ↓
2. Try Different Agent Configurations
   ↓
3. Compare Results
   ↓
4. Analyze Patterns
   ↓
5. Document Findings
```

---

## Tips and Best Practices

### 1. Start Small
- Begin with 100-1000 personas
- Use fewer iterations (3-5) for testing
- Verify output before scaling up

### 2. Monitor Resources
- Check memory usage during generation
- Large persona sets (10k+) may require significant RAM
- Use appropriate max_members setting

### 3. Save Frequently
- Let checkpointing system work automatically
- Don't interrupt during critical phases
- Keep run directories organized

### 4. Document Experiments
- Use descriptive output names
- Save configuration along with results
- Take notes on what works well

### 5. Validation
- Always run basic evaluations
- Compare with reference data
- Check for anomalies

### 6. Error Handling
- Check console log for errors
- Verify API key and base URL
- Ensure file paths are correct
- Test with small datasets first

---

## Troubleshooting Examples

### Problem: Generation is very slow

**Solution**:
- Use gpt-3.5-turbo instead of gpt-4
- Reduce groups_per_iteration
- Check internet connection
- Verify API rate limits

### Problem: Results don't match expected distribution

**Solution**:
- Increase iterations
- Adjust agent temperature
- Check input configuration file
- Review agent parameters

### Problem: Evaluation fails

**Solution**:
- Verify hypergraph file format
- Check if Python scripts are accessible
- Install required dependencies
- Review error messages in console

---

## Advanced Usage

### Custom Evaluation Pipeline

1. Generate hypergraph
2. Run all Python evaluations
3. Export results to JSON
4. Run MATLAB evaluations (if available)
5. Create comprehensive report
6. Compare with baseline

### Integration with External Tools

1. Export hypergraph to CSV format
2. Import into NetworkX/igraph
3. Perform custom analysis
4. Visualize with Gephi/Cytoscape
5. Return to GUI for further iterations

---

For more examples and updates, check the GitHub repository.

