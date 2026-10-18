import { useEffect, useRef } from 'react'
import Message from './Message.jsx'

// ChatWindow component for displaying the chat messages and handling scrolling.
// Props:
// - messages: array of message objects to display
// - loading: boolean indicating if a message is being sent
// - specialRules: array of special rules for linkifying
// - onSpecialRuleClick: function to handle clicks on special rule links
function ChatWindow({ messages, loading, specialRules, onSpecialRuleClick }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  return (
    <div className="chat-window">
      {messages.length === 0 && (
        <p className="placeholder">Ask a question about the Warhammer rules...</p>
      )}
      {messages.map((message, index) => (
        <Message
          key={index}
          message={message}
          specialRules={specialRules}
          onSpecialRuleClick={onSpecialRuleClick}
        />
      ))}
      {loading && <div className="message assistant loading"><span>...</span></div>}
      <div ref={bottomRef} />
    </div>
  )
}

export default ChatWindow
