import { defineConfig } from 'vitepress'
import { katex } from '@mdit/plugin-katex'

export default defineConfig({
  title: 'Why Collatz Works',
  description: 'An amateur mathematician\'s interactive field notes on the Collatz conjecture. No proof is claimed.',
  head: [
    ['meta', { property: 'og:title', content: 'Why Collatz Works' }],
    ['meta', { property: 'og:description', content: 'Interactive explorations of the 3n+1 problem: explainers, a few new results, and honest notes on what did not work. No proof is claimed.' }],
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
      { text: 'Start Here', link: '/about/how-to-read' },
      { text: 'The Tour', link: '/journey/the-puzzle' },
      { text: 'Foundations', link: '/foundations/definitions' },
      { text: 'Structure', link: '/proofs/affine-orbit' },
      { text: 'Cycles', link: '/cycles/convergent-elimination' },
      { text: 'Connections', link: '/connections/' },
      { text: 'Prior Work', link: '/publications' },
      { text: 'Explore', link: '/explore/alpha-sequence' }
    ],

    sidebar: [
      {
        text: 'Start Here',
        items: [
          { text: 'How to read this site', link: '/about/how-to-read' }
        ]
      },
      {
        text: 'The Tour',
        items: [
          { text: '1. The Puzzle', link: '/journey/the-puzzle' },
          { text: '2. The Binary Engine', link: '/journey/binary-engine' },
          { text: '3. No Loops', link: '/journey/no-loops' },
          { text: '4. The Hidden Rotation', link: '/journey/the-rotation' },
          { text: '5. The Countdown', link: '/journey/the-countdown' },
          { text: '6. Finite Fuel', link: '/journey/finite-fuel' },
          { text: '7. The Big Picture', link: '/journey/the-picture' }
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
        text: 'Structure',
        items: [
          { text: 'Affine Orbit Structure', link: '/proofs/affine-orbit' },
          { text: 'Bit Destruction', link: '/proofs/bit-destruction' },
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
        text: 'Connections',
        items: [
          { text: 'Overview', link: '/connections/' },
          { text: 'abc Conjecture', link: '/connections/abc-conjecture' },
          { text: 'Universal Dynamics', link: '/connections/universal-dynamics' },
          { text: 'The Transfer Operator', link: '/connections/hilbert-polya' },
          { text: 'Eisenstein Lattice', link: '/connections/eisenstein' },
          { text: 'The Sturmian L-Probe', link: '/connections/sturmian-l-probe' }
        ]
      },
      {
        text: 'Explore',
        items: [
          { text: 'Alpha Sequence', link: '/explore/alpha-sequence' },
          { text: 'Binary Shortcut', link: '/explore/binary-shortcut' },
          { text: 'Sturmian Bridge', link: '/explore/sturmian-bridge' },
          { text: 'Sturmian Fractals', link: '/explore/sturmian-fractals' },
          { text: 'The Wobble', link: '/explore/log6-wobble' },
          { text: 'The Dropping Dictionary', link: '/explore/dropping-dictionary' },
          { text: 'Thirty-Six', link: '/explore/thirty-six' },
          { text: 'The Folded Pentagon', link: '/explore/folded-pentagon' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/h2ocoder/collatz' }
    ],

    outline: { level: [2, 3] }
  }
})
