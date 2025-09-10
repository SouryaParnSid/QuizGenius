import { QuizGeniusHero } from "@/components/quizgenius-hero"
import { VideoGeneratorSection } from "@/components/video-generator-section"
import { QuizGeneratorSection } from "@/components/quiz-generator-section"
import { FeaturesSection } from "@/components/features-section"
import { CTASection } from "@/components/cta-section"
import { FooterSection } from "@/components/footer-section"
import { AnimatedSection } from "@/components/animated-section"

export default function QuizGeniusPage() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="relative z-10">
        {/* Hero Section */}
        <QuizGeniusHero />
        
        {/* Video Generator Section */}
        <AnimatedSection delay={0.1}>
          <VideoGeneratorSection />
        </AnimatedSection>
        
        {/* Quiz Generator Section */}
        <AnimatedSection delay={0.2}>
          <QuizGeneratorSection />
        </AnimatedSection>
        
        {/* Features Section */}
        <AnimatedSection delay={0.3}>
          <FeaturesSection />
        </AnimatedSection>
        
        {/* CTA Section */}
        <AnimatedSection delay={0.4}>
          <CTASection />
        </AnimatedSection>
        
        {/* Footer */}
        <div className="bg-slate-900">
          <AnimatedSection delay={0.5}>
            <FooterSection />
          </AnimatedSection>
        </div>
      </div>
    </div>
  )
}
