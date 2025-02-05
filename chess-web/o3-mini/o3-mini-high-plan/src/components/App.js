import React, { useState } from "react";
import Board from "./Board";
import MoveHistory from "./MoveHistory";
import { initializeBoard } from "../game/chessEngine";

// Main application component that houses the board and move history.
function App() {
  const [board, setBoard] = useState(initializeBoard());
  const [moveHistory, setMoveHistory] = useState([]);

  // Placeholder for a move handler
  const handleMove = (move) => {
    // TODO: Validate and apply move using chessEngine functions.
    // For now, simply update move history.
    setMoveHistory([...moveHistory, move]);
  };

  return (
    <div className="app">
      <h1>Chess Web Prototype</h1>
      <div className="game-container">
        <Board board={board} onMove={handleMove} />
        <MoveHistory moves={moveHistory} />
      </div>
    </div>
  );
}

export default App;
