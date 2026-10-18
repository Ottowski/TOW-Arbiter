// MessageInput component for handling user input in the chat interface.
// Props:
// - input: current value of the input field
// - inputRef: reference to the input element
// - loading: boolean indicating if a message is being sent
// - appReady: boolean indicating if the app is ready for input
// - onInputChange: function to handle input changes
// - onSubmit: function to handle form submission
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
