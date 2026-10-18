import { useEffect, useRef, useState } from 'react'
import './App.css'
import ChatWindow from './components/ChatWindow.jsx'
import InitializationBanner from './components/InitializationBanner.jsx'
import MessageInput from './components/MessageInput.jsx'

const API_URL = import.meta.env.VITE_API_URL ?? ''
// App component for managing the overall state and interactions of the chat application.
// Handles fetching backend status, loading special rules, and managing user interactions.
function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [appReady, setAppReady] = useState(false)
  const [specialRules, setSpecialRules] = useState([])
  const inputRef = useRef(null)
 // Effect hook for polling the backend status to determine if the app is ready.
  useEffect(() => {
    let timer

    async function pollStatus() {
      try {
        const res = await fetch(`${API_URL}/status`)
        if (res.ok) {
          const data = await res.json()
          if (data.ready) {
            setAppReady(true)
            return
          }
        }
      } catch (error) {
        console.warn('Unable to check backend readiness:', error)
      }

      timer = setTimeout(pollStatus, 1500)
    }

    pollStatus()
    return () => clearTimeout(timer)
  }, [])
  // Effect hook for loading the special rules from the backend.
  useEffect(() => {
    async function loadSpecialRules() {
      try {
        const res = await fetch(`${API_URL}/special-rules`)
        if (!res.ok) return
        const data = await res.json()
        if (Array.isArray(data.special_rules)) {
          setSpecialRules(data.special_rules)
        }
      } catch (error) {
        console.error('Unable to load special rules:', error)
      }
    }

    loadSpecialRules()
  }, [])
  // Function for submitting a user's question to the backend and handling the response.
  async function submitQuestion(question) {
    if (!question || loading) return

    setMessages(prev => [...prev, { role: 'user', text: question }])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      if (!res.ok) throw new Error(`Server error ${res.status}`)
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', text: data.answer, sources: data.sources }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'error', text: `Error: ${err.message}` }])
    } finally {
      setLoading(false)
    }
  }

  // Function for handling the submission of the message input form.
  async function sendMessage(event) {
    event.preventDefault()
    await submitQuestion(input.trim())
  }

  // Function for handling clicks on special rule links in the chat messages.
  function handleSpecialRuleClick(ruleName) {
    setInput(ruleName)
    inputRef.current?.focus()
  }
  // Render the main application UI.
  return (
    <div className="app">
      <header className="header">
        <h1>TOW Arbiter</h1>
      </header>

      <ChatWindow
        messages={messages}
        loading={loading}
        specialRules={specialRules}
        onSpecialRuleClick={handleSpecialRuleClick}
      />

      {!appReady && <InitializationBanner />}

      <MessageInput
        input={input}
        inputRef={inputRef}
        loading={loading}
        appReady={appReady}
        onInputChange={setInput}
        onSubmit={sendMessage}
      />
    </div>
  )
}

export default App
