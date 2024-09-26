import React, { useEffect, useState } from "react"

import "./popup.css"

import { chatQuery } from "~extension/chat/chatQuery"
import { postLecture } from "~extension/rag/postLecture"
import { timestampsQuery } from "~extension/timestamps/timestampsQuery"

export default function IndexPopup() {
  const [userInput, setUserInput] = useState<string>("")
  const [isSynced, setIsSynced] = useState<boolean>(false)
  const [phpSessId, setPhpSessId] = useState<string | null>(null)
  const [lectureID, setLectureID] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [timestampGuide, setTimestampGuide] = useState<
    Array<{ time: string; title: string; summary: string; emoji: string }>
  >([])
  const [messages, setMessages] = useState<
    Array<{ type: "user" | "assistant"; content: string }>
  >([])
  const [isHidden, setIsHidden] = useState(false)

  // New state for authentication
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)

  // Function to handle OAuth login
  const handleLogin = () => {
    // Use chrome.identity.launchWebAuthFlow for OAuth
    chrome.identity.launchWebAuthFlow(
      {
        url:
          "https://your-oauth-provider.com/auth?client_id=YOUR_CLIENT_ID&response_type=token&redirect_uri=" +
          chrome.identity.getRedirectURL(),
        interactive: true
      },
      function (redirectUrl) {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError)
          return
        }
        // Extract the access token from redirectUrl
        const accessToken = extractAccessToken(redirectUrl)
        if (accessToken) {
          // Save the access token and update the authentication state
          localStorage.setItem("accessToken", accessToken)
          setIsAuthenticated(true)
        }
      }
    )
  }

  // Function to extract access token from redirect URL
  const extractAccessToken = (redirectUri) => {
    const m = redirectUri.match(/[#?](.*)/)
    if (!m || m.length < 1) return null
    const params = new URLSearchParams(m[1].split("#")[0])
    return params.get("access_token")
  }

  useEffect(() => {
    // Check if user is already authenticated
    const accessToken = localStorage.getItem("accessToken")
    if (accessToken) {
      setIsAuthenticated(true)
    }

    // The rest of your useEffect for syncing lectures
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const url = tabs[0].url
      if (url && url.includes("umich.edu")) {
        const CAEN_ID = extractLecturerCode(url)
        fetchPHPSESSID(url).then((PHPSESSID) => {
          if (CAEN_ID && PHPSESSID) {
            setIsSynced(true)
            setPhpSessId(PHPSESSID)
            setLectureID(CAEN_ID)
            postLecture(CAEN_ID, PHPSESSID)
          }
        })
      }
    })
  }, [])

  const extractLecturerCode = (url: string): string | null => {
    const match = url.match(/\/player\/r\/([^\/]+)/)
    return match ? match[1] : null
  }

  const fetchPHPSESSID = async (url: string): Promise<string | null> => {
    return new Promise((resolve) => {
      if (chrome && chrome.cookies && chrome.cookies.get) {
        chrome.cookies.get({ url: url, name: "PHPSESSID" }, (cookie) => {
          if (cookie) {
            console.log("PHPSESSID fetched:", cookie.value)
            resolve(cookie.value)
          } else {
            console.log("PHPSESSID not found")
            resolve(null)
          }
        })
      } else {
        console.error("Chrome API not available")
        resolve(null)
      }
    })
  }

  const handleSend = async () => {
    if (!lectureID || !userInput.trim()) return

    setIsLoading(true)

    try {
      const updatedMessages = await new Promise<typeof messages>((resolve) => {
        setMessages((prev) => {
          const newMessages = [
            ...prev,
            { type: "user" as const, content: userInput }
          ]
          resolve(newMessages)
          return newMessages
        })
      })

      setUserInput("")

      const result = await chatQuery(lectureID, userInput, updatedMessages)
      console.log("Response:", result)

      setMessages((prev) => [
        ...prev,
        { type: "assistant" as const, content: result }
      ])
    } catch (error) {
      console.error("Error querying:", error)
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant" as const,
          content: "An error occurred while processing your request."
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleTimestamps = async () => {
    if (!lectureID || !phpSessId) return

    setIsLoading(true)
    try {
      const timestampsData = await timestampsQuery(lectureID, phpSessId)
      setTimestampGuide(timestampsData.timestamps)
    } catch (error) {
      console.error("Error fetching timestamps:", error)
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          content: "An error occurred while processing your request."
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container">
      <header>
        <h2>💬 Chat with M-Scribe</h2>
      </header>

      <main>
        {!isAuthenticated ? (
          <div className="login-section">
            <h2>Login to Get Started!</h2>
            <button className="login-button" onClick={handleLogin}>
              OAuth Login
            </button>
          </div>
        ) : (
          // Render the main content if authenticated
          <>
            <button
              className="toggle-button"
              onClick={() => setIsHidden(!isHidden)}>
              {isHidden ? "▼ Show" : "▲ Hide"}
            </button>
            <div className={`main-content ${isHidden ? "hidden" : ""}`}>
              {!isHidden && (
                <>
                  <div className="question-section">
                    <img
                      src="https://em-content.zobj.net/source/telegram/386/thinking-face_1f914.webp"
                      alt="Thinking Emoji"
                    />
                    <div className="question-text">Have a question?</div>
                    <div className="small-text">
                      {isSynced
                        ? "Lecture is synced."
                        : "Lecture is not synced."}
                    </div>
                  </div>
                  <button id="timestampsBtn" onClick={handleTimestamps}>
                    Timestamps? 🕰️
                  </button>
                </>
              )}
              {timestampGuide.length > 0 && (
                <div className="timestamps-guide">
                  <h3>Timestamps Guide</h3>
                  {timestampGuide.map((ts, index) => (
                    <li key={index}>
                      <strong>
                        {ts.time} {ts.emoji}
                      </strong>{" "}
                      - <strong>{ts.title}</strong>: {ts.summary}
                    </li>
                  ))}
                </div>
              )}
              <div className="chat-messages">
                {messages.map((message, index) => (
                  <div key={index} className={`message ${message.type}`}>
                    {message.content}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </main>
      {isAuthenticated && (
        <footer>
          <input
            type="text"
            id="userInput"
            placeholder="chat here..."
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setUserInput(e.target.value)
            }
            value={userInput}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
          />
          <button
            id="sendBtn"
            className="send-button relative"
            onClick={handleSend}
            disabled={isLoading || !isSynced}>
            {isLoading ? "Sending" : "Send"}
          </button>
        </footer>
      )}
    </div>
  )
}
