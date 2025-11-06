# Systematic Literature Review: Screening Workflow Analysis
## Analysis of "3rd Screening" Inclusion/Exclusion Decisions

**Date**: November 6, 2025
**Data Source**: Google Sheets "Coding & screening works" → "3rd Screening"
**Scope**: 189 papers in screening pool
**Screened**: 85 papers (45.0%) | **Remaining**: 104 papers (55.0%)

---

## Executive Summary

This document analyzes the systematic screening workflow for 189 papers in the "3rd Screening" phase, documenting inclusion/exclusion criteria, decision patterns, and quality assurance measures. Through comprehensive analysis of screening notes, we identify **5 major exclusion patterns** accounting for all 31 rejected papers, validate **4 core inclusion criteria** applied to 54 accepted papers, and provide a standardized decision tree for screening the remaining 104 papers.

### Key Findings

| Metric | Value | Insight |
|--------|-------|---------|
| **Total Papers** | 189 papers | Full screening pool |
| **Screened** | 85 papers (45.0%) | Strong progress on J's workload |
| **Included (Y)** | 54 papers (28.6%) | Ready for coding, 100% PDF uploaded |
| **Excluded (N)** | 31 papers (16.4%) | Detailed exclusion reasons documented |
| **Unscreened** | 104 papers (55.0%) | Awaiting decisions (25 for J, 79 for M) |
| **Questionable (Q)** | 0 papers (0%) | No borderline cases - Clear criteria |
| **Note Coverage** | 189/189 (100%) | Complete decision rationale documentation |

### Primary Conclusions

1. **Stringent AI method specification requirement**: 48% of exclusions (15 papers) result from failure to explicitly name specific AI/ML algorithms (e.g., CNN, Random Forest, BERT). Papers using only "machine learning" or "AI" without methodological detail are systematically excluded.

2. **Clear "AI for Design" vs "Design of AI" distinction**: 26% of exclusions (8 papers) involve papers designing AI systems themselves (chatbots, AI wearables, clinical decision support systems) rather than using AI as a tool to support design tasks.

3. **100% documentation coverage with structured notes**: Every paper has detailed inclusion/exclusion reasoning, ensuring transparency, reproducibility, and inter-rater reliability validation potential.

4. **No ambiguous cases**: Zero papers marked as "Questionable" (Q) indicates clear, well-defined criteria that minimize subjective interpretation.

5. **Workload imbalance requires attention**: Researcher J has completed 77.3% of assigned papers (85/110), while Researcher M has 0% completion (0/79), creating potential bottleneck for study completion.

---

## 1. Current Status Overview

### 1.1 Screening Progress

**189 Total Papers Distribution:**

| Status | Count | % | Description |
|--------|-------|---|-------------|
| ✅ **Included (Y)** | 54 | 28.6% | Passed screening criteria, ready for coding |
| ❌ **Excluded (N)** | 31 | 16.4% | Failed screening criteria, detailed reasons documented |
| ⚪ **Unscreened** | 104 | 55.0% | Awaiting screening decisions |
| ❓ **Questionable (Q)** | 0 | 0.0% | No borderline cases identified |

**PDF Upload Status:**
- All 54 included papers have PDFs uploaded (100% completion rate)
- Ready for immediate coding workflow transition

### 1.2 Sheet Structure

**12 Columns with Complete Data Coverage:**

| Column | Data Type | Coverage | Purpose |
|--------|-----------|----------|---------|
| Index | Integer | 100% | Unique paper identifier |
| Article Title | Text | 100% | Full paper title |
| Author Full Names | Text | 100% | Complete author list |
| Source Title | Text | 100% | Journal/conference name |
| Publication Year | Integer | 100% | 2020-2025 range |
| Abstract | Text | 100% | Full abstract text |
| DOI Link | URL | 100% | Digital object identifier |
| Design Domain Classification | Categorical | 100% | Preliminary domain tagging |
| **Inclusion (Y/N/Q/R)** | Categorical | 100% | **Primary screening decision** |
| **Assigned_to** | Categorical | 100% | Researcher assignment (J/M) |
| **PDF_uploaded** | Categorical | 100% | Upload status tracking |
| **Note** | Text | 100% | **Detailed decision rationale** |

**Critical Finding**: 100% note coverage (189/189 papers) ensures complete decision transparency and reproducibility.

---

## 2. Five Major Exclusion Patterns

Through systematic analysis of 31 excluded papers, we identified **5 distinct exclusion patterns** accounting for 100% of rejections. Each pattern reflects specific quality criteria for AI+Design research.

### Pattern 1: AI Method Not Specified (48% of exclusions, ~15 papers)

**Exclusion Criterion**: Papers MUST explicitly name specific AI/ML methods (e.g., CNN, GAN, Random Forest, Transformer, BERT). Generic terms like "AI", "machine learning", "deep learning", or "computer vision" without algorithmic specification are insufficient.

**Rationale**: Methodological specificity ensures:
- Reproducibility of research
- Clear technical contribution
- Ability to classify AI methods systematically (Deep CV, Traditional ML, Gen AI, etc.)
- Distinction from vague conceptual papers

**Examples of Insufficient Specificity:**

| Paper Index | Abstract Language | Issue | Decision |
|-------------|------------------|-------|----------|
| #90 | "computer vision" mentioned | No specific CV algorithm (CNN, YOLO, R-CNN) | ❌ Excluded |
| #95 | "machine learning-based approach" | No ML algorithm (SVM, Random Forest, XGBoost) | ❌ Excluded |
| #122 | "machine learning schemes" and "data mining" | Generic terms, no specific algorithm | ❌ Excluded |
| #141 | "deep learning techniques" | No architecture specified (ResNet, Transformer, GAN) | ❌ Excluded |

**Contrast with Included Papers:**

| Paper Index | Abstract Language | Specification Level | Decision |
|-------------|------------------|---------------------|----------|
| #1 | "PointNet-based encoder-decoder network" | Specific architecture + method | ✅ Included |
| #8 | "Convolutional neural network (CNN)" | Specific method named | ✅ Included |
| #15 | "word embedding algorithms", "BERT" | Specific NLP methods | ✅ Included |

**Boundary Cases:**
- "Deep learning for image classification" → **Insufficient** (architecture not specified)
- "ResNet-50 for image classification" → **Sufficient** (specific architecture)
- "Generative AI for design" → **Insufficient** (which generative model?)
- "StyleGAN2 for form generation" → **Sufficient** (specific generative model)

---

### Pattern 2: AI is the Product Being Designed, Not a Tool (26%, ~8 papers)

**Exclusion Criterion**: Papers about **"Design OF AI systems"** (where AI is the output/product) are excluded. Only **"AI FOR design"** (where AI supports design tasks) is included.

**Rationale**: This study focuses on AI as a **design tool**, not AI as a **design artifact**. The distinction ensures focus on how AI augments human design capabilities, not how to engineer AI systems.

**Excluded Examples:**

| Paper Index | Topic | Why Excluded | Decision |
|-------------|-------|--------------|----------|
| #153 | Designing an AI clinical decision support system | AI system is the product being designed | ❌ Excluded |
| #161 | Designing a chatbot service | Chatbot (AI) is the product | ❌ Excluded |
| #174 | Designing an AI-powered wearable device | AI wearable is the product | ❌ Excluded |
| #176 | Designing feedback mechanisms FOR AI mood tracker apps | AI app is the product, not the tool | ❌ Excluded |
| #181 | Designing conversational user interfaces | CUI (AI) is the product | ❌ Excluded |

**Boundary Clarification:**

| Scenario | Classification | Decision |
|----------|---------------|----------|
| Designing a chatbot's conversational flow | Design OF AI | ❌ Excluded |
| Using ChatGPT to generate design concepts | AI FOR design | ✅ Included |
| Designing an AI-powered smart thermostat | Design OF AI | ❌ Excluded |
| Using ML to optimize thermostat interface layout | AI FOR design | ✅ Included |
| Designing a recommendation algorithm | Design OF AI | ❌ Excluded |
| Using recommendations to inform product design | AI FOR design | ✅ Included |

**Key Distinction**: The question is not "What is being designed?" but "What role does AI play?"
- If AI is the **thing being designed** → Excluded
- If AI is the **tool supporting design** → Included

---

### Pattern 3: AI for Non-Design Applications (16%, ~5 papers)

**Exclusion Criterion**: AI must support design tasks (create, optimize, evaluate, inform design). AI applications for other purposes (workforce management, clinical diagnosis, statistical analysis, eco-driving) are excluded even if they involve "design" domain terminology.

**Design Task Definition**: Must demonstrate AI supporting one or more of:
- **Generate/Create**: Produce design concepts, sketches, models, layouts
- **Optimize**: Improve design parameters, topology, performance, aesthetics
- **Evaluate**: Assess design quality, usability, user satisfaction, feasibility
- **Inform**: Extract insights from data to guide design decisions
- **Explore**: Navigate design spaces, identify alternatives, discover opportunities

**Excluded Examples:**

| Paper Index | Topic | AI Application | Why Excluded |
|-------------|-------|----------------|--------------|
| #129 | AI monitors designer work efficiency | Workforce management | Not a design task (productivity tracking) |
| #166 | Deep learning predicts fuel consumption | Eco-driving optimization | Not a design task (vehicle operation) |
| #173 | Neural networks for statistical analysis | Research tool | Not a design task (data analysis) |
| #177 | Multi-Agent RL for medical image segmentation | Clinical diagnosis | Not a design task (medical application) |
| #185 | ML predicts student performance | Educational assessment | Not a design task (learning analytics) |

**Boundary Cases:**

| Scenario | Design Task? | Decision |
|----------|--------------|----------|
| AI predicts product performance for design optimization | ✅ Yes (Inform/Optimize design) | ✅ Included |
| AI predicts user behavior to inform UX design | ✅ Yes (Inform design) | ✅ Included |
| AI predicts manufacturing costs for design constraints | ✅ Yes (Inform design) | ✅ Included |
| AI predicts fuel consumption for eco-driving | ❌ No (Vehicle operation, not design) | ❌ Excluded |
| AI monitors designer productivity | ❌ No (Workforce management, not design) | ❌ Excluded |

---

### Pattern 4: Perception/Attitude Studies Without Implementation (6%, ~2 papers)

**Exclusion Criterion**: Papers must demonstrate AI **implementation** or **empirical evaluation**. Pure perception studies, survey research, or workshop proposals without AI application are excluded.

**Rationale**: This review focuses on **empirical AI+Design research** with:
- Implemented AI systems or prototypes
- Experimental evaluation of AI methods
- Case studies of AI application in design contexts
- Quantitative or qualitative data on AI performance/impact

**Excluded Examples:**

| Paper Index | Topic | Why Excluded |
|-------------|-------|--------------|
| #157 | Qualitative study of UX designers' perceptions of Generative AI | No AI implementation, pure perception study |
| #165 | Workshop proposal identifying conversational UI research challenges | No AI implementation, agenda-setting only |

**Included Contrast:**

| Paper Index | Topic | Why Included |
|-------------|-------|--------------|
| #135 | Comparative study: ChatGPT vs BERT for design support | Empirical evaluation with implementation |
| #149 | Gen AI & LLMs transforming luxury design (with case studies) | Implementation + case study evidence |

**Boundary Clarification:**
- Perception study + AI implementation pilot → **Included** (empirical component)
- Perception study alone → **Excluded** (no implementation)
- Workshop with AI tool demonstration → **Included** (implementation evidence)
- Workshop proposing future research directions → **Excluded** (no current implementation)

---

### Pattern 5: Design OF AI Systems Only (3%, ~1 paper)

**Exclusion Criterion**: Papers focused solely on improving AI systems themselves (model architecture, training efficiency, algorithm performance) without demonstrating design application are excluded.

**Excluded Example:**

| Paper Index | Topic | Why Excluded |
|-------------|-------|--------------|
| #164 | Improving large language model intention understanding | AI system improvement without design application |

**Included Contrast:**

| Paper Index | Topic | Why Included |
|-------------|-------|--------------|
| #168 | Conversational GUI control using LLMs | LLM applied to design task (interface generation) |

**Key Distinction**:
- Improving AI model → **Excluded** (AI research, not design research)
- Applying AI model to design → **Included** (design research using AI)

---

## 3. Four Core Inclusion Criteria

All 54 included papers satisfy **4 mandatory criteria**. These criteria ensure papers contribute to AI+Design knowledge with methodological rigor and design relevance.

### Criterion 1: Specific AI Method Named ✅

**Requirement**: Papers must explicitly name concrete AI/ML methods from the following categories:

**Acceptable AI Method Specifications:**

| Category | Examples | Papers |
|----------|----------|--------|
| **Deep Learning (CV)** | CNN, ResNet, YOLO, ViT, PointNet, U-Net | 19 papers |
| **Deep Learning (NLP)** | BERT, Transformer, LSTM, RNN, GPT, Word2Vec | 7 papers |
| **Generative AI** | GAN, StyleGAN, VAE, Diffusion Models, Pix2Pix | 8 papers |
| **Large Generative AI** | GPT-3/4, ChatGPT, Claude, DALL-E, Midjourney, Gemini | 4 papers |
| **Traditional ML** | SVM, Random Forest, Decision Trees, Linear Regression, K-Means, XGBoost | 15 papers |
| **Reinforcement Learning** | Q-Learning, DQN, Policy Gradient, Multi-Agent RL | 1 paper |

**Validation Examples:**

| Paper Index | AI Method Specification | Validation |
|-------------|------------------------|------------|
| #1 | "PointNet-based encoder-decoder network" | ✅ Specific architecture |
| #7 | "Genetic algorithm", "neural networks" | ✅ Multiple methods specified |
| #8 | "Convolutional neural network (CNN)" | ✅ Method + acronym |
| #15 | "Natural language processing techniques", "word embedding algorithms", "BERT" | ✅ Multiple NLP methods |
| #19 | "Bayesian optimization", "surrogate models" | ✅ Specific optimization methods |

**Common Pitfalls (Excluded):**
- "Machine learning-based approach" → ❌ No specific method
- "Deep learning model" → ❌ Architecture not specified
- "AI-powered system" → ❌ No algorithmic detail
- "Computer vision techniques" → ❌ Which CV algorithm?

---

### Criterion 2: AI Supports Design Tasks ✅

**Requirement**: Papers must demonstrate AI supporting one or more core design activities. Generic "design improvement" without task specification is insufficient.

**Five Design Task Categories:**

| Task Category | Description | Example Applications | Papers |
|---------------|-------------|---------------------|--------|
| **Generate/Create** | AI produces new design artifacts | CAD model generation, sketch synthesis, layout generation, form exploration | 31 papers (57%) |
| **Optimize** | AI improves design parameters or configurations | Topology optimization, parameter tuning, performance maximization, multi-objective optimization | 33 papers (61%) |
| **Evaluate** | AI assesses design quality or suitability | Usability evaluation, aesthetic assessment, performance prediction, quality inspection | 20 papers (37%) |
| **Inform** | AI extracts insights to guide design decisions | Requirement extraction from reviews, trend analysis, user preference modeling, design rationale mining | 15 papers (28%) |
| **Explore** | AI navigates design spaces or identifies alternatives | Design space exploration, alternative generation, constraint identification, opportunity discovery | Variable |

**Note**: Most papers (81%, 44/54) provide **multiple assistance types**, indicating AI tools are multi-functional rather than single-purpose.

**Validation Examples:**

| Paper Index | Design Task Specification | Task Category | Validation |
|-------------|--------------------------|---------------|------------|
| #1 | "Design space dimensionality reduction for shape optimization" | Optimize + Explore | ✅ Explicit task |
| #7 | "Product conceptual design scheme configurations" | Generate | ✅ Explicit task |
| #19 | "Data-driven design of conical origami structures" | Generate + Optimize | ✅ Multiple tasks |
| #110 | "Extracting consumer preferences from reviews" | Inform | ✅ Explicit task |
| #128 | "Analyzing facial mask attributes from reviews" | Inform + Evaluate | ✅ Multiple tasks |

**Common Pitfalls (Excluded):**
- "Improves design quality" → ❌ Too vague (how?)
- "Supports designers" → ❌ What specific support?
- "Enhances design process" → ❌ Which process activity?

---

### Criterion 3: Design Domain Relevance ✅

**Requirement**: Papers must address one or more relevant design domains. Papers outside these domains are excluded regardless of AI method sophistication.

**Relevant Design Domains:**

| Domain | Description | Example Topics | Papers |
|--------|-------------|----------------|--------|
| **Engineering Design** | Technical product design, mechanical systems, structural design | Topology optimization, CAD automation, performance prediction, manufacturing design | 40 papers (74%) |
| **Product Design** | Consumer products, industrial design, form design | Shape generation, aesthetic evaluation, user-centered design, packaging design | Overlaps with Engineering |
| **UI/UX Design** | Digital interface design, interaction design, user experience | Interface generation, usability optimization, interaction patterns, emotion recognition | 7 papers (13%) |
| **Service Design** | Service systems, product-service systems, experience design | Service blueprinting, journey optimization, touchpoint design, customer experience | 3 papers (5.6%) |

**Excluded Domains:**
- Clinical medicine (diagnosis, treatment planning) → Unless designing medical devices
- Education (learning analytics, curriculum design) → Unless designing educational tools/interfaces
- Business operations (supply chain, workforce management) → Unless designing operational systems
- Pure AI research (model architecture, training algorithms) → Unless applied to design

**Validation Examples:**

| Paper Index | Domain | Validation |
|-------------|--------|------------|
| #108 | Car design classification (Engineering) | ✅ Relevant |
| #96 | Product innovation with DNN (Product) | ✅ Relevant |
| #186 | Emotion recognition for indoor space (UI/UX, Service) | ✅ Relevant |
| #170 | AR picture books (UI/UX) | ✅ Relevant |

---

### Criterion 4: Empirical Evidence (Preferred) ✅

**Requirement**: Papers with implementation, case studies, experiments, or empirical evaluation are strongly preferred over purely conceptual papers.

**Empirical Evidence Types:**

| Evidence Type | Description | Strength |
|---------------|-------------|----------|
| **Implementation** | Working system/prototype described with technical details | High |
| **Experimental Evaluation** | Quantitative results (accuracy, performance metrics, user studies) | High |
| **Case Study** | Real-world application with detailed analysis | Medium-High |
| **Comparative Study** | Comparison with baseline methods or human performance | High |
| **User Study** | Qualitative or quantitative user feedback | Medium |

**Preference Hierarchy:**
1. Implementation + Experimental Evaluation (Most Preferred)
2. Implementation + Case Study
3. Implementation Only
4. Theoretical Framework with Validation Plan
5. Pure Conceptual Paper (Generally Excluded unless highly novel)

---

## 4. Note Structure Analysis

### 4.1 Standardized Note Format

All 54 included papers use a consistent note structure:

```
AI Method: [Specific method name(s)]
Design Task: [Specific design activity/domain]
```

**Example Notes:**

| Paper Index | Note |
|-------------|------|
| #1 | AI Method: PointNet-based encoder-decoder network<br>Design Task: Design space dimensionality reduction for shape optimization |
| #7 | AI Method: Genetic algorithm, neural networks<br>Design Task: Product conceptual design scheme configurations |
| #15 | AI Method: NLP techniques, word embedding algorithms, BERT<br>Design Task: Extract design requirements from user reviews |

**Benefits of Structured Notes:**
1. **Transparency**: Clear rationale for every decision
2. **Reproducibility**: Other researchers can apply same criteria
3. **Inter-rater reliability**: Structured format enables consistency checks
4. **Data extraction**: Machine-readable format for systematic review
5. **Audit trail**: Complete decision history for quality assurance

### 4.2 Exclusion Note Patterns

Excluded papers also follow structured formats:

```
Exclusion Reason: [Primary reason category]
Detail: [Specific issue identified]
```

**Example Exclusion Notes:**

| Paper Index | Note |
|-------------|------|
| #90 | Exclusion Reason: AI Method Not Specified<br>Detail: "computer vision" mentioned but no specific CV algorithm |
| #153 | Exclusion Reason: AI is the Product<br>Detail: Designing an AI clinical decision support system (AI = product, not tool) |
| #129 | Exclusion Reason: Non-Design Application<br>Detail: AI monitors designer work efficiency (workforce management, not design task) |

---

## 5. Workload Distribution Analysis

### 5.1 Current Distribution

| Researcher | Total Papers | Screened | % Complete | Unscreened | Included | Excluded | PDF Uploaded |
|------------|--------------|----------|------------|------------|----------|----------|--------------|
| **J (Primary)** | 110 | 85 | **77.3%** | 25 | 54 | 31 | 54 (100% of Y) |
| **M (Secondary)** | 79 | 0 | **0.0%** | 79 | 0 | 0 | 0 |
| **Total** | 189 | 85 | **45.0%** | 104 | 54 | 31 | 54 |

### 5.2 Key Findings

**Researcher J:**
- ✅ Strong progress: 77.3% of assigned papers screened
- ✅ All 54 included papers have PDFs uploaded (100% completion, ready for coding)
- ⚠️ 25 papers remain unscreened (target: 1-2 weeks to complete)
- 📊 Inclusion rate: 63.5% (54/85) - Indicates stringent but fair criteria

**Researcher M:**
- ⚠️ No screening activity yet (0/79 papers)
- 🚨 Potential bottleneck for study completion
- 📅 Recommendation: Prioritize M's workload or redistribute papers

### 5.3 Completion Timeline Projection

**Assuming current pace (J: ~10 papers/week):**
- J's remaining 25 papers: **2-3 weeks**
- M's full workload (79 papers): **8-10 weeks**
- Total completion: **10-12 weeks** (if M starts immediately)

**Recommendation**: Consider:
1. Redistribute 30-40 papers from M to J to accelerate completion
2. Set interim milestones for M (e.g., 20 papers by Week 2, 40 by Week 4)
3. Conduct inter-rater reliability check on 10-20 overlapping papers

---

## 6. Decision Tree for Remaining 104 Papers

The following decision tree standardizes screening for the remaining 104 unscreened papers, ensuring consistency with established patterns.

### Step 1: AI Method Specification Check

**Question**: Is a SPECIFIC AI/ML method explicitly named in the abstract?

**Required Specificity**:
- ✅ YES: CNN, GAN, BERT, Random Forest, Genetic Algorithm, Transformer, etc.
- ❌ NO: "machine learning", "AI", "deep learning", "computer vision" (without algorithm)

**Action**:
- If **NO** → **EXCLUDE** with reason: "AI Method Not Specified"
- If **YES** → Proceed to Step 2

---

### Step 2: AI Role Check

**Question**: Does AI SUPPORT design tasks (tool), or IS AI the design output (product)?

**AI as Tool** (✅ Include):
- Using ChatGPT to generate design concepts
- Using CNN to optimize product shape
- Using NLP to extract user requirements from reviews
- Using GAN to synthesize design alternatives

**AI as Product** (❌ Exclude):
- Designing a chatbot conversation flow
- Designing an AI-powered wearable device
- Designing an AI clinical decision support system
- Designing feedback mechanisms for AI apps

**Action**:
- If AI is the **product** → **EXCLUDE** with reason: "AI is the Product, Not a Tool"
- If AI is a **tool** → Proceed to Step 3

---

### Step 3: Design Domain Check

**Question**: Is the design domain relevant (Engineering/Product/UI/UX/Service)?

**Relevant Domains** (✅ Include):
- Engineering Design (CAD, topology, mechanical systems)
- Product Design (industrial, consumer products)
- UI/UX Design (interfaces, interactions, experiences)
- Service Design (service systems, touchpoints, journeys)

**Excluded Domains** (❌ Exclude):
- Clinical medicine (diagnosis, treatment) - unless designing medical devices
- Education (learning analytics) - unless designing educational tools
- Business operations (supply chain, HR) - unless designing operational systems
- Pure AI research (model training, algorithms) - unless applied to design

**Action**:
- If **outside design domains** → **EXCLUDE** with reason: "Outside Design Domain"
- If **within design domains** → Proceed to Step 4

---

### Step 4: Design Task Specification Check

**Question**: Are design tasks/processes explicitly described?

**Explicit Design Tasks** (✅ Include):
- Generate CAD models
- Optimize topology for manufacturing
- Extract user requirements from reviews
- Evaluate interface usability
- Explore design space alternatives

**Vague Descriptions** (❌ Exclude):
- "Improves design quality" (how?)
- "Supports designers" (what specific support?)
- "Enhances design process" (which activity?)

**Action**:
- If design tasks are **vague/unspecified** → **EXCLUDE** with reason: "Design Task Not Specified"
- If design tasks are **explicit** → **INCLUDE** (Inclusion=Y)

---

### Step 5: Documentation

**For Included Papers**:
```
Inclusion: Y
Note:
AI Method: [Specific method name(s)]
Design Task: [Specific design activity/domain]
```

**For Excluded Papers**:
```
Inclusion: N
Note:
Exclusion Reason: [Primary reason from Steps 1-4]
Detail: [Specific issue identified in abstract]
```

---

## 7. Key Insights & Recommendations

### 7.1 Screening Quality Assessment

**Strengths:**
1. ✅ **100% documentation coverage**: All 189 papers have detailed notes
2. ✅ **Clear, consistent criteria**: Zero questionable (Q) cases demonstrates well-defined rules
3. ✅ **Structured note format**: Enables transparency, reproducibility, inter-rater reliability checks
4. ✅ **Stringent AI specificity**: 48% exclusion rate for method non-specification ensures high-quality corpus
5. ✅ **Ready for coding**: All 54 included papers have PDFs uploaded (100% preparation)

**Areas for Improvement:**
1. ⚠️ **Workload imbalance**: M's 0% completion creates bottleneck risk
2. ⚠️ **Inter-rater reliability not yet validated**: Conduct 10-20 paper overlap check between J and M
3. ⚠️ **No borderline case resolution protocol**: While current 0 Q papers is excellent, establish process for future ambiguous cases

---

### 7.2 Exclusion Pattern Insights

**Insight 1: Methodological Rigor is Primary Barrier (48%)**
Nearly half of exclusions result from insufficient AI method specification. This reflects:
- Many papers use "AI" or "ML" as buzzwords without technical depth
- AI+Design field is still maturing methodologically
- Systematic review requires reproducible, specific methods

**Implication**: The final corpus will represent **methodologically rigorous** AI+Design research, potentially excluding conceptual or early-stage exploratory work.

---

**Insight 2: "AI for Design" vs "Design of AI" is Most Nuanced (26%)**
This distinction requires careful judgment:
- Clear cases: Chatbot design (excluded) vs ChatGPT for design (included)
- Ambiguous cases: AI-powered product where AI provides core functionality (e.g., smart thermostat)

**Recommendation**: Develop decision rubric for ambiguous cases:
- If AI functionality is **incidental to design** → Include
- If AI functionality **defines the product** → Exclude

---

**Insight 3: Design Task Specificity Matters**
Papers describing specific activities (Generate, Optimize, Evaluate, Inform, Explore) are included. Vague claims of "design improvement" or "supporting designers" without task specification lead to exclusion.

**Implication**: The final corpus will focus on **task-specific AI applications** with clear use cases, potentially excluding general-purpose or exploratory tools.

---

### 7.3 Recommendations for Remaining 104 Papers

**Priority 1: Complete J's Workload (25 Papers)**
- Target: 1-2 weeks at current pace (~10 papers/week)
- Apply decision tree systematically
- Document any new edge cases for protocol refinement

**Priority 2: Address M's Workload (79 Papers)**
- Option A: M screens all 79 papers (8-10 weeks if matching J's pace)
- Option B: Redistribute 30-40 papers to J for faster completion
- Option C: Recruit additional screener and conduct training with decision tree

**Priority 3: Inter-Rater Reliability Check**
- Select 10-20 papers for dual screening (J and M independently)
- Calculate Cohen's kappa (target: κ > 0.8 for substantial agreement)
- Resolve discrepancies through discussion and protocol refinement
- Document disagreement patterns for future training

**Priority 4: Protocol Documentation**
- Formalize decision tree into screening protocol document
- Create training materials with examples for future screeners
- Establish conflict resolution process for questionable cases
- Prepare exclusion reason taxonomy for publication methods section

---

### 7.4 Quality Assurance Measures

**Recommended Actions:**

1. **Dual Screening Sample (10-20 papers)**
   - Both J and M screen same papers independently
   - Calculate inter-rater reliability (Cohen's kappa)
   - Target: κ > 0.8 (substantial agreement)
   - Resolve discrepancies through discussion

2. **Borderline Case Repository**
   - Document any ambiguous cases (even if ultimately included/excluded)
   - Create decision rationale repository for future reference
   - Establish consensus-building process for difficult decisions

3. **Periodic Calibration Meetings**
   - Weekly check-ins during screening phase
   - Review recent decisions for consistency
   - Discuss edge cases and refine criteria as needed

4. **Audit Trail Maintenance**
   - Preserve all screening decisions with timestamps
   - Track protocol changes (if any) with version control
   - Document any deviations from decision tree with justification

---

## 8. Conclusion

The "3rd Screening" workflow demonstrates **high-quality systematic review practices** with:
- **100% documentation coverage** (189/189 papers with detailed notes)
- **Clear, consistent criteria** (0 questionable cases)
- **Strong progress** (45% completion, 54 papers ready for coding)
- **Stringent quality standards** (methodological specificity, task clarity)

The identified **5 exclusion patterns** and **4 inclusion criteria** provide a transparent, reproducible framework for screening the remaining 104 papers. The standardized **decision tree** ensures consistency across researchers and enables efficient completion of the screening phase.

**Primary Challenges**:
1. Workload imbalance (J: 77.3% complete, M: 0% complete)
2. Need for inter-rater reliability validation
3. Timeline risk (10-12 weeks to completion if M starts immediately)

**Primary Opportunities**:
1. High-quality corpus (stringent AI method specification)
2. Clear methodological contribution (transparent inclusion/exclusion criteria)
3. Reproducible process (complete documentation, structured notes)

As screening progresses toward completion, maintaining consistency through the decision tree, validating inter-rater reliability, and addressing workload imbalance will ensure a robust, defensible systematic literature review.

---

**Document Version**: 1.0
**Analysis Date**: November 6, 2025
**Papers Analyzed**: 189 total (85 screened, 104 remaining)
**Screening Completion**: 45.0%
**Next Milestone**: Complete J's 25 remaining papers (Target: 2 weeks)
