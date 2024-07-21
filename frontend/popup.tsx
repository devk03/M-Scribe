import { useState, useEffect } from "react"
import "./popup.css"

function IndexPopup() {
  const [data, setData] = useState("")
  const [isSynced, setIsSynced] = useState(false)

  useEffect(() => {
    // gets the cookie from the url using chrome.tabs api
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const url = tabs[0].url
      if (url && url.includes('umich.edu')) {
        const lecturerCode = extractLecturerCode(url)
        if (lecturerCode) {
          setIsSynced(true)
        }
      }
    })
  }, [])

  const extractLecturerCode = (url) => {
    const match = url.match(/\/player\/r\/([^\/]+)/)
    return match ? match[1] : null
  }

  return (
    <div className="container">
      <header>
        <h2>💬 Chat with M-Scribe</h2>
      </header>

      <main>

        <div className="question-section">
          <img src="https://em-content.zobj.net/source/telegram/386/thinking-face_1f914.webp" alt="Thinking Emoji" />
          <div className="question-text">Have a question?</div>
          <div className="small-text">{isSynced ? "Lecture is synced." : "Lecture is not synced."}</div>
        </div>


        <button id="summarizeBtn">Summarize Notes 📝 </button>
        <button id="timestampsBtn">Timestamps? 🕰️</button>
      </main>

      <footer>
        <input
          type="text"
          id="userInput"
          placeholder="chat here..."
          onChange={(e) => setData(e.target.value)}
          value={data}
        />
        <button id="sendBtn" className="send-button">Send</button>
      </footer>
    </div>
  )
}

export default IndexPopup
