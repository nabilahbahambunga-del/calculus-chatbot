import { useState } from "react";
import { register, login, chat } from "./api";

function App() {
  const [user, setUser] = useState(null);
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");

  const handleRegister = async () => {
    const res = await register({
      student_id: "65001",
      name: "Test",
      password: "1234",
    });
    alert(JSON.stringify(res));
  };

  const handleLogin = async () => {
    const res = await login({
      student_id: "65001",
      password: "1234",
    });
    setUser(res);
  };

  const handleChat = async () => {
    const res = await chat({
      user_id: user.id,
      message: message,
    });
  setReply(res.reply);
};


  return (
    <div style={{ padding: 40 }}>
      <h1>AI Tutor</h1>

      {!user ? (
        <>
          <button onClick={handleRegister}>Register</button>
          <button onClick={handleLogin}>Login</button>
        </>
      ) : (
        <>
          <p>Welcome {user.name}</p>
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
          <button onClick={handleChat}>Send</button>
          <p><b>AI:</b> {reply}</p>
        </>
      )}
    </div>
  );
}

export default App;
