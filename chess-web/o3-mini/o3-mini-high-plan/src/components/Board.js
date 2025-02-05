import React from "react";
import Square from "./Square";

// Board component renders an 8x8 chessboard based on the state.
function Board({ board, onMove }) {
  // Render rows and columns; board assumed to be an 8x8 2D array.
  return (
    <div className="board">
      {board.map((row, rowIndex) => (
        <div key={`row-${rowIndex}`} className="board-row">
          {row.map((piece, colIndex) => {
            // Determine a coordinate (e.g., "a1", "b2")
            const coordinate =
              String.fromCharCode(97 + colIndex) + (8 - rowIndex);
            return (
              <Square
                key={coordinate}
                coordinate={coordinate}
                piece={piece}
                onMove={onMove}
              />
            );
          })}
        </div>
      ))}
    </div>
  );
}

export default Board;
