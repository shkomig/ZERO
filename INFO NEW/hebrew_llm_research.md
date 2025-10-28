# מחקר מעמיק: פתרונות ומודלים מובילים למערכות LLM מקומיות בעברית

## תקציר
המחקר עוסק במודלים ומסגרות להרצת מודלים גדולים של שפה (LLMs) בעברית בצורה מקומית, כולל השוואה ביצועים, דוגמאות מחקרים ותוצאות אמפיריות עדכניות. הדגש הוא על קוד פתוח ותמיכה בחומרה מודרנית (למשל RTX5090).

---

## מודלים מובילים בעברית

| מודל                 | גודל | בסיס      | מפתח/קהילה  | אימון | רישוי | קישור |
|----------------------|------|-----------|-------------|-------|--------|-------|
| DictaLM 2.0          | 7B   | Mistral   | DICTA       | 200B טוקנים (50% עברית, 50% אנגלית) | קוד פתוח | [HuggingFace](https://huggingface.co/dicta-il/dictalm2.0), [arXiv 2407.07080](https://arxiv.org/abs/2407.07080) |
| Hebrew-Mistral-7B    | 7B   | Mistral   | Yam Peleg   | עברית ואנגלית, טוקניזר מורחב | Apache 2.0 | [HuggingFace](https://huggingface.co/yam-peleg/Hebrew-Mistral-7B) |
| Hebrew-Gemma-11B     | 11B  | Gemma-7B  | Yam Peleg   | >500B טוקנים עברית | קוד פתוח | [HuggingFace](https://huggingface.co/yam-peleg/Hebrew-Gemma-11B) |
| Zion Alpha           | 7B   | Mistral   | SicariusSicariiStuff | Fine-tune עברית | קוד פתוח | [HuggingFace](https://huggingface.co/SicariusSicariiStuff/Zion_Alpha) |

---

## דוגמאות מחקר והשוואת ביצועים

### DictaLM 2.0 (2024)
- פותח בשיתוף DICTA, אימון דו-שלבי בשפה ומטא-נתונים בעברית ואנגלית.
- התגבר על קשיי טוקניזציה בעברית: שילוב 1,000 טוקנים חדשים הפחית את כמות הטוקנים למילה מ-5.78 ל-2.76.
- זכה למעמד state-of-the-art בסביבת מבחן עברית ייעודית: תרגום, סנטימנט, Q&A, ואתגר Winograd.
- [arXiv:2407.07080](https://arxiv.org/abs/2407.07080) – מאמר מפורט עם שיטות אימון תומכות.
- [HuggingFace Leaderboard](https://huggingface.co/blog/leaderboard-hebrew) – לוח דירוג רשמי עם תוצאות עדכניות.

### Zion Alpha – Fine-tune עברית
- שיא עולמי: ציון SNLI 84.05 ב-HuggingFace
- תוצאה מובילה בניתוח סנטימנט: 70.3[62]
- דוגמאות חיות, כולל השוואה מול GPT4 ותוצאות תרגום מורכבות.

### Hebrew-Mistral-7B ו-Gemma-11B
- טוקניזציה מורחבת (>64,000 טוקנים), מאומנים על מאות מיליארדי דגימות עברית – תומכים בגנרציה, תרגום וסיכום טקסט.

---

## סוויטת מבחנים רשמית בעברית

| משימה            | דאטה       | גודל    | מדד ביצוע | תיאור | קישור |
|------------------|------------|---------|-----------|--------|--------|
| שאלות-ותשובות    | HeQ        | 1,436   | TLNLS     | הבנת טקסט והסקת מסקנות | [מידע](https://huggingface.co/blog/leaderboard-hebrew) |
| ניתוח סנטימנט    | Sentiment  | 3,000   | דיוק      | זיהוי רגשות בטקסט | [מידע](https://arxiv.org/abs/2407.07080) |
| אתגר Winograd    | WSC        |   --    | דיוק      | הבנת הקשר ושיוך כינויי גוף | [מידע](https://huggingface.co/blog/leaderboard-hebrew) |
| תרגום אנגלית-עברית | TedTalks |   --    | BLEU      | דיוק ושטף בתרגום | [מידע](https://arxiv.org/abs/2407.07080) |
| סיכום טקסט       | חדשות      | 75      | איכות (GPT-4) | סיכום טקסט | [מידע](https://arxiv.org/abs/2407.07080) |

---

## דרישות חומרה להרצה מקומית

| גודל מודל | FP16 | 8 ביט | 4 ביט | GPU מומלץ | הערות |
|-----------|------|-------|------|-----------|------|
| 7B        | ~14GB| ~7GB  | ~4GB | RTX 4090/5090 | מיטוב זיכרון (Quantized) אפשר להריץ על חומרה צרה |
| 11B       | ~22GB| ~11GB | ~6GB | RTX 5090/A100 | להרצה ב-FP16 כדאי >24GB VRAM |
| 32B-70B   | ~70GB| ~35GB | ~20GB| Dual RTX5090 | להרצה מלאה - הכפול VRAM |

---

## מסגרות להרצה מקומית

- **Ollama**: התקנה פשטנית, תמיכה ב-GGUF, ריצה בפשטות על חומרה מגוונת ([שאלות ותשובות](https://github.com/ollama/ollama/blob/main/docs/import.md))
- **llama.cpp**: מיטוב CPU/GPU, תמיכה מלאה בכימות, ממשק CLI קל לתפעול ([github](https://github.com/ggml-org/llama.cpp))
- **LM Studio**: ממשק גרפי פשוט מאוד, תמיכה ברוב המודלים הפתוחים.
- **TensorRT-LLM**: מיטוב ייעודי ל-NVIDIA, תוצאות עדיפות בהרצת Hebrew LLM[34]
- **vLLM**: שרת ביצועים גבוהים, אידיאלי לסביבות ייצור.
- **Hugging Face Transformers**: ספריית הפיתוח הבינלאומית, תמיכה מלאה באימון והרצה.

---

## ביצועי חומרה
- RTX 5090 מריץ Qwen 2.5-Coder-7B במהירות **5,841 טוקנים לשנייה** – פי 1.7 מה-4090.
- מודלים 32B: RTX 5090 מסוגל להריץ אותם על 32GB VRAM (או כפול לקריאות גדולות)[75][73]
- חיסכון בגודל וכמות זיכרון על ידי Quantization (4/8 ביט) מאפשר הרצה גם על חומרה צרה.

---

## תוצאות בולטים
- DictaLM 2.0 מוביל את הדירוג לביצועים בעברית (תרגום, סנטימנט, Q&A)[13][28]
- Zion Alpha קובע שיא בניתוח סנטימנט ועונה בהצלחה על שאלות מורכבות בעברית[62]
- Hebrew-Mistral-7B נותן פתרון ברמה עסקית, תחבורתית וחינוכית למשימות מגוונות.

---

## קישורים רלוונטיים
- [DictaLM 2.0 – HuggingFace](https://huggingface.co/dicta-il/dictalm2.0)
- [DictaLM מחקר - arXiv](https://arxiv.org/abs/2407.07080)
- [Hebrew-Mistral-7B – HuggingFace](https://huggingface.co/yam-peleg/Hebrew-Mistral-7B)
- [Zion Alpha – HuggingFace](https://huggingface.co/SicariusSicariiStuff/Zion_Alpha)
- [Hebrew Leaderboard – HuggingFace](https://huggingface.co/blog/leaderboard-hebrew)
- [TensorRT LLM לכיוונון והטמעה](https://developer.nvidia.com/blog/accelerating-hebrew-llm-performance-with-nvidia-tensorrt-llm/)
- [ערוץ השוואות LLMs](https://huggingface.co/spaces/hebrew-llm-leaderboard/leaderboard)

---

## לסיכום
להרצת LLM בעברית מקומית ברמה מחקרית/עסקית מומלץ לבדוק את DictaLM 2.0 (כולל Fine-tune והורדה מיידית), Hebrew-Mistral-7B, ו-Zion Alpha, דרך מסגרות כמו Ollama/llama.cpp/Transformers. RTX5090 מהווה חומרה מיטבית להרצת מודלים בינוניים-גדולים על קוד פתוח בעברית. כל הכלים, כל הדאטה ופתרונות, וגם benchmark עדכני – מרוכזים כאן.

מחקר זה נותן מענה, דוגמאות, תוצאות והמלצות ליישום LLM מקומי בעברית, כולל קישורים ישירים ומידע אמפירי מלא.
