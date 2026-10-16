export const SPECIAL_RULE_LINK_PREFIX = '#special-rule='

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function specialRulePattern(rule) {
  return escapeRegExp(rule)
    .replace(/X\\\+/g, '[^)]*')
    .replace(/X/g, '[^)]*')
}

export function linkifySpecialRules(text, specialRules) {
  if (!text || specialRules.length === 0) return text

  const orderedRules = [...specialRules].sort((left, right) => right.length - left.length)
  const pattern = orderedRules
    .map(rule => specialRulePattern(rule))
    .join('|')

  if (!pattern) return text

  const matcher = new RegExp(`(^|[^\\w\\[])(${pattern})(?=$|[^\\w\\]])`, 'g')
  return text.replace(matcher, (_match, prefix, ruleName) => {
    return `${prefix}[${ruleName}](${SPECIAL_RULE_LINK_PREFIX}${encodeURIComponent(ruleName)})`
  })
}

export function getNodeText(node) {
  if (typeof node === 'string' || typeof node === 'number') {
    return String(node)
  }

  if (!node || !Array.isArray(node.props?.children)) {
    return typeof node?.props?.children === 'string' ? node.props.children : ''
  }

  return node.props.children.map(getNodeText).join('')
}
