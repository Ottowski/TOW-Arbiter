import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { getNodeText, linkifySpecialRules, SPECIAL_RULE_LINK_PREFIX } from './markdown.js'

// Message component for displaying chat messages.
// Props:
// - message: the message object containing role, text, and sources
// - specialRules: array of special rules for linkifying
// - onSpecialRuleClick: function to handle clicks on special rule links
function Message({ message, specialRules, onSpecialRuleClick }) {
  const markdownComponents = {
    a({ href, children }) {
      const linkText = getNodeText({ props: { children } }).trim()
      const matchingRule = specialRules.find(rule => rule.toLowerCase() === linkText.toLowerCase())

      if (matchingRule) {
        return (
          <button
            type="button"
            className="rule-link"
            onClick={() => onSpecialRuleClick(matchingRule)}
          >
            {children}
          </button>
        )
      }

      if (href?.startsWith(SPECIAL_RULE_LINK_PREFIX)) {
        const ruleName = decodeURIComponent(href.slice(SPECIAL_RULE_LINK_PREFIX.length))
        return (
          <button
            type="button"
            className="rule-link"
            onClick={() => onSpecialRuleClick(ruleName)}
          >
            {children}
          </button>
        )
      }

      return (
        <a href={href} target="_blank" rel="noreferrer">
          {children}
        </a>
      )
    },
  }

  return (
    <div className={`message ${message.role}`}>
      {message.role === 'assistant'
        ? (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={markdownComponents}
          >
            {linkifySpecialRules(message.text, specialRules)}
          </ReactMarkdown>
        )
        : <p>{message.text}</p>
      }
      {message.sources && message.sources.length > 0 && (
        <ul className="sources">
          {message.sources.map((source, index) => (
            <li key={index}>{source.source ?? source.file ?? 'Unknown source'}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default Message
