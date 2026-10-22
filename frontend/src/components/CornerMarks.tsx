import React from 'react'

export const CornerMarks: React.FC = () => {
  return (
    <>
      {/* Top Left */}
      <div aria-hidden="true" className="pointer-events-none absolute size-3 -translate-x-1/2 -translate-y-1/2 top-0 left-0 z-20">
        <span className="absolute inset-0 m-auto block h-px w-full bg-white/40" />
        <span className="absolute inset-0 m-auto block h-full w-px bg-white/40" />
      </div>
      {/* Top Right */}
      <div aria-hidden="true" className="pointer-events-none absolute size-3 -translate-y-1/2 top-0 right-0 translate-x-1/2 z-20">
        <span className="absolute inset-0 m-auto block h-px w-full bg-white/40" />
        <span className="absolute inset-0 m-auto block h-full w-px bg-white/40" />
      </div>
      {/* Bottom Left */}
      <div aria-hidden="true" className="pointer-events-none absolute size-3 -translate-x-1/2 bottom-0 left-0 translate-y-1/2 z-20">
        <span className="absolute inset-0 m-auto block h-px w-full bg-white/40" />
        <span className="absolute inset-0 m-auto block h-full w-px bg-white/40" />
      </div>
      {/* Bottom Right */}
      <div aria-hidden="true" className="pointer-events-none absolute size-3 right-0 bottom-0 translate-x-1/2 translate-y-1/2 z-20">
        <span className="absolute inset-0 m-auto block h-px w-full bg-white/40" />
        <span className="absolute inset-0 m-auto block h-full w-px bg-white/40" />
      </div>
    </>
  )
}
