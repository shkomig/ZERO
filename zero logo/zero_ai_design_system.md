
# 🎨 ZERO AI – Web Design System

עיצוב אחיד לממשק אינטרנטי תואם ללוגו **ZERO AI – Desktop Agent**.

---

## 🎨 צבעים ראשיים

| שימוש | HEX | תיאור |
|-------|------|--------|
| **Primary** | `#00BFFF` | כחול נאון בוהק (התואם ל־Z בלוגו) |
| **Secondary** | `#007ACC` | כחול עמוק יותר ללחצנים/הצללות |
| **Background** | `#0A0F1F` | כחול־שחור כהה מאוד, רקע דיגיטלי חלק |
| **Text Primary** | `#E0F7FF` | תכלת לבנה זוהרת לקריאות גבוהה |
| **Text Secondary** | `#A0C8FF` | טקסט הסבר או תוויות (Labels) |
| **Highlight / Accent** | `#33FFFF` | הדגשות, קווים או אנימציות בהירות |
| **Error / Warning** | `#FF3366` | אדום נאון לאזהרות או שגיאות |

---

## 🖋️ פונטים מומלצים

| שימוש | פונט | גיבוי | סגנון |
|-------|-------|--------|--------|
| **כותרות (Headings)** | `Orbitron` | `sans-serif` | עתידני ונקי |
| **טקסט כללי (Body)** | `Inter` | `Arial, sans-serif` | קריא, מאוזן |
| **קוד / טכני** | `JetBrains Mono` | `monospace` | מושלם לשורות קוד |

**שימוש מומלץ:**  
```css
font-family: 'Inter', 'Orbitron', sans-serif;
```

---

## 🧩 אלמנטים גרפיים

### כפתורים (Buttons)
```css
background: linear-gradient(90deg, #00BFFF, #007ACC);
color: #E0F7FF;
border-radius: 12px;
box-shadow: 0 0 15px #00BFFF66;
transition: 0.3s;
```
**Hover:**
```css
background: #33FFFF;
box-shadow: 0 0 25px #33FFFF99;
```

### כרטיסים (Cards)
```css
background: #0F1629;
border: 1px solid #00BFFF33;
border-radius: 16px;
box-shadow: 0 0 20px #00BFFF11;
```

### Navbar / Sidebar
```css
background: rgba(10, 15, 31, 0.9);
backdrop-filter: blur(10px);
border-bottom: 1px solid #007ACC44;
```

### אנימציית Glow
```css
@keyframes glow {
  0% { text-shadow: 0 0 5px #00BFFF; }
  50% { text-shadow: 0 0 20px #33FFFF; }
  100% { text-shadow: 0 0 5px #00BFFF; }
}
```

---

## 🧠 מבנה טיפוגרפי לדף Web

```css
body {
  background-color: #0A0F1F;
  color: #E0F7FF;
  font-family: 'Inter', sans-serif;
  line-height: 1.6;
}

h1, h2, h3 {
  font-family: 'Orbitron', sans-serif;
  color: #33FFFF;
  letter-spacing: 1px;
}

a {
  color: #00BFFF;
  text-decoration: none;
}

a:hover {
  color: #33FFFF;
  text-shadow: 0 0 8px #00BFFF;
}
```

---

**Created for ZERO AI – Desktop Agent Design System**
