import { defineConfig } from 'vitepress'
import { katex } from '@mdit/plugin-katex'

export default defineConfig({
  title: 'Why Collatz Works',
  description: 'An interactive proof that every Collatz orbit converges to 1',
  head: [
    ['meta', { property: 'og:title', content: 'Why Collatz Works' }],
    ['meta', { property: 'og:description', content: 'An interactive journey through the proof that every positive integer reaches 1 under the 3n+1 map.' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }],
  ],
  markdown: {
    config: (md) => {
      md.use(katex, { mhchem: false })
    }
  },

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Proof Journey', link: '/journey/the-puzzle' },
      { text: 'The Proof', link: '/proof/' },
      { text: 'Foundations', link: '/foundations/definitions' },
      { text: 'Proofs', link: '/proofs/affine-orbit' },
      { text: 'Cycles', link: '/cycles/convergent-elimination' },
      { text: 'Roadmap', link: '/roadmap/path-to-proof' },
      { text: 'Connections', link: '/connections/' },
      { text: 'Prior Work', link: '/publications' },
      { text: 'Explore', link: '/explore/alpha-sequence' }
    ],

    sidebar: [
      {
        text: 'Proof Journey',
        items: [
          { text: '1. The Puzzle', link: '/journey/the-puzzle' },
          { text: '2. The Binary Engine', link: '/journey/binary-engine' },
          { text: '3. No Loops', link: '/journey/no-loops' },
          { text: '4. The Hidden Rotation', link: '/journey/the-rotation' },
          { text: '5. The Countdown', link: '/journey/the-countdown' },
          { text: '6. Finite Fuel', link: '/journey/finite-fuel' },
          { text: '7. The Complete Picture', link: '/journey/the-picture' }
        ]
      },
      {
        text: 'Foundations',
        items: [
          { text: 'Definitions', link: '/foundations/definitions' },
          { text: 'Terminology Map', link: '/foundations/terminology' }
        ]
      },
      {
        text: 'Proved Results',
        items: [
          { text: 'Affine Orbit Structure', link: '/proofs/affine-orbit' },
          { text: 'Logarithmic Escape', link: '/proofs/logarithmic-escape' },
          { text: 'Bit Destruction Bound', link: '/proofs/bit-destruction' },
          { text: '3-Adic Mixing', link: '/proofs/mixing' }
        ]
      },
      {
        text: 'Cycle Analysis',
        items: [
          { text: 'Convergent Elimination', link: '/cycles/convergent-elimination' },
          { text: 'Divisibility Obstruction', link: '/cycles/divisibility-obstruction' }
        ]
      },
      {
        text: 'Roadmap',
        items: [
          { text: 'Path to Proof', link: '/roadmap/path-to-proof' }
        ]
      },
      {
        text: 'Connections',
        items: [
          { text: 'Overview', link: '/connections/' },
          { text: 'abc Conjecture', link: '/connections/abc-conjecture' },
          { text: 'Universal Dynamics', link: '/connections/universal-dynamics' },
          { text: 'The Transfer Operator', link: '/connections/hilbert-polya' },
          { text: 'Eisenstein Lattice', link: '/connections/eisenstein' }
        ]
      },
      {
        text: 'Explore',
        items: [
          { text: 'Alpha Sequence', link: '/explore/alpha-sequence' },
          { text: 'Binary Shortcut', link: '/explore/binary-shortcut' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/h2ocoder/collatz' }
    ],

    outline: { level: [2, 3] }
  }
})
