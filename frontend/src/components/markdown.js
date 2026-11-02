// Markdown utility functions for handling special rule linkification and node text extraction.
export const SPECIAL_RULE_LINK_PREFIX = '#special-rule='
export const EQUIPMENT_LINK_PREFIX = '#equipment='

// Escapes special characters in a string for use in a regular expression.
function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

// Converts a special rule into a regex pattern for matching within text.
function specialRulePattern(rule) {
  return escapeRegExp(rule)
    .replace(/X\\\+/g, '[^)]*')
    .replace(/X/g, '[^)]*')
}

// Replaces occurrences of special rules in the text with markdown links.
export function linkifySpecialRules(text, specialRules) {
  if (!text || specialRules.length === 0) return text

  const orderedRules = [...specialRules].sort((left, right) => right.length - left.length)
  const pattern = orderedRules
    .map(rule => specialRulePattern(rule))
    .join('|')

  if (!pattern) return text

  const matcher = new RegExp(`(^|[^\\w\\[])(${pattern})(?=$|[^\\w\\]])`, 'g')
  return text.split(/(\[[^\]]+\]\([^)]+\))/g).map((part, index) => {
    if (index % 2 === 1) return part
    return part.replace(matcher, (_match, prefix, ruleName) => {
      return `${prefix}[${ruleName}](${SPECIAL_RULE_LINK_PREFIX}${encodeURIComponent(ruleName)})`
    })
  }).join('')
}

export function linkifyEquipment(text) {
  if (!text) return text

  return text.replace(
    /^([ \t]*(?:\*\*)?Equipment:(?:\*\*)?[ \t]*)(.+)$/gim,
    (_line, prefix, equipment) => {
      const parts = equipment.split(/(,\s*|\s+and\s+)/i)
      const linkedEquipment = parts.map((part, index) => {
        if (index % 2 === 1 || !part.trim()) return part

        const leadingWhitespace = part.match(/^\s*/)[0]
        const trailingWhitespace = part.match(/\s*$/)[0]
        let label = part.trim()
        const trailingPunctuation = label.match(/[.;]+$/)?.[0] ?? ''
        label = label.slice(0, label.length - trailingPunctuation.length)
        if (!label) return part

        return `${leadingWhitespace}[${label}](${EQUIPMENT_LINK_PREFIX}${encodeURIComponent(label)})${trailingPunctuation}${trailingWhitespace}`
      }).join('')

      return `${prefix}${linkedEquipment}`
    },
  )
}

// Recursively extracts the text content from a React node.
export function getNodeText(node) {
  if (typeof node === 'string' || typeof node === 'number') {
    return String(node)
  }

  if (!node || !Array.isArray(node.props?.children)) {
    return typeof node?.props?.children === 'string' ? node.props.children : ''
  }

  return node.props.children.map(getNodeText).join('')
}
