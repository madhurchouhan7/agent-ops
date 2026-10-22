import React, { useState, useEffect } from 'react'
import { Navbar } from './components/Navbar'
import { Hero } from './components/Hero'
import { TechMarquee } from './components/TechMarquee'
import { BentoGrid } from './components/BentoGrid'
import { ScaleMetrics } from './components/ScaleMetrics'
import { Testimonials } from './components/Testimonials'
import { PricingTable } from './components/PricingTable'
import { FaqSection } from './components/FaqSection'
import { CtaBanner } from './components/CtaBanner'
import { Footer } from './components/Footer'
import { Console } from './components/Console'

export function App() {
  const [currentView, setCurrentView] = useState<'landing' | 'console'>('landing')

  // Check initial URL pathname or query
  useEffect(() => {
    const checkView = () => {
      const path = window.location.pathname
      const params = new URLSearchParams(window.location.search)
      if (path === '/console' || params.get('view') === 'console') {
        setCurrentView('console')
      } else {
        setCurrentView('landing')
      }
    }
    checkView()
    window.addEventListener('popstate', checkView)
    return () => window.removeEventListener('popstate', checkView)
  }, [])

  const handleNavigate = (view: 'landing' | 'console') => {
    setCurrentView(view)
    if (view === 'console') {
      window.history.pushState({}, '', '/console')
    } else {
      window.history.pushState({}, '', '/')
    }
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleStartDemo = () => {
    handleNavigate('console')
  }

  if (currentView === 'console') {
    return <Console onBackToLanding={() => handleNavigate('landing')} />
  }

  return (
    <div className="min-h-screen bg-[#030303] text-[#ededed] font-sans selection:bg-white selection:text-black">
      <Navbar 
        currentView={currentView} 
        onNavigate={handleNavigate}
        onStartDemo={handleStartDemo}
      />
      <main>
        <Hero 
          onLaunchConsole={() => handleNavigate('console')}
          onStartDemo={handleStartDemo}
        />
        <TechMarquee />
        <BentoGrid />
        <ScaleMetrics />
        <Testimonials />
        <PricingTable onSelectPlan={() => handleNavigate('console')} />
        <FaqSection />
        <CtaBanner 
          onLaunchConsole={() => handleNavigate('console')}
          onStartDemo={handleStartDemo}
        />
      </main>
      <Footer />
    </div>
  )
}

export default App
