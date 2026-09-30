import { HeroSection } from "@/components/home/HeroSection";
import { TopPredictions } from "@/components/home/TopPredictions";
import { HowItWorks } from "@/components/home/HowItWorks";
import { ModelPerformanceSnapshot } from "@/components/home/ModelPerformanceSnapshot";
import { ExploreLinks } from "@/components/home/ExploreLinks";

export default function Home() {
  return (
    <>
      <HeroSection />
      <TopPredictions />
      <HowItWorks />
      <ModelPerformanceSnapshot />
      <ExploreLinks />
    </>
  );
}
