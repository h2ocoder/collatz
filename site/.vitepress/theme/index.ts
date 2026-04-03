import DefaultTheme from 'vitepress/theme'
import 'katex/dist/katex.min.css'
import './custom.css'
import AlphaExplorer from './components/AlphaExplorer.vue'
import BinaryShortcut from './components/BinaryShortcut.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('AlphaExplorer', AlphaExplorer)
    app.component('BinaryShortcut', BinaryShortcut)
  }
}
