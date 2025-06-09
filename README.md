# 🧑‍⚕️💬 TalkDep: Clinically Grounded LLM Personas for Conversation-Centric Depression Screening

<!-- Author list (center-aligned) -->
<div style="text-align:center; line-height:1.4; font-family:system-ui, sans-serif;">

  <!-- Authors with numbered affiliations -->
  <strong>Xi Wang</strong><sup>2</sup>, <a href="mailto:anxo.pvila@udc.es"><strong>Anxo Pérez</strong></a><sup>1</sup>, <strong>Javier Parapar</strong><sup>1</sup>, <strong>Fabio Crestani</strong><sup>3</sup>



  <!-- Affiliation list -->
  <sup>1</sup> IRLab, CITIC, Universidade da Coruña, A Coruña, Spain<br>
  <sup>2</sup> Information School, University of Sheffield, Sheffield, UK<br>
  <sup>3</sup> Faculty of Informatics, Università della Svizzera italiana (USI), Lugano, Switzerland

</div>


## 📌  Overview

This repository accompanies the paper **“Enhancing Automatic Depression Diagnosis with Language Model-Driven Simulated Patients”** and contains all code, data, and instructions needed to replicate its experiments. 

 ## Abstract
The increasing demand for mental health services has outpaced the availability of trained clinical professionals, leading to limited depression diagnosis support. This shortage has motivated the development of simulated or virtual patients to assist in training and evaluation, but existing approaches often fail to generate clinically valid, natural and diverse symptom presentations. In this work, we embrace the recent advanced language models as the backbone and propose a novel patient simulation pipeline with access to diversified patient profiles to generate simulated patients. By conditioning the model on psychiatric diagnostic criteria, symptom severity scales, and contextual factors, we aim to create authentic patient responses that can better support diagnostic model training and evaluation. We verify the reliability of these simulated patients with thorough assessments conducted by clinical professionals. The availability of validated simulated patients offers a scalable and adaptable resource for improving the robustness and generalisability of automatic depression diagnosis systems. 

## 📁 Repository Structure

```text
.
├── llm-personas-information/       # Conversation logs, prompts, golden‑truth ranking
│   └── conversation-logs/   # Conversation logs
│   └── Form-Simulation_Evaluation_of_LLM_Personas.pdf   # Form with the evaluation of LLM personas given to clinicians
│   └── golden_truth_BDI_depression_ranking.txt   # Golden truth depression ranking the LLM personas based on the BDI-II

├── src/
│   └── llms/
│       └── structured_output/
│           └── llm_judge_compare_depression.py  # Main experiment script
│           └── evaluation/evaluate_ranking_depression_prediction.py  # Evaluation script
│           └── singularity/  # Bash scripts designed to facilitate the use of Singularity containers for the experiments
│           └── results/  # Results from the four LLMs included in the paper


└── README.md                       # You are here 🙂

```

## 🔬  Quick Start

### 🔧 Running the Experiments
*Important, you need to infrastructure to deploy your Ollama server and models. We use singularity in this repository for constructing the images and running the experiments, but you can use Docker or any technology you may prefer.*

1.  **Prepare the data**
    
    Place the patient conversation `.txt` files in a directory, e.g.:
    
    ```text
    data/conversations/
    ├── patient_01.txt
    ├── patient_02.txt
    └── ...
    
    ```
    
2.  **Launch the comparison script**
    
    ```bash
    python src/llms/structured_output/llm_judge_compare_depression.py \
        /path/to/conversations \
        /path/to/results.jsonl
    
    ```
    
    -   `conversations_dir` – directory containing the `.txt` logs
        
    -   `results_file` – path where the JSONL results will be written
        

### 📊  Evaluating the Results

```bash
python src/evaluation/evaluate_results.py \
    /path/to/results.jsonl \
    llm-personas-information/golden_truth_BDI_depression_ranking.txt

```

The script reports accuracy metrics by comparing your model’s ranking against the **BDI (Beck Depression Inventory) golden‑truth** in `golden_truth_BDI_depression_ranking.txt`.


## 📝 Citation

*Coming soon – paper under submission.*  
If you use this resource, please ⭐ star the repo and stay tuned for citation info.

---

## 📬 Contact

For questions, please reach out via email: `anxo.pvila@udc.es`