import React from "react";

// Display move history in a simple list.
function MoveHistory({ moves }) {
  return (
    <div className="move-history">
      <h2>Move History</h2>
      <ul>
        {moves.map((move, idx) => (
          <li key={idx}>{move}</li>
        ))}
      </ul>
    </div>
  );
}

export default MoveHistory;
