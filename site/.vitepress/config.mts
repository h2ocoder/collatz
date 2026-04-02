import { defineConfig } from 'vitepress'
import { katex } from '@mdit/plugin-katex'

export default defineConfig({
  title: 'Collatz Research',
  description: 'Toward a proof of the Collatz conjecture',
  ignoreDeadLinks: true,

  markdown: {
    config: (md) => {
      md.use(katex, { mhchem: false })
    }
  },

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Foundations', link: '/foundations/definitions' },
      { text: 'Proofs', link: '/proofs/affine-orbit' },
      { text: 'Cycles', link: '/cycles/convergent-elimination' },
      { text: 'Roadmap', link: '/roadmap/path-to-proof' },
      { text: 'Connections', link: '/connections/' }
    ],

    sidebar: [
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
          { text: 'abc Conjecture', link: '/connections/abc-conjecture' }
        ]
      }
    ],

    outline: { level: [2, 3] }
  }
})
