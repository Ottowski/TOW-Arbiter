function MessageInput({ input, inputRef, loading, appReady, onInputChange, onSubmit }) {
  return (
    <form className="input-row" onSubmit={onSubmit}>
      <input
        ref={inputRef}
        type="text"
        value={input}
        onChange={event => onInputChange(event.target.value)}
        placeholder={appReady ? 'Type your question here...' : 'Loading rules, input will unlock shortly...'}
        disabled={loading || !appReady}
      />
      <button type="submit" disabled={loading || !input.trim() || !appReady}>Send</button>
    </form>
  )
}

export default MessageInput
