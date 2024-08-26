import React, { useState, useEffect } from "react";
import "./popup.css";
import { postLecture } from "~extension/rag/postLecture";
import { chatQuery } from "~extension/chat/chatQuery";
import { summaryQuery } from "~extension/summary/summaryQuery";

export default function IndexPopup() {
  const [userInput, setUserInput] = useState<string>("");
  const [isSynced, setIsSynced] = useState<boolean>(false);
  const [phpSessId, setPhpSessId] = useState<string | null>(null);
  const [lectureID, setLectureID] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [messages, setMessages] = useState<Array<{ type: 'user' | 'assistant', content: string }>>([]);
  const [isHidden, setIsHidden] = useState(false);
  const [summary, setSummary] = useState("");
  const [notes, setNotes] = useState([]);
  const [reviewQuestions, setReviewQuestions] = useState([]);

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
    setMessages(prev => [...prev, { type: 'user', content: userInput }]);
    setUserInput("");

    try {
      const result = await chatQuery(lectureID, userInput);
      console.log("Response:", result);
      setMessages(prev => [...prev, { type: 'assistant', content: result }]);
    } catch (error) {
      console.error("Error querying:", error);
      setMessages(prev => [...prev, { type: 'assistant', content: "An error occurred while processing your request." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSummary = async () => {
	  if (!lectureID || !phpSessId) return;
	  
	  setIsLoading(true);
	  try {
      console.log("lectureID:", lectureID, "phpSessId:", phpSessId);
		  const summaryResult = await summaryQuery(lectureID, phpSessId);
		  //console.log("Summary Result:", summaryResult);
		  setSummary(summaryResult.summary.summary)
      setNotes(summaryResult.summary.notes)
      setReviewQuestions(summaryResult.summary.questions)
	  } catch (error) {
      console.error("Error fetching summary:", error);
      setMessages(prev => [...prev, { type: 'assistant', content: "An error occurred while processing your request." }]);
    }
  };

  return (
    <div className="container">
      <header>
        <h2>💬 Chat with M-Scribe</h2>
      </header>

      <main>
        <button className="toggle-button" onClick={() => setIsHidden(!isHidden)}>
          {isHidden ? '▼ Show' : '▲ Hide'}
        </button>
        <div className={`main-content ${isHidden ? 'hidden' : ''}`}>
          {!isHidden && (
            <>
              <div className="question-section">
                <img src="https://em-content.zobj.net/source/telegram/386/thinking-face_1f914.webp" alt="Thinking Emoji" />
                <div className="question-text">Have a question?</div>
                <div className="small-text">
                  {isSynced ? "Lecture is synced." : "Lecture is not synced."}
                </div>
              </div>
              <button id="summarizeBtn" onClick={handleSummary}>Summarize Notes 📝</button>
              <button id="timestampsBtn">Timestamps? 🕰️</button>
            </>
          )}
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.type}`}>
                {message.content}
              </div>
            ))}
          </div>

          <div className="summary-output">
            <h3>Summary</h3>
            <p>{summary}</p>

            <h3>Important Notes</h3>
            <ul>
            {notes ? notes.map((note, index) => (
              <li key={index}>{note}</li>
            )) : <li>No notes available</li>}
            </ul>

            <h3>Review Questions</h3>
            <ul>
            {reviewQuestions ? reviewQuestions.map((question, index) => (
            <li key={index}>{question}</li>
            )) : <li>No questions available</li>}
            </ul>
</div>

    


        </div>
      </main>
      <footer>
        <input
          type="text"
          id="userInput"
          placeholder="chat here..."
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUserInput(e.target.value)}
          value={userInput}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button
          id="sendBtn"
          className="send-button relative"
          onClick={handleSend}
          disabled={isLoading || !isSynced}
        >
          {isLoading ? (
            "Sending"
          ) : (
            "Send"
          )}
        </button>
      </footer>
    </div>
  );
}