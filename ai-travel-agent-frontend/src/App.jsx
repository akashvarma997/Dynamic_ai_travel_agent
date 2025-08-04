import React, { useEffect, useRef } from 'react'
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import {v4 as uuidv4} from 'uuid'
import ReactMarkdown from 'react-markdown';
import { DotLottie } from '@lottiefiles/dotlottie-web';
import LottieAnimation from './LottieAnimation'

function App() {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [inputValue, setInputValue] = useState('');
  const chatBoxRef = useRef(null);
  // Load chat history from localStorage on initial render
  const [chatHistory, setChatHistory] = useState(() => {
    const savedHistory = localStorage.getItem('chat_history');
    return savedHistory ? JSON.parse(savedHistory) : [];
  });

  useEffect(() => {
    // Get or create session ID
    let storedSessionId = localStorage.getItem('travel_agent_session_id');
    if (!storedSessionId) {
      storedSessionId = uuidv4();
      localStorage.setItem('travel_agent_session_id', storedSessionId);
    }
    setSessionId(storedSessionId);
  },[])

  useEffect(() => {
    localStorage.setItem('chat_history', JSON.stringify(chatHistory));
  }, [chatHistory]);

  useEffect(() => {
    console.log("Chat history updated:", chatHistory);
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleSubmit = async () => {
    if (!inputValue.trim()) return;
    const userMessage = { sender: 'User', text: inputValue };
    setChatHistory(prev => [...prev, userMessage]);
    setInputValue('');

    setMessage('');
    setIsLoading(true);

    // Use the environment variable for the API URL
    const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
    console.log("API URL:", apiUrl);

    try{
    const response = await fetch (`${apiUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: inputValue,
        session_id: sessionId,
      }),
    })

    if (!response.ok) {
      setIsLoading(false);
      setMessage("Error: " + response.statusText);
      return;
    }

    const data = await response.json();
    const aiMessage = { sender: 'AI', text: data.response || "Sorry, I encountered an issue." };
    setChatHistory(prev => [...prev, aiMessage]);

    setIsLoading(false);
    console.log(data, "data from server");
    setMessage(data.response || "No response from server");

    setInputValue('');
    } catch (error) {
      console.error("Failed to fetch:", error);
      const errorMessage = { sender: 'AI', text: "Sorry, I couldn't connect to the server." };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  const markdown = `
**User:** Hey, what exactly is quantum computing?

**AI:** Quantum computing is a type of computation that uses quantum bits (qubits). Unlike classical bits, which can be either 0 or 1, qubits can be in a superposition of states, allowing quantum computers to process information in a highly parallel way.

---

**User:** That sounds cool. Is it faster than classical computing?

**AI:** In certain cases, yes. For example, quantum algorithms like Shor’s algorithm can factor large numbers exponentially faster than the best-known classical algorithms.

`;


  return (
    <section className="text-gray-400 bg-gray-900 body-font relative h-screen flex items-center justify-center flex-col">
      <div className="container mx-auto">
        <div className="flex flex-col text-center w-full mb-12">
          <h1 className="sm:text-3xl text-2xl font-medium title-font mb-4 text-white">
            AI Travel Agent
          </h1>
          <p className="lg:w-2/3 mx-auto leading-relaxed text-base">
            The intelligent way to plan your travels.
          </p>
        </div>
      </div>
      <div className="container mx-auto w-7/12">
        <div className="mx-50">
        {true && 
            <div ref={chatBoxRef} className="chat-box overflow-y-auto mt-4 mb-2 scrollbar-hide h-[470px] border-t border-gray-300 =">
              {chatHistory.map((message, index) => (
              <div key={index} className={`message ${message.sender === 'User' ? 'text-right' : 'text-left'} mb-[5px]`}>
                <div className={`inline-block ${message.sender === 'User' ? "bg-gray-800" : "bg-gray-700"} rounded-lg px-4 py-2`}>
                <ReactMarkdown>
                  {`${message.text}`}
                </ReactMarkdown>
                </div>
              </div>
            ))}
              {/* <ReactMarkdown>{message}</ReactMarkdown> */}
              {/* <ReactMarkdown>{markdown}</ReactMarkdown> */}
          </div>}
          <div className="flex -m-2">
            <div className="p-2 w-full">
              {isLoading && (
              <div className='fixed left-1/2 bottom-[70px]'>
              <LottieAnimation />
              </div>
              )}
              <div className="relative">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSubmit()}
                  placeholder="Ask your travel agent..."
                  id="message"
                  name="message"
                  className="w-full bg-gray-800 bg-opacity-40 rounded border border-gray-700 focus:border-pink-500 focus:bg-gray-900 focus:ring-2 focus:ring-pink-900 h-22 text-base outline-none text-gray-100 py-1 px-3 resize-none leading-6 transition-colors duration-200 ease-in-out"
                ></textarea>
              </div>
            </div>
            <div className="p-2  flex justify-center  items-start flex-col">
              <button className="flex mx-auto text-white bg-pink-500 border-0 py-2 px-8 focus:outline-none hover:bg-pink-600 rounded text-lg"
              onClick={handleSubmit}
              >
                Ask
              </button>
            {/* {!isLoading && <Loader />} */}
          </div>
        </div>
      </div>
      </div>
    </section>
  );
}

export default App
