# AI+Design Research Landscape: Executive Summary
## Analysis of 54 Coded Papers from Systematic Literature Review

**Date**: November 6, 2025
**Data Source**: Google Sheets "Coding & screening works"
**Analysis Scope**: 54 coded papers from 189-paper screening pool (28.6% completion)

---

## Executive Summary

This document presents key findings from systematic coding of 54 research papers on AI applications in design, representing 28.6% of the full 189-paper corpus. Through quantitative pattern analysis, we identify **5 major patterns** and **6 critical research gaps** in the current AI+Design research landscape.

### Key Findings at a Glance

| Finding | Value | Assessment |
|---------|-------|------------|
| **Coding Progress** | 54/189 papers (28.6%) | Strong 2022-2024 representation |
| **Industrial/Product Design** | 74% (40/54 papers) | Dominates over UI/UX and Service Design |
| **Develop Phase** | 93% (50/54 papers) | Concentrated in prototyping/testing stages |
| **Discovery/Delivery Phases** | 0% each | Completely absent from current research |
| **Service Design** | 5.6% (3/54 papers) | Severely underrepresented |
| **2024 Large Gen AI** | 4 papers (all from 2024) | Paradigm shift post-ChatGPT |
| **Deep CV + Traditional ML** | 63% combined | Most mature research methods |

### Five Primary Conclusions

1. **Research is heavily concentrated in execution phases**: 93% of papers focus on algorithm development and prototyping (Develop phase), while early-stage exploration (Discovery) and post-deployment (Delivery) are completely absent.

2. **Industrial and product design dominate**: 74% of papers address physical product design and engineering applications, while service design (5.6%) and UI/UX design (13%) are underrepresented relative to industry demand.

3. **Traditional methods persist alongside deep learning**: Despite the deep learning revolution, Traditional ML remains strong (28%), particularly for early-stage requirements extraction where interpretability matters.

4. **2024 marks a paradigm shift**: All 4 papers using Large Gen AI (GPT-4, ChatGPT) are from 2024, signaling the transition from task-specific AI to general-purpose design assistants.

5. **Critical research gaps represent high-impact opportunities**: Discovery phase AI (0%), Delivery phase AI (0%), Service Design AI (5.6%), and Reinforcement Learning for design (1.9%) are severely underexplored areas with significant potential.

### Discussion Agenda

The following questions frame key debates emerging from this analysis:

1. **Is Develop phase dominance inevitable?** Can we realistically shift AI research earlier into Discovery, or does this reflect fundamental limitations of current AI capabilities for open-ended exploration?

2. **Why does Service Design lag so far behind?** With 74% Industrial vs 5.6% Service, does this represent academic-industry misalignment, or are service experiences genuinely harder to model with AI?

3. **Will Large Gen AI replace specialized models?** The 2024 explosion suggests a paradigm shift, but Traditional ML and Deep CV still dominate. What's the future balance between general-purpose and task-specific AI?

4. **Are Discovery papers miscoded or truly absent?** Could Discovery-focused papers exist in the remaining 135 papers under different terminology (e.g., "exploratory study", "user research"), or is this a genuine research void?

5. **Traditional ML's persistent value**: Why does 28% of research still use Traditional ML despite deep learning's superiority? Is this methodological conservatism or a principled choice for interpretability?

6. **Prioritization dilemma**: Should future research fill critical gaps (Discovery, Delivery, Service Design) or deepen mature areas (Deep CV × Industrial) where infrastructure is established?

---

## 1. Overview & Current Progress

**Progress Metrics**: 54 papers coded from 189-paper pool (28.6%) | Timeline: 2020-2025 (6 years)

| Year | Coded Papers | % | AI Methods Evolution |
|------|--------------|---|---------------------|
| 2020 | 3 | 5.6% | Baseline (Traditional ML: 2, Deep CV: 1) |
| 2021 | 6 | 11.1% | Deep CV emerges (3 papers) |
| 2022 | 17 | 31.5% | **Peak volume**, balanced methods |
| 2023 | 5 | 9.3% | **Underrepresented** - Critical transition year |
| 2024 | 19 | 35.2% | **Large Gen AI explosion** (4 papers, all LLMs) |
| 2025 | 4 | 7.4% | Early year data |

**Critical Observation**: 2023 is significantly underrepresented (5 coded vs 26 available), representing a temporal gap in current coding. This year captures the critical 12-18 month period following ChatGPT's November 2022 launch, when researchers began integrating Large Gen AI into design workflows. Prioritizing 2023 papers in next coding batch will ensure temporal continuity.

---

## 2. Five Major Patterns

### Pattern 1: Industrial/Product Design Dominance (74%)

**Quantitative Data**: Industrial/Product 40 papers (74%) | UI/UX 7 papers (13%) | Service 3 papers (5.6%)

| Design Discipline | Deep CV | Traditional ML | Gen AI | Large Gen AI | Total |
|-------------------|---------|----------------|--------|--------------|-------|
| Industrial/Product | 14 | 14 | 7 | 3 | 38 |
| UI/UX | 4 | 1 | 1 | 1 | 7 |
| Service Design | 1 | 0 | 0 | 0 | 1 |

**Analysis**: Industrial design applications span all AI methods from Traditional ML to Large Gen AI, representing the most mature AI+Design research area. This dominance reflects three factors: (1) **Measurable outcomes** - engineering performance metrics and structural analysis provide clear evaluation criteria; (2) **Data availability** - CAD models, specifications, and manufacturing data are standardized and accessible; (3) **Industry funding** - automotive, aerospace, and manufacturing sectors heavily invest in AI research.

**Cross-Domain Insight**: Deep CV × Industrial Design represents 22% of the entire dataset (12 papers), forming the most established research cluster with 15+ years of infrastructure development (AlexNet 2012 → ViT 2020). This area focuses on shape analysis, 3D modeling, topology optimization, and visual quality assessment.

**Discussion Point**: The severe underrepresentation of Service Design (5.6%) and moderate underrepresentation of UI/UX (13%) suggests potential academic-industry misalignment. Industry demand for service design AI (customer journey optimization, touchpoint design) and UI/UX AI (interface generation, usability prediction) may exceed academic research output.

---

### Pattern 2: Develop Phase Near-Monopoly (93%)

**Quantitative Data**: Develop 50 papers (93%) | Define 4 papers (7%) | Discovery 0 papers (0%) | Delivery 0 papers (0%)

| AI Method | Discovery | Define | Develop | Delivery |
|-----------|-----------|--------|---------|----------|
| Deep CV | 0 | 0 | 19 | 0 |
| Traditional ML | 0 | 3 | 12 | 0 |
| Gen AI | 0 | 0 | 8 | 0 |
| Large Gen AI | 0 | 0 | 4 | 0 |
| Deep NLP | 0 | 1 | 6 | 0 |
| RL | 0 | 0 | 1 | 0 |

**The 4 Define Phase Papers**: All focus on extracting user requirements from textual customer data (reviews, feedback):
- Index 128: Facial Masks Review Analysis (Traditional ML + XAI, 2024)
- Index 111: User Knowledge Acquisition (Traditional ML, 2021)
- Index 110: Consumer Preferences (Traditional ML, 2022)
- Index 91: Robot Failures from Reviews (Deep NLP, 2024)

**Analysis**: The 93% concentration in Develop phase reflects three converging factors:

1. **Academic publication bias**: Algorithm development and quantitative performance metrics are easier to publish in technical AI venues (CVPR, NeurIPS, AAAI) than exploratory or deployment research. Develop phase papers offer clear evaluation criteria (accuracy, F1 score, performance improvement), while Discovery and Delivery research produces qualitative insights harder to benchmark.

2. **AI's current capabilities**: AI excels at structured execution tasks (pattern recognition, generation, prediction) but struggles with open-ended exploration (Discovery requires creativity, cultural understanding, contextual inquiry) and long-term deployment management (Delivery requires stakeholder coordination, iterative refinement based on real-world feedback).

3. **Methodological divide**: Define phase uniquely favors Traditional ML (3 out of 4 papers, 75%) because early-stage requirements extraction demands **interpretability** over performance. Stakeholders need to understand how AI extracted requirements from customer data, making explainable Traditional ML preferable to black-box deep learning. In contrast, Develop phase prioritizes performance, enabling deep learning dominance.

**Cross-Phase Insight**: Traditional ML × Define Phase represents the only early-stage AI+Design research cluster, suggesting a structural barrier: early-stage design (Discovery, Define) requires interpretable, small-data methods, while execution (Develop) leverages powerful, data-hungry deep learning. This methodological divide may explain why 93% of research concentrates in Develop.

**Discussion Point**: Is this 93% concentration sustainable? Discovery and Delivery phases represent 0% of current research but are critical to design practice. Can explainable AI (XAI) bridge the methodological divide, enabling deep learning to enter early-stage design research?

---

### Pattern 3: Product Data Overwhelming (76%)

**Quantitative Data**: Product 41 papers (76%) | Behavior 6 papers (11%) | Perception 6 papers (11%) | Physiology 1 paper (1.9%) | Demographic/Environment 0 papers (0%)

| Data Type | Industrial | UI/UX | Service | Total |
|-----------|------------|-------|---------|-------|
| Product | 35 | 4 | 2 | 41 |
| Behavior | 3 | 3 | 0 | 6 |
| Perception | 2 | 3 | 1 | 6 |
| Physiology | 0 | 1 | 0 | 1 |

**Analysis**: Product data dominance (76%) aligns with Industrial Design focus (74%), reflecting genuine research concentration on physical product design. Product data encompasses diverse sub-types (specifications, images, reviews, performance metrics), but these are grouped into a single category. The complete absence of Demographic (0%) and Environment (0%) data signals missed opportunities in inclusive design (fairness, accessibility, cultural customization) and sustainable design (eco-design, lifecycle assessment, context-aware interfaces).

**Unique Case**: Index 167 (BCI for Electric Vehicle HMI, 2024) is the only paper using Physiology data (EEG brain-computer interface), combining Time Series (biosignals) + Image (dashboard) in a multimodal approach. This represents an extremely rare research direction with high potential for emotion-driven design and accessibility applications.

**Discussion Point**: The breadth of "Product" (76%) versus specificity of "Physiology" (1.9%) and absence of "Demographic/Environment" (0%) suggests structural imbalance. Should we subdivide Product data into granular categories (specifications, performance, reviews, images) to better understand research distribution?

---

### Pattern 4: Deep CV + Traditional ML Lead AI Methods (63%)

**Quantitative Data**: Deep CV 19 papers (35%) | Traditional ML 15 papers (28%) | Gen AI 8 papers (15%) | Deep NLP 7 papers (13%) | Large Gen AI 4 papers (7%) | RL 1 paper (1.9%)

**Year Trend Analysis**:

| Year | Deep CV | Traditional ML | Gen AI | Large Gen AI | Key Trend |
|------|---------|----------------|--------|--------------|-----------|
| 2020 | 1 | 2 | 0 | 0 | Baseline |
| 2021 | 3 | 2 | 0 | 0 | Deep CV growth |
| 2022 | 6 | 6 | 1 | 0 | Peak diversity |
| 2023 | 2 | 1 | 2 | 0 | Gen AI emerges |
| 2024 | 6 | 3 | 4 | **4** | **LLM explosion** |
| 2025 | 1 | 1 | 1 | 0 | Early data |

**Critical Insight**: All 4 Large Gen AI papers are from 2024, representing a paradigm shift 18 months after ChatGPT's November 2022 launch. These papers explore:
- Index 135: ChatGPT vs BERT for Design Support (comparative study)
- Index 149: Gen AI & LLMs Transform Luxury Design (creative process transformation)
- Index 168: Conversational GUI Control (natural language interface generation)
- Index 138: AI Collaboration Model for Design Forms (human-AI co-creation)

**Analysis**: Why do mature methods (Deep CV 35%, Traditional ML 28%) still dominate despite the Gen AI revolution?

1. **Established infrastructure**: Deep CV has 15+ years of research maturity (AlexNet 2012 → ResNet 2015 → ViT 2020), abundant pre-trained models (ImageNet, COCO), and mature toolkits (PyTorch, TensorFlow). Researchers can rapidly prototype and validate ideas.

2. **Task-method alignment**: Deep CV naturally pairs with Industrial Design (shape analysis, 3D modeling) which dominates this dataset. Traditional ML naturally pairs with Define phase (interpretable requirements extraction) and small-data scenarios.

3. **Gen AI emerging barriers**: High computational costs (GPU clusters for LLMs), ethical concerns (bias, misinformation, copyright), and integration challenges (prompt engineering, fine-tuning) slow adoption despite transformative potential.

**2024 Paradigm Shift**: Large Gen AI enables three capabilities absent in specialized models:
- **Natural language interfaces**: Designers specify requirements in plain English, not code
- **General-purpose tools**: Same model (GPT-4) works across design domains (product, UI, service)
- **Conversational iteration**: Refine designs through dialogue, not parameter tuning

**Discussion Point**: By 2026, will Large Gen AI exceed 50% of AI+Design research? Or will specialized models (Deep CV, Traditional ML) persist due to performance, cost, and control advantages?

---

### Pattern 5: Image Modality Dominance (56%)

**Quantitative Data**: Image standalone 18 papers (33%) | Text standalone 15 papers (28%) | Multimodal (Image+) 12 papers (22%) | Time Series 8 papers (15%) | Audio 1 paper (1.9%) | Video 1 paper (1.9%)

**Total papers involving images**: 30/54 = 56%

| Modality | Deep CV | Traditional ML | Gen AI | Deep NLP | Total |
|----------|---------|----------------|--------|----------|-------|
| Image | 11 | 3 | 4 | 0 | 18 |
| Text | 0 | 9 | 2 | 4 | 15 |
| Image+Text (Multimodal) | 5 | 2 | 2 | 1 | 10 |
| Time Series | 2 | 5 | 0 | 0 | 7 |
| Audio | 0 | 1 | 0 | 0 | 1 |
| Video | 1 | 0 | 0 | 0 | 1 |

**Analysis**: Deep CV + Image is the most common combination (11 papers, 20% of dataset), representing the most mature AI+Design research area. Image dominance reflects:
- **Established infrastructure**: ImageNet (2009), ResNet (2015), ViT (2020) provide abundant pre-trained models
- **Natural fit**: Design artifacts (CAD models, sketches, product photos) are inherently visual
- **Data accessibility**: Images are easier to collect, annotate, and share than video or audio

**Multimodal Examples**:
- **Index 167**: BCI for Electric Vehicle HMI - Time Series (EEG) + Image (dashboard)
- **Index 172**: Automating GUI from Design Documents - Image (mockups) + Text (specifications)
- **Index 186**: Emotion Recognition for Indoor Space - Image + Video

**Audio/Video Scarcity**: Only 1 paper each (1.9%) reflects technical barriers (computational cost, storage, privacy concerns, annotation difficulty) rather than lack of application potential. As multimodal foundation models (GPT-4V, Gemini) mature, audio/video design research will likely accelerate in 2025-2026.

**Discussion Point**: Should AI+Design research invest in audio/video modalities (voice UI, video-based user testing) despite technical barriers, or continue optimizing image-based approaches where infrastructure is established?

---

## 3. Critical Gaps & Research Opportunities

The following table consolidates 6 critical research gaps, structured by: Current State | Research Opportunity | Why This Gap Exists | Estimated Impact

| Gap | Current State | Research Opportunity | Why This Gap Exists | Impact |
|-----|---------------|---------------------|---------------------|--------|
| **1. Discovery Phase** | 0 papers (0%) | AI for ethnography (interview analysis, observation videos), trend forecasting (social media/patent mining), opportunity identification (clustering complaints) | **Academic bias**: Exploratory research hard to publish in technical venues (CVPR, NeurIPS)<br>**Methodological mismatch**: Discovery requires open-ended inquiry; AI excels at structured tasks<br>**Venue separation**: Discovery research publishes in CHI, DIS (design), not AI conferences | **Very High**<br>Early-stage automation<br>HCI collaboration needed |
| **2. Delivery Phase** | 0 papers (0%) | AI for lifecycle design (durability prediction, recyclability), deployment monitoring (anomaly detection, degradation alerts), continuous improvement (auto-prioritizing feedback) | **Industry-proprietary**: Deployment data is confidential<br>**Long-term studies**: Requires months/years post-launch<br>**Practical focus**: Less theoretical novelty, harder to publish | **High**<br>Sustainability focus<br>Industry partnerships needed |
| **3. Service Design** | 3 papers (5.6%)<br>All in "Multiple" | Service blueprinting automation, customer journey optimization (predictive analytics), touchpoint design (sentiment analysis), omnichannel experience optimization (RL) | **Community separation**: Service design publishes in business/management venues<br>**Data challenges**: Service experiences harder to quantify than physical products<br>**AI immaturity**: Service design AI less developed than product design AI | **Very High**<br>Interdisciplinary frontier<br>High feasibility |
| **4. Audio/Video Data** | Audio 1 paper (1.9%)<br>Video 1 paper (1.9%) | Voice UI design (speech synthesis + NLP), video-based user testing (emotion recognition, gaze tracking), sonic branding (generative audio), multimodal interaction (speech+gesture+gaze) | **Technical barriers**: Computational expense, storage costs<br>**Data scarcity**: Limited annotated datasets<br>**Privacy concerns**: Recording users raises ethical issues | **High**<br>Multimodal foundation models (GPT-4V) emerging |
| **5. Demographic/Environment Data** | Demographic 0 papers (0%)<br>Environment 0 papers (0%) | **Demographic**: Inclusive design (fairness-aware AI), accessibility (auto-accessible interfaces), cultural customization<br>**Environment**: Sustainable design (eco-optimization), context-aware interfaces (IoT), urban planning | **Ethical concerns**: Demographic data raises fairness/bias issues<br>**Privacy regulations**: GDPR, CCPA restrictions<br>**Environmental complexity**: Requires IoT infrastructure | **Very High**<br>Responsible design<br>Inclusive/sustainable focus |
| **6. Reinforcement Learning** | 1 paper (1.9%)<br>Index 87 only | Human-in-the-loop RL (designer reward feedback), preference learning (inverse RL from designer behavior), multi-armed bandits (A/B testing optimization), adaptive interfaces (personalized UIs) | **Reward signal challenge**: Design lacks clear, quantifiable rewards<br>**Non-stationary preferences**: User preferences change over time<br>**Sample inefficiency**: RL requires many iterations; design exploration is expensive<br>**Benchmark scarcity**: No standard RL environments for design | **Medium**<br>High-risk, high-reward<br>Needs RL experts + designers |

### Gap Analysis Summary

**Structural Pattern**: Gaps cluster in three categories:
1. **Phase-based gaps** (Discovery 0%, Delivery 0%): Early and late design stages completely absent
2. **Discipline-based gaps** (Service 5.6%): Non-product design severely underrepresented
3. **Data/method gaps** (Audio/Video <2%, RL 1.9%, Demographic/Environment 0%): Alternative data types and methods barely explored

**Validation Question**: Are Discovery papers truly absent, or miscoded? The remaining 135 uncoded papers may contain Discovery research under alternative terminology ("exploratory study", "user research", "contextual inquiry"). Recommendation: Manually review "3rd Screening" sheet for these keywords before concluding Discovery is a genuine void.

**Prioritization Insight**: Service Design (5.6%, Very High Impact, High Feasibility) and Multimodal Foundation Models (emerging, Very High Impact, High Feasibility) represent the **most accessible high-impact opportunities** for immediate research investment. Discovery and Delivery phases have Very High Impact but require HCI collaboration or industry partnerships, increasing execution difficulty.

---

## 4. Strategic Recommendations

### High-Impact Research Opportunities

| Opportunity | Current % | Potential Impact | Feasibility | Strategic Priority |
|-------------|-----------|------------------|-------------|-------------------|
| **Discovery Phase AI** | 0% | Very High - Early-stage automation | Medium - Needs HCI collaboration | ⭐⭐⭐ |
| **Service Design AI** | 5.6% | Very High - Journey optimization, blueprinting | High - Data becoming available | ⭐⭐⭐⭐⭐ |
| **Multimodal Foundation Models** | Emerging | Very High - Video/audio interface design | High - GPT-4V, Gemini available | ⭐⭐⭐⭐⭐ |
| **Explainable AI for Design** | 1.9% | High - Designer trust, transparency | High - XAI methods mature | ⭐⭐⭐⭐ |
| **Delivery Phase AI** | 0% | High - Lifecycle, sustainability | Low - Requires industry data | ⭐⭐ |
| **RL for Adaptive Design** | 1.9% | Medium - Personalization, optimization | Medium - Reward engineering hard | ⭐⭐⭐ |

### Next Steps

**For Coding Progress**:
1. Prioritize 2023 papers (currently 5/26 coded, 19.2%) to close temporal gap
2. Search for Discovery/Delivery papers using keywords: "exploratory", "ethnography", "deployment", "post-launch"
3. Validate current classifications through 10-paper sample review

**For Research Direction**:
1. Pursue Service Design AI (high-impact, high-feasibility): Journey optimization, service blueprinting, omnichannel design
2. Leverage multimodal foundation models (GPT-4V, Gemini) for video/audio design applications
3. Advance Explainable AI to bridge Define/Develop methodological divide
4. Establish interdisciplinary teams (AI researchers + service designers, HCI researchers) for Discovery phase research

---

## 5. Appendix: Complete Classification Distribution

| Category | Option | Count | % | Notes |
|----------|--------|-------|---|-------|
| **Design Discipline** | Industrial/Product | 40 | 74% | Spans all AI methods |
| | UI/UX | 7 | 13% | Primarily Deep CV |
| | Service (Multiple) | 3 | 5.6% | Completely absent as standalone |
| **Design Phase** | Develop | 50 | 93% | All AI methods funnel here |
| | Define | 4 | 7% | Traditional ML dominant (3/4) |
| | Discovery | 0 | 0% | **Critical gap** |
| | Delivery | 0 | 0% | **Critical gap** |
| **Data About** | Product | 41 | 76% | Broad category (specs, images, reviews, performance) |
| | Behavior | 6 | 11% | User actions, interactions |
| | Perception | 6 | 11% | User preferences, aesthetics |
| | Physiology | 1 | 1.9% | Index 167 only (BCI) |
| | Demographic | 0 | 0% | **Inclusive design opportunity** |
| | Environment | 0 | 0% | **Sustainable design opportunity** |
| **AI Methods** | Deep CV | 19 | 35% | Most mature, 15+ years infrastructure |
| | Traditional ML | 15 | 28% | Persistent value (interpretability) |
| | Gen AI | 8 | 15% | Emerging (GANs, VAEs, Diffusion) |
| | Deep NLP | 7 | 13% | Text-based design (reviews, specs) |
| | Large Gen AI | 4 | 7% | **All from 2024** (paradigm shift) |
| | RL | 1 | 1.9% | Index 87 only |
| **Data Modality** | Image | 18 | 33% | Natural fit with design artifacts |
| | Text | 15 | 28% | Reviews, specifications, requirements |
| | Multimodal (Image+) | 12 | 22% | Increasingly common |
| | Time Series | 8 | 15% | Performance metrics, sensor data |
| | Audio | 1 | 1.9% | **Technical barriers** |
| | Video | 1 | 1.9% | **Technical barriers** |
| **AI Assistance Types** | Prediction | 33 | 61% | Performance, preference, behavior |
| | Design Generation | 31 | 57% | Generative models, optimization |
| | Decision Making | 20 | 37% | Validation, evaluation, ranking |
| | Sense Making | 15 | 28% | Explanation, visualization |
| | Coordination | 0 | 0% | **Team collaboration absent** |

**Note**: 81% of papers (44/54) provide **multiple assistance types**, indicating AI design tools are multi-functional platforms, not single-purpose algorithms. The most common combination is Design Generation + Prediction (8 papers), where generative models also forecast performance or user response.

---

## Conclusion

This systematic analysis of 54 coded papers reveals an AI+Design research landscape heavily concentrated in **execution-phase applications** (93% Develop) for **physical product design** (74% Industrial), using **mature computer vision methods** (35% Deep CV) on **image data** (56% involve images). The **complete absence** of Discovery (0%) and Delivery (0%) phases, along with severe underrepresentation of Service Design (5.6%), Reinforcement Learning (1.9%), and alternative data modalities (audio/video <2%, demographic/environment 0%) reveals significant research gaps.

These gaps represent **high-impact opportunities** for advancing AI+Design research beyond its current execution-focused paradigm. Particularly promising are Service Design AI (high feasibility, very high impact), Multimodal Foundation Models for audio/video design (GPT-4V, Gemini emerging), and Explainable AI to bridge the methodological divide between early-stage (Define) and execution (Develop) phases.

The **2024 emergence of Large Gen AI** (4 papers, all from 2024) signals a paradigm shift toward general-purpose design assistants, suggesting the field is on the cusp of transformation from task-specific algorithms to conversational, multi-functional design tools. Whether this trend continues toward >50% Large Gen AI by 2026, or whether specialized models persist due to performance and control advantages, remains an open question for the research community.

As coding progresses toward the remaining 135 papers, prioritizing temporal gaps (2023 underrepresentation), underrepresented phases (Discovery, Delivery), and alternative disciplines (Service Design, UI/UX) will provide a more comprehensive understanding of the full AI+Design research landscape.

---

**Document Version**: 2.0
**Analysis Date**: November 6, 2025
**Papers Analyzed**: 54 coded + 189 screening pool
**Completion Status**: 28.6%
**Full data tables and cross-tabulations available in supplementary materials**
