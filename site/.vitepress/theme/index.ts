import DefaultTheme from 'vitepress/theme'
import 'katex/dist/katex.min.css'
import './custom.css'
import AlphaExplorer from './components/AlphaExplorer.vue'
import BinaryShortcut from './components/BinaryShortcut.vue'
import OrbitPlayground from './components/journey/OrbitPlayground.vue'
import HailstoneChart from './components/journey/HailstoneChart.vue'
import BinaryStepVisualizer from './components/journey/BinaryStepVisualizer.vue'
import DroppingSetExplorer from './components/journey/DroppingSetExplorer.vue'
import CycleHunter from './components/journey/CycleHunter.vue'
import ConvergentNavigator from './components/journey/ConvergentNavigator.vue'
import Base6Circle from './components/journey/Base6Circle.vue'
import BitDestructionLandscape from './components/journey/BitDestructionLandscape.vue'
import CountdownVisualizer from './components/journey/CountdownVisualizer.vue'
import DepthExplorer from './components/journey/DepthExplorer.vue'
import BounceSimulator from './components/journey/BounceSimulator.vue'
import NaturalVs2Adic from './components/journey/NaturalVs2Adic.vue'
import ProofMap from './components/journey/ProofMap.vue'
import PhysicsAnalogy from './components/journey/PhysicsAnalogy.vue'
import ZooExplorer from './components/journey/ZooExplorer.vue'
import SpectrumVisualizer from './components/journey/SpectrumVisualizer.vue'
import EisensteinWalk from './components/journey/EisensteinWalk.vue'
import AlphaPositionChart from './components/journey/AlphaPositionChart.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('AlphaExplorer', AlphaExplorer)
    app.component('BinaryShortcut', BinaryShortcut)
    app.component('OrbitPlayground', OrbitPlayground)
    app.component('HailstoneChart', HailstoneChart)
    app.component('BinaryStepVisualizer', BinaryStepVisualizer)
    app.component('DroppingSetExplorer', DroppingSetExplorer)
    app.component('CycleHunter', CycleHunter)
    app.component('ConvergentNavigator', ConvergentNavigator)
    app.component('Base6Circle', Base6Circle)
    app.component('BitDestructionLandscape', BitDestructionLandscape)
    app.component('CountdownVisualizer', CountdownVisualizer)
    app.component('DepthExplorer', DepthExplorer)
    app.component('BounceSimulator', BounceSimulator)
    app.component('NaturalVs2Adic', NaturalVs2Adic)
    app.component('ProofMap', ProofMap)
    app.component('PhysicsAnalogy', PhysicsAnalogy)
    app.component('ZooExplorer', ZooExplorer)
    app.component('SpectrumVisualizer', SpectrumVisualizer)
    app.component('EisensteinWalk', EisensteinWalk)
    app.component('AlphaPositionChart', AlphaPositionChart)
  }
}
