import React, { useState, useEffect } from "react";
import "./popup.css";
import { postLecture } from "~extension/rag/postLecture";
import { chatQuery } from "~extension/chat/chatQuery";

export default function IndexPopup() {
  const [userInput, setUserInput] = useState<string>("");
  const [isSynced, setIsSynced] = useState<boolean>(false);
  const [phpSessId, setPhpSessId] = useState<string | null>(null);
  const [lectureID, setLectureID] = useState<string | null>(null);
  const [response, setResponse] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const url = tabs[0].url;
      if (url && url.includes('umich.edu')) {
        const CAEN_ID = extractLecturerCode(url);
        fetchPHPSESSID(url).then((PHPSESSID) => {
          if (CAEN_ID && PHPSESSID) {
            setIsSynced(true);
            setPhpSessId(PHPSESSID);
            setLectureID(CAEN_ID);
            postLecture(CAEN_ID, PHPSESSID);
          }
        });
      }
    });
  }, []);

  const extractLecturerCode = (url: string): string | null => {
    const match = url.match(/\/player\/r\/([^\/]+)/);
    return match ? match[1] : null;
  };

  const fetchPHPSESSID = async (url: string): Promise<string | null> => {
    return new Promise((resolve) => {
      if (chrome && chrome.cookies && chrome.cookies.get) {
        chrome.cookies.get({ url: url, name: 'PHPSESSID' }, (cookie) => {
          if (cookie) {
            console.log("PHPSESSID fetched:", cookie.value);
            resolve(cookie.value);
          } else {
            console.log("PHPSESSID not found");
            resolve(null);
          }
        });
      } else {
        console.error('Chrome API not available');
        resolve(null);
      }
    });
  };

  const handleSend = async () => {
    if (!lectureID || !userInput.trim()) return;

    setIsLoading(true);
    try {
      const result = await chatQuery(lectureID, userInput);
      console.log("Response:", result);
      setResponse(result);
    } catch (error) {
      console.error("Error querying:", error);
      setResponse("An error occurred while processing your request.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h2>💬 Chat with M-Scribe</h2>
      </header>

      <main>
        <div className="question-section">
          <img src="https://em-content.zobj.net/source/telegram/386/thinking-face_1f914.webp" alt="Thinking Emoji" />
          <div className="question-text">Have a question?</div>
          <div className="small-text">
            {isSynced ? "Lecture is synced." : "Lecture is not synced."}
          </div>
        </div>

        <button id="summarizeBtn">Summarize Notes 📝</button>
        <button id="timestampsBtn">Timestamps? 🕰️</button>

        {response && (
          <div className="response-section">
            <h3>Response:</h3>
            <p>{response}</p>
          </div>
        )}
      </main>

      <footer>
        <input
          type="text"
          id="userInput"
          placeholder="chat here..."
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUserInput(e.target.value)}
          value={userInput}
        />
        <button
          id="sendBtn"
          className="send-button"
          onClick={handleSend}
          disabled={isLoading || !isSynced}
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </footer>
    </div>
  );
}