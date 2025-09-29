# 🔐 API Key Setup for QuizGenius

## Security Notice
Your API key is now properly secured! The hardcoded key has been removed from the code.

## Setup Instructions

### 1. Create Environment File
Create a new file called `.env.local` in the root directory of your project:

```bash
# In the project root (same directory as package.json)
touch .env.local
```

### 2. Add Your API Key
Open `.env.local` and add your Gemini API key:

```env
NEXT_PUBLIC_GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Get Your API Key
If you don't have a Gemini API key:
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and paste it in your `.env.local` file

### 4. Restart Development Server
After adding the API key, restart your development server:

```bash
npm run dev
```

## ✅ Security Features

- ✅ **No hardcoded keys** - API key is only in environment variables
- ✅ **Git ignored** - `.env.local` is automatically ignored by Git
- ✅ **Runtime validation** - App checks if API key is configured
- ✅ **Clear error messages** - Helpful errors if key is missing

## 🚨 Important Security Notes

1. **Never commit `.env.local`** - This file contains your private API key
2. **Don't share your API key** - Keep it private and secure
3. **Use different keys** for development and production
4. **Rotate keys regularly** for better security

## Troubleshooting

If you see "Gemini API key is not configured" error:
1. Make sure `.env.local` exists in the project root
2. Check that the key is correctly formatted (no spaces, quotes, etc.)
3. Restart the development server after making changes
4. Verify the key is valid by testing it directly with Google AI Studio
