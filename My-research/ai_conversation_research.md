# מחקר עמוק: שדרוג סוכני שיחה AI לשיחה מופשטת, זורמת וידידותית

הקובץ מרכז שיטות, טכניקות, דוגמאות, המלצות וקישורים לשיפור סוכנים AI מבוססי שיחה, מבוסס על עשרות מחקרים ומקורות עדכניים.

---

## עקרונות יסוד לשיחה איכותית
- שמירה על תגובות קצרות וממוקדות (עד 15 מילים באופן אידיאלי)
- שאילת שאלה אחת בכל פעם והימנעות מעומס קוגניטיבי
- הצגת אפשרויות בחירה ברורות (כפתורים/רשימות)
- שיקוף הקשבה פעילה ע"י חזרה על מה שהמשתמש אמר
- שמירה על עקביות בפרסונה ובסגנון השיחה

## טכניקות מתקדמות
### Fine-tuning ו-SFT
- QLoRA – שיפור ביצועים בעלות נמוכה (60M params)
- Supervised Fine-Tuning – שיפור של 48-75% בביצועי הערכת דיאלוג
- Loss Masking – התאמה של חישוב הלוס
- Chain-of-Thought – סוכן חושב צעד-אחר-צעד (Analysis-first עדיף)

### RAG – Retrieval-Augmented Generation
- איסוף מסמכים רלוונטיים, יצירת embeddings ושימוש בחיפוש סמנטי בזמן אמת למשל:
  - [link](https://kairntech.com/blog/articles/rag-conversational-ai-the-complete-guide-to-building-advanced-ai-chatbots/)
  - [link](https://www.anaconda.com/blog/how-to-build-a-retrieval-augmented-generation-chatbot)

### Prompt Engineering
- Zero/Few-shot prompting – השתמש בדוגמה אחת עד ארבע נבחרות אלגוריתמית
- Chain-of-Thought, Role-based prompting, System prompt structure
- COSTAR framework: הגדרת הקשר, מטרה, סגנון, טון, קהל יעד
- Conversational Prompt Engineering: יצירת prompts אישיים דרך שיחה אינטראקטיבית

### Dialogue State Tracking
- ECDG-DST, Example-Guided QA, Selectively Overwriting Memory
- הבנה ושימור הקשר רב-שלבי, התמודדות עם רב-משתתפים

## הכנת נתוני אימון איכותיים
- מבנה JSONL: שדה role (user/assistant/system) ברור, שילוב system message
- deduplication (ניקוי כפילויות) עם Sentence Transformers
- איזון בין דיוק, גיוון ומורכבות תשובות: Accuracy, Diversity, Complexity
- גודל מומלץ: בסיסי 10k-50k, מקיף 100k-500k, תחום ספציפי 5k-20k

קישורים לנתוני אימון:
- [Curated LLM Datasets](https://github.com/mlabonne/llm-datasets)
- [Conversational AI Datasets](https://github.com/wangxieric/Conversational-AI-Datasets)
- [PersonaChat dataset](https://github.com/facebookresearch/Persona-Chat)
- MSC (Multi-Session Chat), Empathetic Dialogues, WildChat-1M

## הערכת איכות שיחה
### אוטומטית
- Perplexity, BLEU/ROUGE, F1-score, Spearman/Pearson correlation

### אנושית
- Coherence, Relevance, Fluency, Engagingness, Specificity, User satisfaction

### מוכוונת-משימה
- Task Success Rate, Dialog Efficiency, Slot Filling Accuracy

### קישור לפירוט על מטריקות:
- [Dialog evaluation metrics](https://aclanthology.org/2021.eancs-1.3.pdf)
- [Evaluation Metrics For Dialog Systems](https://www.topbots.com/evaluation-metrics-for-dialog-systems/)

## פרסונה ושיחה מותאמת אישית
- שילוב personal facts (יש לי כלב), תכונות אישיות (Big Five)
- שימוש ב- reranking לשיפור עקביות פרסונה בתשובות
- דוגמאות: PersonaChat, MSC, Pandora, PEC
- [Persona-based Dialogue Systems papers](https://github.com/Sahandfer/PersonaPaper)

## כלים פתוחים ומודלים להטמעה
- מסגרות: Botpress, Rasa, LangChain, Distilabel, Curator
- מודלים: Llama 3.1, Mistral, Gemma 2, Qwen 2.5
- כלי סינון נתונים: Argilla, Lilac, SemHash, text-clustering

## טעויות נפוצות
- over-fitting על דאטה מוגבל, prompts ארוכים, הקשר שלא נשמר, חוסר איזון בנתונים
- תגובות פעילות מדי, תשובות ארוכות מדי, אימוג'ים לא מקצועיים, חוסר עקביות בפרסונה
- הסתמכות יתר על מטריקות אוטומטיות, חוסר בדיקות edge cases, אי ביצוע A/B טסט עם משתמשים

## עשרת דגשים קריטיים לפרקטיקה מיטבית
1. התחילו ממודל קטן שעבר fine-tuning לפני הגדלה
2. שלבו RAG למידע עדכני
3. בצעו prompt engineering איטרטיבי עם משוב ממשתמשים
4. הגדרו פרסונה ברורה ועקבית
5. שלבו הערכה אנושית בערכת אוטומטית
6. נטרו שיחות אמיתיות לזיהוי חולשות
7. שמרו על איזון בין תמציתיות ומידעיות
8. אפשרו טיפול שגיאות מובנה והבהרות
9. השתמשו ב-few-shot examples נבחרים
10. עדכנו את הסוכן על פי דאטה ומשוב באופן שוטף

---

## מקורות אקדמיים עיקריים
- [Leveraging LLMs for Dialogue Quality Measurement (ACL 2024)](https://aclanthology.org/2024.naacl-industry.30.pdf)
- [Fine-Tuning LLMs for Multi-Turn Conversations](https://www.together.ai/blog/fine-tuning-llms-for-multi-turn-conversations-a-technical-deep-dive)
- [Context-Aware AI Chatbot Using Transformer-Based Models (2025)](https://www.scitepress.org/Papers/2025/136398/136398.pdf)
- [Persona-Based Conversational AI (2022)](https://arxiv.org/pdf/2212.03699.pdf)
- [Persona-based Dialogue Response Generation (Tokyo/U Tokyo 2024)](https://www.tkl.iis.u-tokyo.ac.jp/new/uploads/publication_file/file/1032/IWSDS2024_CameraReady.pdf)
- [Curated LLM Datasets for Fine-tuning](https://github.com/mlabonne/llm-datasets)
- [Conversational-AI-Datasets](https://github.com/wangxieric/Conversational-AI-Datasets)

---

## דוגמאות JSON לנתונים רב-משתתפיים לפיין-טיונינג
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful AI chatbot."},
    {"role": "user", "content": "שלום, איך עובדים מודלים של מכונה?"},
    {"role": "assistant", "content": "מודלים של מכונה מנתחים מידע..."},
    {"role": "user", "content": "תוכל לתת דוגמא?"},
    {"role": "assistant", "content": "בטח..."}
  ]
}
```

## דוגמה לפיין-טיונינג פרסונה
```json
{
  "persona": "אני אוהב גינון, יש לי כלב, ואני נוטה להיות לא מסכים עם אחרים.",
  "context": "מה דעתך על עצים בגן?",
  "response": "אני מעדיף עצים חזקים שעשויים לעמוד בכלב שובב!"
}
```

---

## הצעות להמשך קריאה ומקורות פתוחים
- [Dialog evaluation metrics](https://aclanthology.org/2021.eancs-1.3.pdf)
- [Best Practices for Voice Agent Design](https://academy.fajutek.com/natural-conversation-voice-agent/)
- [Fine-Tuning LLMs for Multi-Turn Conversations](https://www.together.ai/blog/fine-tuning-llms-for-multi-turn-conversations-a-technical-deep-dive)
- [Curated LLM Datasets](https://github.com/mlabonne/llm-datasets)
- [Conversational AI Datasets Aggregator](https://github.com/wangxieric/Conversational-AI-Datasets)

---