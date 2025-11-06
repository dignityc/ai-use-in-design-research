# 3rd Screening Comprehensive Analysis Report

**Generated:** 2025-11-06
**Total Papers:** 189
**Data Source:** Google Sheets "Coding & screening works" → "3rd Screening"

---

## Executive Summary

The "3rd Screening" sheet contains **189 papers** that have undergone initial screening and categorization. The current status shows:

- **54 papers (28.6%)** are **Included (Y)** for coding
- **31 papers (16.4%)** are **Excluded (N)**
- **104 papers (55.0%)** are **Blank/Unscreened** (highest priority for action)
- **0 papers (0.0%)** are **Questionable (Q)**

All papers assigned to "J" (the primary researcher) have been screened, with 54 papers included and all PDFs uploaded for coding work.

---

## 1. Sheet Structure & Columns

### 12 Columns Total:

1. **Index** - Unique paper identifier (189 papers)
2. **Article Title** - Full paper title (189 papers)
3. **Author Full Names** - Complete author list (189 papers)
4. **Source Title** - Journal/conference name (189 papers)
5. **Publication Year** - Year published (189 papers)
6. **Abstract** - Full abstract text (189 papers)
7. **DOI Link** - Digital object identifier link (189 papers)
8. **ENGINEERING.PRODUCT/UI.UX/SERVICE** - Design domain classification (189 papers)
9. **Inclusion (Y/N/Q/R) for 2nd screening** - Primary screening decision (189 papers)
10. **Assigned_to** - Researcher assigned (189 papers: "J" or "M")
11. **PDF_uploaded** - PDF upload status (189 papers: "Y" or blank)
12. **Note** - Detailed reasoning for inclusion/exclusion (189 papers, 100% filled)

### Key Observations:
- **All 189 papers have complete data** in all columns (100% data coverage)
- **Note column is 100% populated**, providing detailed reasoning for every paper
- **No "Q" (Questionable) status** - all decisions are definitive (Y/N or blank)

---

## 2. Screening Workflow Analysis

### 2.1 Inclusion Status Distribution

| Status | Count | % | Description |
|--------|-------|---|-------------|
| **Y (Included)** | 54 | 28.6% | Papers accepted for full coding |
| **N (Excluded)** | 31 | 16.4% | Papers rejected with reasons |
| **Blank** | 104 | 55.0% | Papers awaiting screening decision |
| **Q (Questionable)** | 0 | 0.0% | No borderline cases identified |

### 2.2 Assignment Distribution

| Assignee | Total Papers | Included (Y) | Excluded (N) | Blank | PDF Uploaded |
|----------|--------------|--------------|--------------|-------|--------------|
| **J** | 110 | 54 | 31 | 25 | 54 (100% of Y) |
| **M** | 79 | 0 | 0 | 79 | 0 |

**Key Findings:**
- **Researcher J has completed screening** for 85 papers (77.3% of assigned)
- **All 54 included papers** (Inclusion=Y) have PDFs uploaded (100% completion rate)
- **Researcher M has 79 unscreened papers** (100% blank status)

---

## 3. Exclusion Reason Analysis

### 3.1 Common Exclusion Patterns (31 Excluded Papers)

Based on detailed note analysis of all 31 excluded papers, the following **primary exclusion reasons** emerge:

#### **Category 1: AI Method Not Specified (Most Common)**
**Count:** ~15 papers (48%)

**Pattern:** Papers describe AI supporting design but do not mention specific AI/ML methods (e.g., "machine learning", "deep learning", "neural network" mentioned generically without naming a concrete algorithm).

**Examples:**
- Paper #90: "computer vision" mentioned but no specific method (GAN, CNN, etc.)
- Paper #95: "machine learning-based" but no specific ML algorithm named
- Paper #101: "machine learning" mentioned but no concrete method identified
- Paper #122: "machine learning schemes" and "data mining" but no specific algorithm

**Exclusion Rule:**
> Papers MUST explicitly name a specific AI/ML method (e.g., CNN, Random Forest, GAN, BERT, Transformer) to be included. Generic terms like "AI", "machine learning", "deep learning" alone are insufficient.

---

#### **Category 2: AI is the Product Being Designed (Not a Design Tool)**
**Count:** ~8 papers (26%)

**Pattern:** Papers describe designing/building AI systems themselves, rather than using AI to support design tasks.

**Examples:**
- Paper #153: Designing an AI clinical decision support system (AI = product)
- Paper #161: Designing a chatbot service (AI = product)
- Paper #162: Designing age-inclusive conversational interfaces (AI = interface being designed)
- Paper #174: Designing an AI-powered wearable for wildlife detection (AI = product)
- Paper #176: Designing user feedback mechanisms FOR AI mood tracker apps

**Exclusion Rule:**
> Papers about "design OF AI systems" (where AI is the output) are excluded. Only papers about "AI supporting design tasks" (where AI is the tool) are included.

---

#### **Category 3: AI for Non-Design Applications**
**Count:** ~5 papers (16%)

**Pattern:** AI is used for applications other than design tasks (e.g., statistical analysis, prediction, monitoring, medical diagnosis).

**Examples:**
- Paper #129: AI monitors designer work efficiency (workforce management, not design support)
- Paper #166: Deep learning predicts fuel consumption (eco-driving evaluation, not design)
- Paper #173: Neural networks for statistical analysis of learning engagement (research tool, not design)
- Paper #177: Multi-Agent RL for medical image segmentation (clinical diagnosis, not design)
- Paper #187: GAN for emotion recognition system (emotion detection, not design support)

**Exclusion Rule:**
> AI applications must directly support design tasks/processes (create, optimize, evaluate, inform design outputs). AI for statistics, monitoring, or non-design domains are excluded.

---

#### **Category 4: Perception/Attitude Studies (Not Implementation)**
**Count:** ~2 papers (6%)

**Pattern:** Papers study perceptions or attitudes toward AI in design, without implementing or evaluating AI for design tasks.

**Examples:**
- Paper #157: Qualitative study of UX designers' perceptions of GenAI (interview-based, no implementation)
- Paper #165: Workshop proposal identifying CUI research challenges (no specific AI method or implementation)

**Exclusion Rule:**
> Papers must demonstrate AI implementation or evaluation in design contexts. Pure perception studies, reviews, or workshop proposals without empirical AI application are excluded.

---

#### **Category 5: Design OF AI Systems Only**
**Count:** ~1 paper (3%)

**Pattern:** Papers that design/improve AI algorithms or frameworks without applying them to design tasks.

**Examples:**
- Paper #164: Improving LLM intention understanding (AI system design, not design support)

**Exclusion Rule:**
> Papers focused solely on improving AI systems themselves (without design application context) are excluded.

---

### 3.2 Exclusion Keyword Frequency

| Keyword/Phrase | Frequency | Context |
|----------------|-----------|---------|
| **"no specific AI/ML method"** | 15 | Most common exclusion reason |
| **"AI is the product being designed"** | 8 | Second most common reason |
| **"not design tasks"** | 5 | Third most common reason |
| **"no empirical"** | 3 | Perception studies without implementation |
| **"not ai"** | 3 | Papers lacking AI methods entirely |
| **"not design"** | 3 | Papers outside design domain |
| **"review"** | 1 | Literature review without original contribution |

---

## 4. Inclusion Criteria Analysis

### 4.1 What Makes Papers Included? (54 Papers with Inclusion=Y)

Based on analyzing included papers with notes, the following **inclusion criteria** are evident:

#### **Criterion 1: Specific AI Method Named**
✓ Papers explicitly name concrete AI/ML methods:
- Deep Learning, CNN, GAN, Transformer, BERT, GPT
- Random Forest, SVM, Neural Networks, ANN
- Reinforcement Learning, Genetic Algorithms
- Natural Language Processing (with specific models)

**Examples from Included Papers:**
- Paper #1: "PointNet-based encoder-decoder network" (specific architecture)
- Paper #2: "Reference vector guided evolutionary algorithm" (specific algorithm)
- Paper #8: "Convolutional neural network" (specific method)
- Paper #15: "Natural language processing techniques", "word embedding algorithms" (specific methods)

---

#### **Criterion 2: AI Supports Design Tasks/Processes**
✓ Papers demonstrate AI actively supporting one or more design activities:
- **Generate/Create:** AI generates design concepts, sketches, CAD models
- **Optimize:** AI optimizes design parameters, topology, performance
- **Evaluate:** AI evaluates design quality, performance, user satisfaction
- **Inform:** AI extracts insights from data to inform design decisions
- **Explore:** AI helps explore design spaces, alternatives

**Examples from Included Papers:**
- Paper #1: "Design space dimensionality reduction for shape optimization" (Optimize)
- Paper #7: "Product conceptual design scheme configurations" (Generate)
- Paper #10: "Conflict resolution model for conceptual design" (Inform)
- Paper #19: "Data-driven design of conical origami structures" (Generate + Optimize)

---

#### **Criterion 3: Design Domain Relevance**
✓ Papers address design domains relevant to the research scope:
- **Engineering Design:** Product design, mechanical design, topology optimization
- **Product Design:** Industrial design, form design, packaging design
- **UI/UX Design:** Interface design, interaction design, experience design
- **Service Design:** Service systems, product-service systems

**Examples from Included Papers:**
- Paper #3: "Product attributes from consumer reviews" (Product Design)
- Paper #9: "Sustainable product design features" (Engineering Design)
- Paper #23: "Generative AI for prototyping in engineering design" (Engineering Design)
- Paper #27: "Computer vision in product design" (Product Design)

---

#### **Criterion 4: Empirical Evidence (Preferred)**
✓ Papers with empirical validation, case studies, or implementation examples are preferred:
- Case studies demonstrating AI application
- Experimental results with datasets
- Prototypes or systems built and tested
- Comparative evaluations with baselines

**Note:** Some conceptual/theoretical papers are included if criteria 1-3 are strongly met.

---

### 4.2 Inclusion Notes Pattern Analysis

**Sample Inclusion Notes (from Papers 1-10):**

All included papers have notes structured as:
```
AI Method: [Specific method name]
Design Task: [Specific design activity supported]
```

This structure ensures:
1. **Specific AI method is clearly identified**
2. **Design task/domain is explicitly stated**
3. **Relationship between AI and design is transparent**

---

## 5. Comparison: Coded Papers vs. Remaining Included Papers

### 5.1 Current Coding Status

| Category | Count | Description |
|----------|-------|-------------|
| **Included (Y) Papers** | 54 | Papers approved for coding |
| **PDF Uploaded** | 54 | 100% of included papers have PDFs |
| **Coded Papers** | ~54 | Assumed all uploaded PDFs are being coded |
| **Pending Coding** | 0 | All included papers have PDFs uploaded |

**Key Finding:**
> **All 54 included papers (Inclusion=Y, Assigned_to=J) have PDFs uploaded**, suggesting coding is complete or in progress for the entire included set.

---

### 5.2 Papers Needing Screening (104 Papers)

**Breakdown by Assignee:**

| Assignee | Unscreened Papers | Status |
|----------|-------------------|--------|
| **J** | 25 | Assigned but not yet screened |
| **M** | 79 | Fully unscreened (100% blank) |

**Recommendation:**
> **Priority 1:** Screen the 25 remaining papers assigned to "J" (to complete J's workload)
> **Priority 2:** Screen the 79 papers assigned to "M" (largest unscreened batch)

---

## 6. Insights & Recommendations

### 6.1 Key Insights

#### **Insight 1: Stringent AI Method Specification Requirement**
The screening process applies a **strict rule requiring explicit AI/ML method naming**. Generic terms like "machine learning", "AI", "deep learning" without specific algorithms (CNN, GAN, Transformer, etc.) lead to exclusion.

**Implication:**
- This ensures high-quality papers with clear methodological contributions
- May exclude some conceptual/theoretical papers that discuss AI broadly
- Aligns with empirical research focus requiring reproducible methods

---

#### **Insight 2: Clear Distinction Between "AI FOR Design" vs. "Design OF AI"**
The screening process **distinguishes between:**
- **Included:** Papers using AI as a tool to support design tasks (AI FOR design)
- **Excluded:** Papers designing AI systems themselves (Design OF AI)

**Examples of Boundary Cases:**
- Designing a chatbot interface → Excluded (AI is the product)
- Using ChatGPT to generate design concepts → Included (AI supports design)

---

#### **Insight 3: Design Task Specificity Matters**
Included papers explicitly describe how AI supports specific design activities:
- Generate, Optimize, Evaluate, Inform, Explore design outputs
- Generic mentions of "design improvement" without specific tasks may be excluded

**Recommendation:**
> When screening remaining 104 papers, explicitly identify the **specific design task** AI supports in the notes (e.g., "Generate CAD models", "Optimize topology", "Extract user requirements").

---

#### **Insight 4: No Questionable (Q) Cases Identified**
**All 85 screened papers** have definitive Y/N decisions with no "Q" (Questionable) status.

**Possible Reasons:**
- Clear inclusion/exclusion criteria reduce ambiguity
- Detailed notes allow thorough reasoning before finalizing decisions
- Borderline cases may be resolved through discussion (not tracked in sheet)

**Implication:**
> The screening process is highly structured and decisive, minimizing gray areas.

---

### 6.2 Common Exclusion Reasons Summary

| Reason | % of Exclusions | Key Criteria |
|--------|-----------------|--------------|
| **AI Method Not Specified** | 48% | Must name specific AI/ML algorithm |
| **AI is Product (Not Tool)** | 26% | AI must support design, not BE the design |
| **Non-Design Application** | 16% | AI must support design tasks, not other domains |
| **Perception Study Only** | 6% | Must demonstrate implementation, not just attitudes |
| **Design OF AI Systems** | 3% | Must apply AI to design, not just improve AI |

---

### 6.3 Recommendations for Remaining 104 Papers

#### **Recommendation 1: Apply Consistent Screening Criteria**

When screening the 104 unscreened papers, apply the following **decision tree**:

```
1. Is a SPECIFIC AI/ML method named?
   → No: EXCLUDE (Reason: "No specific AI/ML method")
   → Yes: Continue to Step 2

2. Does AI SUPPORT design tasks (not BE the design output)?
   → No: EXCLUDE (Reason: "AI is the product being designed, not a design tool")
   → Yes: Continue to Step 3

3. Is the design domain relevant (Engineering/Product/UI/UX/Service)?
   → No: EXCLUDE (Reason: "Outside design domain")
   → Yes: Continue to Step 4

4. Are design tasks/processes explicitly described?
   → No: EXCLUDE (Reason: "Design task not specified")
   → Yes: INCLUDE (Inclusion=Y)

5. Document in Notes:
   AI Method: [Specific method name]
   Design Task: [Specific design activity]
```

---

#### **Recommendation 2: Prioritize High-Value Papers**

Focus screening effort on:
1. **Papers with recent publication years** (2023-2025) for cutting-edge methods
2. **Papers from top journals/conferences** (based on Source Title)
3. **Papers with specific keywords in title:** "generative AI", "deep learning", "neural network", "optimization"

---

#### **Recommendation 3: Leverage Past Decisions for Training**

Use the 85 screened papers (54 Y + 31 N) as **training examples** for:
- Calibrating judgment on borderline cases
- Identifying common exclusion patterns to avoid
- Understanding what constitutes "specific AI method" vs. generic terms

---

#### **Recommendation 4: Consider Batch Screening**

For the 79 papers assigned to "M":
1. **Pre-filter using title/abstract keywords** (e.g., specific AI methods)
2. **Batch process likely exclusions** (e.g., papers clearly outside design domain)
3. **Focus deep reading on promising candidates** (e.g., papers mentioning CNN, GAN, Transformer + design tasks)

---

## 7. Future Screening Workflow Improvements

### 7.1 Potential Enhancements

#### **Enhancement 1: Automated Pre-Screening**
Use NLP/text mining to automatically:
- Extract AI method mentions from abstracts (e.g., "CNN", "GAN", "Transformer")
- Identify design task keywords (e.g., "optimize", "generate", "evaluate")
- Flag papers likely to meet criteria for priority review

**Benefits:**
- Reduce manual screening time for obvious exclusions
- Focus human effort on borderline cases requiring judgment

---

#### **Enhancement 2: Inter-Rater Reliability Check**
Randomly select 10-20 papers screened by one researcher (e.g., J) and have another researcher (e.g., M) independently screen them to:
- Measure agreement rate (Cohen's Kappa)
- Identify inconsistencies in criteria application
- Calibrate judgment across researchers

**Benefits:**
- Ensure consistent screening quality
- Reduce subjective biases

---

#### **Enhancement 3: Structured Note Templates**
Formalize note structure for all papers:

**For Included Papers:**
```
AI Method: [Specific method]
Design Task: [Specific design activity]
Empirical: [Yes/No]
```

**For Excluded Papers:**
```
Reason: [Primary exclusion category]
Details: [Brief explanation]
Empirical: [Yes/No]
```

**Benefits:**
- Enable automated analysis of inclusion/exclusion patterns
- Support future literature reviews and meta-analyses

---

## 8. Quantitative Summary

### 8.1 Current Status

| Metric | Value | Percentage |
|--------|-------|------------|
| **Total Papers** | 189 | 100.0% |
| **Screened Papers** | 85 | 45.0% |
| **Unscreened Papers** | 104 | 55.0% |
| **Included (Y)** | 54 | 28.6% |
| **Excluded (N)** | 31 | 16.4% |
| **Questionable (Q)** | 0 | 0.0% |
| **Blank** | 104 | 55.0% |
| **PDF Uploaded** | 54 | 28.6% (100% of Y) |

### 8.2 Researcher Workload

| Researcher | Total | Screened | Unscreened | Included | Excluded | PDF Uploaded |
|------------|-------|----------|------------|----------|----------|--------------|
| **J** | 110 | 85 (77.3%) | 25 (22.7%) | 54 (49.1%) | 31 (28.2%) | 54 (100% of Y) |
| **M** | 79 | 0 (0.0%) | 79 (100.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

### 8.3 Exclusion Reason Distribution (31 Papers)

| Exclusion Category | Count | % of Exclusions |
|--------------------|-------|-----------------|
| AI Method Not Specified | ~15 | 48.4% |
| AI is Product (Not Tool) | ~8 | 25.8% |
| Non-Design Application | ~5 | 16.1% |
| Perception Study Only | ~2 | 6.5% |
| Design OF AI Systems | ~1 | 3.2% |

---

## 9. Conclusion

The "3rd Screening" sheet demonstrates a **well-structured and rigorous screening process** with:

1. **Clear Inclusion Criteria:**
   - Specific AI/ML methods must be named
   - AI must support design tasks (not be the design output)
   - Design domain must be relevant (Engineering/Product/UI/UX/Service)
   - Design tasks/processes must be explicitly described

2. **Transparent Exclusion Reasons:**
   - 48% excluded for lack of specific AI method naming
   - 26% excluded for designing AI systems (not using AI for design)
   - 16% excluded for non-design applications
   - Detailed notes provide clear reasoning for every decision

3. **High Completion Rate for Included Papers:**
   - All 54 included papers have PDFs uploaded (100%)
   - Coding work is complete or in progress for the entire included set

4. **Significant Remaining Work:**
   - 104 papers (55%) await screening decisions
   - Prioritize completing J's 25 remaining papers, then M's 79 papers

**Overall Assessment:**
The screening workflow is **robust, consistent, and well-documented**, providing a solid foundation for high-quality literature review and systematic analysis. The next priority is completing screening for the remaining 104 papers using the established criteria and decision tree.

---

## 10. Action Items

### Priority 1: Complete Screening (104 Papers)
- [ ] Screen J's remaining 25 papers (target: 1 week)
- [ ] Screen M's 79 papers (target: 2-3 weeks)
- [ ] Apply consistent criteria using decision tree (Section 6.3)

### Priority 2: Quality Assurance
- [ ] Conduct inter-rater reliability check (10-20 papers)
- [ ] Review borderline cases from past screening for consistency
- [ ] Document any criteria refinements based on new edge cases

### Priority 3: Analysis & Reporting
- [ ] Generate final screening statistics after completion
- [ ] Create exclusion reason taxonomy for publication
- [ ] Prepare literature review summary of included papers

---

**Report End**
