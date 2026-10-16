import { useEffect, useRef } from 'react'
import Message from './Message.jsx'

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
