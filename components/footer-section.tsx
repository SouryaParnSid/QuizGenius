"use client"

import { Twitter, Github, Linkedin } from "lucide-react"

export function FooterSection() {
  return (
    <footer className="w-full max-w-[1320px] mx-auto px-5 flex flex-col md:flex-row justify-between items-start gap-8 md:gap-0 py-10 md:py-[70px] bg-slate-900 border-t border-slate-700">
      {/* Left Section: Logo, Description, Social Links */}
      <div className="flex flex-col justify-start items-start gap-8 p-4 md:p-8">
        <div className="flex gap-3 items-stretch justify-center">
          <div className="text-center text-white text-xl font-semibold leading-4">QuizGenius</div>
        </div>
        <p className="text-slate-300 text-sm font-medium leading-[18px] text-left">AI-powered learning revolution</p>
        
        {/* Social Links */}
        <div className="flex gap-4">
          <a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors">
            <Twitter className="h-5 w-5" />
          </a>
          <a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors">
            <Github className="h-5 w-5" />
          </a>
          <a href="#" className="text-slate-400 hover:text-cyan-400 transition-colors">
            <Linkedin className="h-5 w-5" />
          </a>
        </div>
      </div>
      {/* Right Section: Product, Company, Resources */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-8 md:gap-12 p-4 md:p-8 w-full md:w-auto">
        <div className="flex flex-col justify-start items-start gap-3">
          <h3 className="text-slate-400 text-sm font-medium leading-5">Product</h3>
          <div className="flex flex-col justify-end items-start gap-2">
            <a href="#video-generator" className="text-slate-300 text-sm font-normal leading-5 hover:text-cyan-400 hover:underline transition-colors">
              Video Generator
            </a>
            <a href="#quiz-creator" className="text-slate-300 text-sm font-normal leading-5 hover:text-cyan-400 hover:underline transition-colors">
              Quiz Creator
            </a>
            <a href="#features" className="text-slate-300 text-sm font-normal leading-5 hover:text-cyan-400 hover:underline transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="text-slate-300 text-sm font-normal leading-5 hover:text-cyan-400 hover:underline transition-colors">
              How it Works
            </a>
            <a href="#" className="text-slate-300 text-sm font-normal leading-5 hover:text-cyan-400 hover:underline transition-colors">
              AI Learning Tools
            </a>
          </div>
        </div>
        
        <div className="flex flex-col justify-start items-start gap-3">
          <h3 className="text-slate-400 text-sm font-medium leading-5">Resources</h3>
          <div className="flex flex-col justify-center items-start gap-2">
            <a href="#" className="text-slate-300 text-sm font-normal leading-5 hover:text-cyan-400 hover:underline transition-colors">
              Terms of use
            </a>
            <a href="#" className="text-slate-300 text-sm font-normal leading-5 hover:text-cyan-400 hover:underline transition-colors">
              API Reference
            </a>
            <a href="#" className="text-slate-300 text-sm font-normal leading-5 hover:text-cyan-400 hover:underline transition-colors">
              Documentation
            </a>
            <a href="#" className="text-slate-300 text-sm font-normal leading-5 hover:text-cyan-400 hover:underline transition-colors">
              Learning Center
            </a>
            <a href="#" className="text-slate-300 text-sm font-normal leading-5 hover:text-cyan-400 hover:underline transition-colors">
              Support
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
