# AI Services Classification Report

> **분류 기준**: 입출력 모달리티 (Input/Output Modalities)
> **작성일**: 2025-12-04
> **총 서비스**: 38개 | **분류 완료**: 36개 | **미분류**: 2개

---

## 📊 분류 현황 요약

| 분류 | 서비스 수 | 비율 |
|------|----------|------|
| MULTI (멀티모달) | 31개 | 81.6% |
| T2T (Text-to-Text) | 2개 | 5.3% |
| OTHER | 1개 | 2.6% |
| 미분류 | 2개 | 5.3% |

---

## 🏷️ 모달리티 분류 기준

| ID | Name | Description |
|----|------|-------------|
| T2T | Text-to-Text | 텍스트 입력 → 텍스트 출력 (LLM, 챗봇) |
| T2I | Text-to-Image | 텍스트 입력 → 이미지 생성 |
| I2T | Image-to-Text | 이미지 입력 → 텍스트 출력 (비전, OCR) |
| T2V | Text-to-Video | 텍스트 입력 → 비디오 생성 |
| V2T | Video-to-Text | 비디오 입력 → 텍스트 출력 |
| T2A | Text-to-Audio | 텍스트 입력 → 오디오 생성 (TTS) |
| A2T | Audio-to-Text | 오디오 입력 → 텍스트 출력 (STT) |
| T2C | Text-to-Code | 텍스트 입력 → 코드 생성 |
| T23D | Text-to-3D | 텍스트 입력 → 3D 모델 생성 |
| I2I | Image-to-Image | 이미지 입력 → 이미지 출력 (스타일 변환) |
| I2V | Image-to-Video | 이미지 입력 → 비디오 생성 |
| MULTI | Multimodal | 여러 모달리티 지원 |
| OTHER | Other | 기타 특수 목적 |

---

## 🤖 서비스별 상세 분류

### 1. Gemini
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2I` `T2V` `T2A` `A2T` `I2T` `V2T` `T2C` |
| **설명** | Google의 네이티브 멀티모달 AI. Gemini 2.5/3.0은 텍스트/이미지/비디오/오디오 입출력 모두 지원. Veo로 비디오 생성, Gemini Live로 실시간 음성 대화, Jules/CLI로 코드 생성. 1M 토큰 컨텍스트로 전체 비디오 분석 가능 |
| **출처** | https://deepmind.google/models/gemini/ |

---

### 2. Deepseek
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2C` `I2T` `T2I` |
| **설명** | 중국 AI 기업의 LLM 플랫폼. V3/R1(텍스트), Coder(코드), VL2(이미지 분석), Janus-Pro(이미지 생성) 등 다양한 모델 제공. MIT 라이선스 오픈소스. 음성 기능은 VL 2.0에서 예정 |
| **출처** | https://www.deepseek.com/ |

---

### 3. ChatGPT
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2I` `I2T` `T2A` `A2T` `T2C` |
| **설명** | OpenAI의 GPT-4o 기반 멀티모달 AI. 텍스트/이미지/오디오를 단일 모델에서 통합 처리. 2025년 3월 네이티브 이미지 생성, Advanced Voice Mode로 실시간 음성 대화, 50+ 언어 지원. 2025년 8월 GPT-5 출시 |
| **출처** | https://openai.com/index/hello-gpt-4o/ |

---

### 4. NotebookLM
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2A` `A2T` `V2T` `T2V` `I2T` |
| **설명** | Google의 AI 리서치 어시스턴트. Gemini 기반. Audio Overviews(T2A), Video Overviews(T2V), YouTube/오디오 입력(V2T, A2T), PDF 내 이미지 분석(I2T). 50+ 언어 |
| **출처** | https://blog.google/technology/google-labs/notebooklm-new-features-december-2024/ |

---

### 5. Apple Intelligence
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2I` `A2T` `I2T` |
| **설명** | iOS 18/macOS Sequoia 통합 AI 시스템. Writing Tools(T2T), Image Playground/Genmoji/Image Wand(T2I), Siri 음성(A2T), Visual Intelligence로 카메라 기반 분석(I2T). 온디바이스 + Private Cloud Compute. ChatGPT 선택적 통합 |
| **출처** | https://www.apple.com/apple-intelligence/ |

---

### 6. Granola
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `A2T` `T2T` |
| **설명** | AI 회의 노트 앱. 봇 없이 디바이스 오디오 직접 캡처(A2T), GPT-4로 노트 보강/요약(T2T). Mac/Windows/iOS 지원, Zoom/Meet/Teams/Slack 연동. 2025년 5월 $40M Series B ($250M 밸류) |
| **출처** | https://www.granola.ai/ |

---

### 7. Copilot
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2I` `I2T` `T2A` `A2T` `T2C` |
| **설명** | Microsoft의 GPT-4/5 기반 AI 어시스턴트. Designer로 이미지 생성(T2I), Copilot Vision으로 이미지 분석(I2T), Voice로 음성 대화(T2A, A2T), GitHub Copilot으로 코드 생성(T2C). M365 앱 통합, 2025년 무제한 이미지 생성 |
| **출처** | https://en.wikipedia.org/wiki/Microsoft_Copilot |

---

### 8. Grok
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2I` `I2T` `T2V` `T2A` `T2C` |
| **설명** | xAI의 AI 챗봇. Aurora 이미지(T2I), Grok Imagine 비디오+음성(T2V, T2A), 코드 생성(T2C). X 플랫폼 통합 |
| **출처** | https://x.ai/grok/ |

---

### 9. Grammarly
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2A` |
| **설명** | AI 글쓰기 어시스턴트. Compose/Rewrite/Ideate/Reply(T2T). 2025년 Coda 인수. Speechify 통합으로 TTS 기능(T2A). AI grader/proofreader/citation finder |
| **출처** | https://www.grammarly.com/ai |

---

### 10. Craft
| 항목 | 내용 |
|------|------|
| **분류** | T2T |
| **모달리티** | `T2T` |
| **설명** | 문서 작성 앱의 AI 어시스턴트. GPT-4o mini/GPT-4o 기반. 2025년 DeepSeek R1 오프라인 모델, Apple Foundation Models(온디바이스 AI), Apple Writing Tools 지원 추가. 텍스트 생성/요약/번역/브레인스토밍 T2T 특화 |
| **출처** | https://support.craft.do/hc/en-us/articles/8104602502557-About-Craft-AI-Assistant |

---

### 11. Perplexity
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `I2T` `T2I` `A2T` `T2V` `T2A` |
| **설명** | AI 검색 엔진 → 멀티모달 플랫폼. 이미지/비디오 생성(T2I, T2V), 음성 입출력(A2T, T2A), 카메라 분석. GPT-4o/Claude/Gemini 지원 |
| **출처** | https://www.perplexity.ai/changelog/april-11th-2025-product-update |

---

### 12. Claude
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `I2T` `T2C` `A2T` `T2A` |
| **설명** | Anthropic의 AI 어시스턴트. Claude Opus 4/Sonnet 4. 2025년 5월 Voice Mode 출시(A2T, T2A) - 5가지 음성, Google Workspace 통합. 이미지 분석(I2T), 코드 생성(T2C), Computer Use |
| **출처** | https://techcrunch.com/2025/05/27/anthropic-launches-a-voice-mode-for-claude/ |

---

### 13. Claude Code
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2C` |
| **설명** | Anthropic의 에이전틱 코딩 도구. 자연어 지시사항으로 구현 계획 생성(T2T), 코드 생성/편집/테스트(T2C). Subagents/Hooks/Background tasks, Claude Agent SDK |
| **출처** | https://www.anthropic.com/claude-code |
| **부모 서비스** | Claude |

---

### 14. Miro AI
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2I` `I2I` |
| **설명** | Intelligent Canvas 기반. 텍스트→다이어그램(T2I), AI Sidekicks(T2T), 이미지→다이어그램 변환(I2I). 2025년 AI Prototyping |
| **출처** | https://miro.com/intelligent-canvas/ |
| **부모 서비스** | Miro |

---

### 15. Whimsical AI
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2I` `T2T` |
| **설명** | 텍스트→다이어그램(플로우차트/마인드맵/시퀀스/스티키노트) 자동 생성(T2I), 요약 기능(T2T). ChatGPT 통합, Notion/Jira/Slack 연동. ChatGPT에서 Whimsical Diagrams GPT로 직접 생성 가능 |
| **출처** | https://whimsical.com/ai |
| **부모 서비스** | Whimsical |

---

### 16. Figma AI
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2I` `T2T` `I2T` `I2I` |
| **설명** | First Draft 텍스트→디자인(T2I), Text improvements(T2T), Visual Search(I2T), 이미지 배경 제거(I2I). Figma Make 프로토타입 |
| **출처** | https://www.figma.com/ai/ |
| **부모 서비스** | Figma |

---

### 17. Adobe Firefly
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2I` `T2V` `T2A` `T23D` `I2I` `T2C` |
| **설명** | 올인원 크리에이티브 AI. Image Model 5(T2I), 이미지 편집(I2I), Video/Audio Model(T2V, T2A), 3D(T23D), 벡터 그래픽 변환(T2C) |
| **출처** | https://news.adobe.com/news/2025/10/adobe-max-2025-firefly |
| **부모 서비스** | Adobe |

---

### 18. Midjourney
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2I` `T2V` `I2I` `T2A` |
| **설명** | 고품질 이미지 생성. 텍스트→이미지(T2I), 이미지 스타일 참조(I2I), V1 Video(T2V), Draft Mode 음성입력(T2A) |
| **출처** | https://updates.midjourney.com/introducing-our-v1-video-model/ |

---

### 19. DALL-E
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2I` `I2I` |
| **설명** | OpenAI 이미지 생성 모델. 텍스트→이미지(T2I), 이미지 변형/편집(I2I). 2025년 GPT-4o 네이티브 이미지 생성으로 통합 |
| **출처** | https://openai.com/index/dall-e/ |
| **비고** | 2025년 3월부터 GPT-4o에 통합 |

---

### 20. Canva Magic Studio
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2I` `T2V` `T2T` `T2A` `I2I` |
| **설명** | 올인원 디자인. Magic Media 이미지(T2I), 스타일 참조(I2I), 비디오(T2V), AI Voice(T2A), Magic Write(T2T) |
| **출처** | https://www.canva.com/magic/ |
| **부모 서비스** | Canva |

---

### 21. VIZcom
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2I` `I2I` `T23D` |
| **설명** | 산업 디자인 AI 플랫폼(Ford, New Balance 사용). 스케치→렌더링(I2I), 텍스트→이미지(T2I), 2D→3D 변환(T23D, USDZ/AR 내보내기). Fall 2025: Make 3D, Variate, Adjust. Palettes로 개인화 스타일 |
| **출처** | https://docs.vizcom.ai/2d-to-3d-feature |
| **비고** | I2I = Image-to-Image (스케치→렌더링), $26M 펀딩 |

---

### 22. Kling
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2V` `T2I` `I2V` `I2I` `T2T` `T2A` |
| **설명** | 통합 멀티모달 AI. Kling O1 비디오(T2V), 이미지(T2I), 스타일 전송(I2I), 프롬프트(T2T), 오디오 생성(T2A), I2V |
| **출처** | https://www.prnewswire.com/news-releases/kling-o1-launches-as-the-worlds-first-unified-multimodal-video-model-302630630.html |
| **비고** | I2V = Image-to-Video |

---

### 23. Basecamp
| 항목 | 내용 |
|------|------|
| **분류** | OTHER |
| **모달리티** | - |
| **설명** | 프로젝트 관리 도구. 2025년에도 네이티브 AI 기능 없음. Sembly AI(회의록 전사), Relevance AI, Lindy AI 등 서드파티 AI 에이전트 통합으로만 AI 기능 사용 가능 |
| **출처** | https://basecamp.com/extras |
| **비고** | 네이티브 AI 없음 - 서드파티 통합만 (Basecamp Research는 별도 회사) |

---

### 24. Notion AI
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `A2T` `I2T` |
| **설명** | GPT-5/Claude Opus 4.1/o3 기반. 텍스트 생성/요약(T2T), 시스템 오디오 녹음 전사(A2T, Zoom/Meet/Teams 봇 없이), PDF/이미지 분석(I2T). 2025년 9월 Notion 3.0 AI Agents 출시. Business($20) 이상 필요 |
| **출처** | https://www.notion.com/product/ai |
| **부모 서비스** | Notion |

---

### 25. Confluence AI
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2C` |
| **설명** | Atlassian Intelligence 기반. 콘텐츠 생성/요약(T2T), 텍스트→Jira 작업 변환(T2C). 2025년 Rovo AI teammate 출시 |
| **출처** | https://www.atlassian.com/software/confluence/resources/guides/best-practices/atlassian-ai |
| **부모 서비스** | Confluence |

---

### 26. Monday.com AI
| 항목 | 내용 |
|------|------|
| **분류** | T2T |
| **모달리티** | `T2T` |
| **설명** | 2025년 Elevate에서 monday magic/vibe/sidekick 정식 출시. monday agents - AI 스페셜리스트가 업무 end-to-end 실행. Agent Factory로 노코드 AI 에이전트 생성. 텍스트 요약/감정분석/번역/자동분류 |
| **출처** | https://monday.com/w/ai |
| **부모 서비스** | Monday.com |

---

### 27. Slack AI
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `A2T` `T2A` |
| **설명** | 메시지 요약/검색(T2T), Huddles 전사(A2T), Canvas AI 작성 지원(T2A). Agentforce in Slack, 서드파티 AI 통합 |
| **출처** | https://slack.com/features/ai |
| **부모 서비스** | Slack |

---

### 28. AI Studio
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2C` `I2T` `V2T` `A2T` `T2I` `T2V` `T2A` |
| **설명** | Google AI Studio(Gemini 프로토타이핑 플랫폼). 2025년 'Vibe Coding' - 프롬프트→앱 생성, Cloud Run 원클릭 배포. Gemini 멀티모달(텍스트/이미지/비디오/음성 입출력), 이미지/비디오/오디오 생성(T2I, T2V, T2A), Function Calling |
| **출처** | https://ai.google.dev/aistudio |
| **비고** | Google AI Studio로 추정. Azure AI Studio일 경우 재분류 필요 |

---

### 29. String
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2C` |
| **설명** | 자연어로 AI 에이전트 생성 플랫폼. 자연어 요구사항 설명(T2T), 코드 자동 생성/배포(T2C). 2,500+ 앱/API 연동 |
| **출처** | https://string.com/ |

---

### 30. Replit AI
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2C` `T2I` `T2T` |
| **설명** | 2025년 9월 Agent 3 출시 - 200분 자율 실행, 10배 자율성, 자가 테스트/디버깅 루프. 자연어 대화(T2T)→앱/에이전트 생성. 2025년 8월 AI 이미지 생성 추가(아이콘/플레이스홀더). Slack/Notion/Outlook 통합 |
| **출처** | https://replit.com/agent3 |

---

### 31. Cursor
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2C` `I2T` `T2T` |
| **설명** | 2025년 Cursor 2.0 출시($9.9B 밸류). Agent Mode - 8개 병렬 실행, Background Agent(자율 원격). 자연어 대화(T2T)로 코드 지시, Composer 모델(30초 완료). Browser Agent로 스크린샷/UI 분석(I2T). OpenAI/Anthropic/Gemini/xAI 지원 |
| **출처** | https://cursor.com/features |

---

### 32. CX Agents
| 항목 | 내용 |
|------|------|
| **분류** | ❓ 미분류 |
| **모달리티** | - |
| **설명** | - |
| **비고** | 특정 서비스 아님 - 'Customer Experience AI Agents' 일반 카테고리. 2025년 CX 분야 Agentic AI 급성장 중 (Forethought, NICE CXone, SAP Joule, Salesforce Agentforce 등) |

---

### 33. Power Automate AI
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2A` |
| **설명** | 자연어로 플로우 생성/수정(T2T), 문서/커뮤니케이션 요약 자동 생성(T2A). Copilot for Power Automate, AI Builder |
| **출처** | https://learn.microsoft.com/en-us/power-automate/ |
| **부모 서비스** | Microsoft Power Platform |

---

### 34. ClovaNote
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `A2T` `T2T` |
| **설명** | Naver의 AI 회의록 서비스. 음성 전사(A2T, 한/영/일/중), 요약/주제/액션아이템 추출(T2T), 화자 분리. NAVER WORKS ClovaNote 기업용 - 커스텀 AI 모델, 2단계 인증. 감정 인식 업데이트 예정 |
| **출처** | https://help.worksmobile.com/en/use-guides/clovanote/overview/ |

---

### 35. Malirang
| 항목 | 내용 |
|------|------|
| **분류** | T2T |
| **모달리티** | `T2T` |
| **설명** | Wings의 AI 서비스. 한국 기업용 AI 어시스턴트로 추정되나 상세 정보 제한적 |
| **비고** | by Wings - 정보 제한적 |

---

### 36. Stitch
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2I` `I2I` `T2C` `T2T` |
| **설명** | Google Labs의 AI UI 디자인 도구 (I/O 2025 발표, Galileo AI 인수). 자연어 대화(T2T)로 디자인 지시, 텍스트/스케치/와이어프레임→UI 디자인(T2I, I2I), 프론트엔드 코드 생성(T2C). Gemini 2.5 Pro/Flash, Figma 내보내기 |
| **출처** | https://developers.googleblog.com/en/stitch-a-new-way-to-design-uis/ |
| **비고** | stitch.withgoogle.com |

---

### 37. UX Pilot
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2I` `I2T` `T2C` |
| **설명** | AI UX/UI 디자인 도구+Figma 플러그인. 텍스트→UI/와이어프레임(T2I), Predictive Heatmap(사용자 시선 예측, I2T), HTML/CSS/React 코드 내보내기(T2C). Image-to-Design, 디자인 리뷰(접근성/사용성). 디자인 시간 80% 단축 |
| **출처** | https://uxpilot.ai/ |

---

### 38. LLMs (General)
| 항목 | 내용 |
|------|------|
| **분류** | MULTI |
| **모달리티** | `T2T` `T2I` `T2A` `T2V` |
| **설명** | 2025년 주요 LLM들은 멀티모달 지원. 텍스트(T2T), 이미지 생성(T2I, Grok 4), 오디오 출력(T2A, Gemini), 비디오 생성(T2V, Gemini) |
| **비고** | 일반적인 LLM 카테고리 - 2025년 멀티모달 표준화 |

---

## 📈 검증 결과 요약

> **검증 일시**: 2025-12-04
> **검증 방법**: Perplexity API + GPT-4o-mini 기반 자동 검증

| 상태 | 서비스 수 | 비율 |
|------|----------|------|
| ✅ match (일치) | 13개 | 35% |
| ⚠️ partial (부분 일치) | 14개 | 38% |
| 🔄 needs_upgrade (업그레이드됨) | 7개 | 19% |
| ❓ no_detection (검출 실패) | 2개 | 5% |
| ❌ mismatch (불일치) | 1개 | 3% |

### 업데이트된 서비스 (21개)

**needs_upgrade → MULTI로 변경 (7개)**:
- Grammarly: T2T → MULTI [T2T, T2A]
- Claude Code: T2C → MULTI [T2T, T2C]
- DALL-E: T2I → MULTI [T2I, I2I]
- Confluence AI: T2T → MULTI [T2T, T2C]
- String: T2C → MULTI [T2T, T2C]
- Power Automate AI: T2T → MULTI [T2T, T2A]
- LLMs (General): T2T → MULTI [T2T, T2I, T2A, T2V]

**partial → 모달리티 추가 (14개)**:
- NotebookLM, Grok, Perplexity, Miro AI, Figma AI
- Adobe Firefly, Midjourney, Canva Magic Studio, Kling
- Slack AI, AI Studio, Replit AI, Cursor, Stitch

---

*마지막 업데이트: 2025-12-04*
