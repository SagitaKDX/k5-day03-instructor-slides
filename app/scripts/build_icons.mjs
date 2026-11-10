// Renders the Lucide icons used inside slide HTML to static SVG strings.
// Run from app/: node scripts/build_icons.mjs  -> writes ../content/icons.json
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { Lightbulb, TriangleAlert, CircleCheck } from 'lucide-react'
import { writeFileSync } from 'node:fs'

const icons = { coach: Lightbulb, anti: TriangleAlert, check: CircleCheck }
const out = {}
for (const [k, C] of Object.entries(icons)) {
  out[k] = renderToStaticMarkup(createElement(C, { 'aria-hidden': 'true', className: 'box-icon', size: 20, strokeWidth: 2 }))
}
writeFileSync(new URL('../../content/icons.json', import.meta.url), JSON.stringify(out, null, 2) + '\n')
console.log(Object.keys(out).join(', '))
