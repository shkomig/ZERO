# מחקר מעמיק: בניית וניהול מערכות LLM מקומיות עם סוכנים אוטונומיים

---

## מבוא - הצורך במערכות מקומיות
מערכות LLM מקומיות מציעות יתרונות:
- פרטיות המידע
- עצמאות מענן
- אפס עלויות API
- שליטה מלאה בהתנהגות המודלים
מודלים מובילים כיום: **DeepSeek-R1-32B**, **Llama-3.1-8B**, **Qwen-2.5-Coder-32B**

---

## חלק 1: ארכיטקטורה
### רכיבי ליבה:
- שכבת מודלים: Ollama, LM Studio
- שכבת סוכנים: Planning/Execution/Retrieval/Tool Agent
- שכבת ניהול קונטקסט: RAG, זיכרון ארוך וקצר טווח
- שכבת קואורדינציה: Message Queue, Central Orchestrator

### דפוסי מבנה:
- Pipeline (רציפה)
- Parallel Execution (במקביל)
- Hierarchical Structure (היררכי)

---

## חלק 2: פריסה מעשית
### התקנת Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run deepseek-r1:7b
ollama run llama3.1:8b
ollama run qwen2.5-coder:32b
```
קוונטיזציה: q4_K_M / q8_0 (יעילות מול איכות)

---

## חלק 3: בניית RAG מקומי
```python
import chromadb
from sentence_transformers import SentenceTransformer
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.create_collection(name="docs")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
documents = ["מסמך 1", "מסמך 2"]
embeddings = embed_model.encode(documents)
collection.add(documents=documents, embeddings=embeddings, ids=["1", "2"])
```

---

## חלק 4: פריימוורקים
### השוואה: LangGraph vs CrewAI vs AutoGen
| קריטריונים | LangGraph | CrewAI | AutoGen |
|-------------|-----------|--------|---------|
| ארכיטקטורה  | גרפית     | צוותית | דיאלוגית|
| התאמה אישית | גבוהה     | גבוהה  | בינונית |
| מדרגיות      | גבוהה     | בינונית| נמוכה    |

---

## חלק 5: סוכן לשליטה במחשב
```python
import pyautogui
import ollama
from PIL import ImageGrab
# שימוש בסיסי בסוכן לפעולות במחשב
```

---

## חלק 6: Prompt Engineering
```txt
[ROLE]
אתה {role}, ביצע רק פעולות {scope}
[CONTEXT]
על פי סוכנים נוספים: ...
[TASK]
משימה: ...
```

---

## חלק 7: Observability
- Distributed Tracing
- מדדים: Success Rate, Latency, Error Propagation
- כלים: OpenTelemetry, Maxim AI, LangSmith

---

## קישורים למחקר מעמיק (PDF)
**Multi-Agent וארכיטקטורה:**
https://arxiv.org/pdf/2509.17489.pdf
https://arxiv.org/pdf/2501.12948.pdf
https://arxiv.org/pdf/2509.10446.pdf
https://arxiv.org/pdf/2504.12330.pdf
https://arxiv.org/pdf/2504.21030.pdf

**RAG ו-Vector DB:**
https://dev.to/jamesbmour/building-a-pdf-chatbot-with-langchain-ollama-and-chroma-a-step-by-step-tutorial-30hd
https://dev.to/kaymen99/build-your-own-local-rag-researcher-with-deepseek-r1-11m

**סוכני שליטה:**
https://arxiv.org/pdf/2504.19678v1.pdf
https://arxiv.org/pdf/2507.19132.pdf
https://www.ijcai.org/proceedings/2024/0711.pdf
https://openreview.net/pdf/43bef34ab8d4a9ad688a8e1b2d0e5ab031f89fb2.pdf

**Prompt Engineering ו-Networking:**
https://arxiv.org/pdf/2402.16713.pdf
https://arxiv.org/pdf/2509.08646.pdf
https://arxiv.org/pdf/2505.02502.pdf

**מדריכים:**
https://www.scribd.com/document/822482053/Hands-on-Guide-Running-DeepSeek-LLMs-Locally
https://www.scribd.com/document/823291319/Install-Deepseek-Locally-1738388118
https://www.scribd.com/document/900996587/Agentic-AI-Framework-Comparison

**כלים:**
- https://ollama.com
- https://github.com/deepseek-ai/DeepSeek-R1
- https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen
- https://www.ibm.com/think/tutorials/llm-agent-orchestration-with-langchain-and-granite
