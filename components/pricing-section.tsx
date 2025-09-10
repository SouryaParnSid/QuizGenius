"use client"

import { useState } from "react"
import { Check } from "lucide-react"
import { Button } from "@/components/ui/button"

export function PricingSection() {
  const [isAnnual, setIsAnnual] = useState(true)

  const pricingPlans = [
    {
      name: "Free",
      monthlyPrice: "$0",
      annualPrice: "$0",
      description: "Perfect for individuals starting their journey.",
      features: [
        "Real-time code suggestions",
        "Basic integration logos",
        "Single MCP server connection",
        "Up to 2 AI coding agents",
        "Vercel deployments with Pointer branding",
      ],
      buttonText: "Get Started",
      buttonClass:
        "bg-zinc-300 shadow-[0px_1px_1px_-0.5px_rgba(16,24,40,0.20)] outline outline-0.5 outline-[#1e29391f] outline-offset-[-0.5px] text-gray-800 text-shadow-[0px_1px_1px_rgba(16,24,40,0.08)] hover:bg-zinc-400",
    },
    {
      name: "Pro",
      monthlyPrice: "$20",
      annualPrice: "$16",
      description: "Ideal for professionals.",
      features: [
        "Enhanced real-time previews",
        "Unlimited integrations with custom logos",
        "Multiple MCP server connections",
        "Up to 10 concurrent AI coding agents",
        "Collaborative coding with team chat",
        "Advanced version control integrations",
        "Priority email and chat support",
      ],
      buttonText: "Join now",
      buttonClass:
        "bg-primary-foreground shadow-[0px_1px_1px_-0.5px_rgba(16,24,40,0.20)] text-primary text-shadow-[0px_1px_1px_rgba(16,24,40,0.08)] hover:bg-primary-foreground/90",
      popular: true,
    },
    {
      name: "Ultra",
      monthlyPrice: "$200",
      annualPrice: "$160",
      description: "Tailored solutions for teams.",
      features: [
        "Dedicated account support",
        "Unlimited MCP server clusters",
        "Unlimited AI coding agents",
        "Enterprise-grade security and compliance",
        "Priority deployments and SLA guarantees",
      ],
      buttonText: "Talk to Sales",
      buttonClass:
        "bg-secondary shadow-[0px_1px_1px_-0.5px_rgba(16,24,40,0.20)] text-secondary-foreground text-shadow-[0px_1px_1px_rgba(16,24,40,0.08)] hover:bg-secondary/90",
    },
  ]

  return (
    null
  )
}
