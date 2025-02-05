import React from "react";
import Piece from "./Piece";

// Each square on the board. Highlights valid move targets and handles user clicks.
function Square({ coordinate, piece, onMove }) {
  // Placeholder click handler; in a complete app, this will handle selection and move logic.
  const handleClick = () => {
    // TODO: Call onMove with the selected move info
    console.log(`Square ${coordinate} clicked`);
  };

  // Determine square color based on its coordinate.
  const isDark =
    (coordinate.charCodeAt(0) - 97 + parseInt(coordinate[1], 10)) % 2 !== 0;
  const squareClass = isDark ? "square dark-square" : "square light-square";

  return (
    <div className={squareClass} onClick={handleClick}>
      {piece && <Piece piece={piece} />}
    </div>
  );
}

export default Square;
