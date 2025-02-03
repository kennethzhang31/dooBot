import './App.css';
import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [displayedResponse, setDisplayedResponse] = useState("");
  const [robotState, setRobotState] = useState("idle");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!query) return;

    setIsLoading(true);
    setRobotState("thinking");

    try {
      const result = await axios.post("http://localhost:8000/query", {
        query: query,
      });
      setResponse(result.data.response);
      setRobotState("speaking");
      setIsLoading(false);
    } catch (error) {
      setResponse("Error: Unable to fetch response");
      setRobotState("idle");
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (robotState === "speaking" || robotState === "idle") {
      setIsLoading(false);
    }
  }, [robotState]);

  // ✅ Fix Response Display Effect
  useEffect(() => {
    if (robotState === "speaking" && response) {
      let index = 0;
      setDisplayedResponse(response[index]);
      const interval = setInterval(() => {
        if (index < response.length-1) {
          setDisplayedResponse((prev) => prev + response[index]);
          index++;
        } else {
          clearInterval(interval);
          setTimeout(() => {
            setRobotState("idle");
          }, 3000);
        }
      }, 30);
      return () => clearInterval(interval);
    }
  }, [robotState, response]);

  // useEffect(() => {
  //   if (robotState === "speaking" && response) {
  //     let index = 0;
  //     setDisplayedResponse(response[index]);
  //     const interval = setInterval(() => {
  //       if (index < response.length - 1) {
  //         setDisplayedResponse((prev) => prev + response[index]);
  //         index++;
  //       } else {
  //         clearInterval(interval);
  //         setTimeout(() => {
  //           setRobotState("idle");
  //         }, 3000);
  //       }
  //     }, 30);
  //     return () => clearInterval(interval);
  //   }
  // }, [robotState, response]);

  // useEffect(() => {
  //   if (robotState === "thinking") {
  //     setDisplayedResponse("");
  //   }
  // }, [robotState]);

  return (
    <div className="App">
      <h1>NTHU Dormbot</h1>
      <div className="chat-container">
        <div className="robot">
          {robotState === "thinking" && (
            <img
              src="/robot-thinking.gif"
              alt="Thinking"
              className="robot-animation"
            />
          )}
          {robotState === "speaking" && (
            <img
              src="/robot-speaking.gif"
              alt="Speaking"
              className="robot-animation"
            />
          )}
          {robotState === "idle" && (
            <img
              src="/robot-idle.gif"
              alt="Speaking"
              className="robot-animation"
            />
          )}
        </div>
        <div className="chat">
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about dorm rules..."
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading}>
              {isLoading ? "Thinking..." : "Ask"}
            </button>
          </form>
          {displayedResponse && (
            <div className="response">
              <h2>Response:</h2>
              <p>{displayedResponse}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
