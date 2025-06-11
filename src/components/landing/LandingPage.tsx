import { Hero } from "./Hero";
import { PersonalityTests } from "./PersonalityTests";
import { UniversityExplorer } from "./UniversityExplorer";
import { WhyChooseUs } from "./WhyChooseUs";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";

export const LandingPage = () => {
  return (
    <div className="min-h-screen w-screen bg-white text-text-primary overflow-x-hidden">
      <Navbar />
      <main className="flex flex-col items-center w-screen px-2 md:px-4">
        <Hero />
        <PersonalityTests />
        <UniversityExplorer />
        <WhyChooseUs />
      </main>
      <Footer />
    </div>
  );
};

