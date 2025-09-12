# 🧠✨ QuizGenius - AI-Powered Learning Revolution

<div align="center">

![QuizGenius Logo](https://img.shields.io/badge/🧠-QuizGenius-6366f1?style=for-the-badge&labelColor=1e293b)

**Transform your content into engaging podcasts and interactive quizzes with AI magic! 🪄**

[![Next.js](https://img.shields.io/badge/Next.js-15.2.4-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.1.1-61dafb?style=flat-square&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178c6?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-06b6d4?style=flat-square&logo=tailwindcss)](https://tailwindcss.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini-2.0%20Flash-ff6b6b?style=flat-square&logo=google)](https://ai.google.dev/)

[🚀 Live Demo](#) • [📖 Documentation](#features) • [🎯 Features](#features) • [⚡ Quick Start](#quick-start)

</div>

---

## 🌟 What is QuizGenius?

QuizGenius is a cutting-edge AI-powered platform that revolutionizes learning by transforming your documents and images into:
- 🎙️ **Interactive Learning Podcasts** from text and PDFs with AI narration
- 📝 **Smart Quizzes** from PDFs and images with OCR
- 🎯 **Personalized Learning Experiences** with real-time feedback

### ✨ The Magic Behind It
Powered by **Google's Gemini 2.0 Flash** AI model and advanced PDF processing with Python, QuizGenius understands your content deeply and creates meaningful podcasts with natural narration and context-aware quiz questions that actually test comprehension - not just metadata!

---

## 🎯 Features That Make Learning Fun

<table>
<tr>
<td align="center">
<img src="https://img.shields.io/badge/🎙️-Podcast%20Generator-purple?style=for-the-badge&logoColor=white" alt="Podcast Generator"/>
<br><br>
<b>AI Podcast Generation</b><br>
Transform text & PDFs into engaging learning podcasts with natural AI narration
</td>
<td align="center">
<img src="https://img.shields.io/badge/📝-Quiz%20Creator-blue?style=for-the-badge&logoColor=white" alt="Quiz Creator"/>
<br><br>
<b>Smart Quiz Generation</b><br>
Create quizzes from PDFs & images with OCR
</td>
<td align="center">
<img src="https://img.shields.io/badge/🎯-Smart%20Scoring-green?style=for-the-badge&logoColor=white" alt="Smart Scoring"/>
<br><br>
<b>Intelligent Scoring</b><br>
Get detailed feedback & explanations
</td>
</tr>
<tr>
<td align="center">
<img src="https://img.shields.io/badge/🔍-PDF%20Processing-orange?style=for-the-badge&logoColor=white" alt="PDF Processing"/>
<br><br>
<b>Advanced PDF Processing</b><br>
Multi-method Python-based extraction with OCR support for scanned documents
</td>
<td align="center">
<img src="https://img.shields.io/badge/🌙-Dark%20Theme-indigo?style=for-the-badge&logoColor=white" alt="Dark Theme"/>
<br><br>
<b>Beautiful Dark Theme</b><br>
Easy on the eyes, stunning design
</td>
<td align="center">
<img src="https://img.shields.io/badge/📱-Responsive-pink?style=for-the-badge&logoColor=white" alt="Responsive"/>
<br><br>
<b>Mobile Responsive</b><br>
Perfect on any device
</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites
- 📦 Node.js 18+ 
- 🐍 Python 3.x (for advanced PDF processing)
- 🔑 Google Gemini API Key ([Get yours here](https://ai.google.dev/))

### 1️⃣ Clone & Install
```bash
git clone https://github.com/yourusername/quizgenius.git
cd quizgenius
npm install
```

### 2️⃣ Setup Environment
```bash
# Create environment file
cp .env.example .env.local

# Add your API key to .env.local
NEXT_PUBLIC_GEMINI_API_KEY=your_gemini_api_key_here
```

### 3️⃣ Setup Python Dependencies 
```bash
# Install Python dependencies for advanced PDF processing
pip install -r scripts/requirements.txt

# Test the setup
python scripts/test_setup.py
```

### 4️⃣ Launch! 🚀
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) and start creating! ✨

---

## 🛠️ Tech Stack

<div align="center">

| Frontend | AI/ML | Styling | Tools |
|----------|--------|---------|-------|
| ![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white) | ![Google AI](https://img.shields.io/badge/Gemini%202.0-4285F4?style=for-the-badge&logo=google&logoColor=white) | ![Tailwind](https://img.shields.io/badge/Tailwind-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white) | ![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white) |
| ![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) | ![OCR](https://img.shields.io/badge/OCR-Vision%20AI-FF6B6B?style=for-the-badge) | ![Radix UI](https://img.shields.io/badge/Radix%20UI-161618?style=for-the-badge&logo=radix-ui&logoColor=white) | ![ESLint](https://img.shields.io/badge/ESLint-4B3263?style=for-the-badge&logo=eslint&logoColor=white) |

</div>

---

## 🎨 How It Works

```mermaid
graph LR
    A[📄 Upload PDF] --> B[🐍 Python PDF Processing]
    B --> C[🤖 AI Analysis]
    C --> D[🎙️ Podcast Generation]
    C --> E[📝 Quiz Creation]
    E --> F[🎯 Take Quiz]
    F --> G[📊 Smart Scoring]
    G --> H[💡 Learn & Improve]
```

### The QuizGenius Process:
1. **📄 Advanced PDF Processing**: Multi-method Python extraction (PyMuPDF, pdfplumber, OCR)
2. **🤖 AI Content Analysis**: Gemini AI reads and understands your documents deeply
3. **🎙️ Podcast Generation**: Creates engaging audio content with natural AI narration
4. **📝 Quiz Creation**: Generates context-aware questions about actual content
5. **💬 Detailed Feedback**: Provides explanations and references to source material

---

## 📁 Project Structure

```
quizgenius/
├── 🏠 app/                    # Next.js app directory
│   ├── 📄 layout.tsx         # Root layout with metadata
│   ├── 🏡 page.tsx           # Main page composition
│   └── 🔗 api/               # API routes for backend
│       ├── 📄 extract-pdf/   # PDF processing endpoint
│       ├── 🎙️ generate-podcast/ # Podcast generation
│       └── 🔊 text-to-speech/ # Audio synthesis
├── 🧩 components/            # Reusable React components
│   ├── 🎭 ui/                # Base UI components
│   ├── 🎙️ podcast-generator-section.tsx
│   ├── 📝 quiz-generator-section.tsx
│   └── 🎨 *-section.tsx      # Feature sections
├── 🐍 scripts/               # Python processing scripts
│   ├── 📄 pdf_text_extractor.py # Multi-method PDF extraction
│   └── 🔧 requirements.txt   # Python dependencies
├── 📚 lib/                   # Utility libraries
│   └── 🤖 gemini.ts          # AI integration
├── 🔧 .env.local             # Environment variables (private)
└── 📖 README.md              # You are here! 👋
```

---

## 🔒 Security Features

<div align="center">

| Security Feature | Status | Description |
|------------------|---------|-------------|
| 🔐 **API Key Protection** | ✅ Secure | Environment variables only |
| 🚫 **Git Ignore** | ✅ Active | Prevents accidental commits |
| 🛡️ **Runtime Validation** | ✅ Protected | Validates configuration |
| 🔍 **Error Handling** | ✅ Robust | Graceful failure management |

</div>

---

## 🎮 Usage Examples

### 📝 Creating a Quiz
```typescript
// Upload a PDF or image
const quiz = await generateQuiz(file, {
  numberOfQuestions: 5,
  difficulty: 'medium',
  questionTypes: ['multiple-choice', 'true-false']
});

// Take the quiz and get instant feedback! 🎯
```

### 🎙️ Generating Podcasts
```typescript
// From text or PDF content
const podcast = await generateLearningPodcast(content, {
  style: 'conversational',
  voice: 'professional',
  duration: 'auto'
});
```

---

## 🌈 Screenshots

<div align="center">

### 🏠 Beautiful Landing Page
*Coming Soon: Screenshots of the stunning dark theme interface*

### 📝 Quiz Interface
*Coming Soon: Interactive quiz generation and taking experience*

### 🎙️ Podcast Generation
*Coming Soon: Screenshots of AI-powered podcast creation with natural narration*

</div>

---

## 🤝 Contributing

We love contributions! Here's how you can help make QuizGenius even better:

1. 🍴 **Fork** the repository
2. 🌱 **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. 💾 **Commit** your changes: `git commit -m 'Add amazing feature'`
4. 📤 **Push** to the branch: `git push origin feature/amazing-feature`
5. 🎉 **Open** a Pull Request

### 🎯 Areas for Contribution
- 🎨 UI/UX improvements
- 🤖 AI prompt optimization
- 📱 Mobile responsiveness
- 🌐 Internationalization
- 🧪 Testing coverage

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- 🤖 **Google Gemini AI** - For powering our intelligent content generation
- 🐍 **Python PDF Libraries** - PyMuPDF, pdfplumber, Tesseract OCR for robust document processing
- 🎙️ **Google Text-to-Speech** - For natural audio synthesis
- ⚛️ **React & Next.js** - For the amazing development experience
- 🎨 **Tailwind CSS** - For making styling a breeze
- 🔧 **Radix UI** - For accessible component primitives

---

## 📞 Support & Contact

<div align="center">

**Need help? We're here for you!** 💖

[![GitHub Issues](https://img.shields.io/badge/Issues-GitHub-green?style=for-the-badge&logo=github)](https://github.com/yourusername/quizgenius/issues)
[![Discord](https://img.shields.io/badge/Discord-Community-7289da?style=for-the-badge&logo=discord)](https://discord.gg/your-discord)
[![Email](https://img.shields.io/badge/Email-Support-red?style=for-the-badge&logo=gmail)](mailto:support@quizgenius.com)

</div>

---

<div align="center">

### 🌟 Star us on GitHub!

**If QuizGenius helped you learn better, give us a star! ⭐**

<!-- [⭐ **STAR THIS REPO** ⭐](https://github.com/yourusername/quizgenius) -->

---

**Made with ❤️ by developers who believe learning should be fun and accessible to everyone.**

🧠✨ **QuizGenius - Where AI meets Education!** ✨🧠

</div>