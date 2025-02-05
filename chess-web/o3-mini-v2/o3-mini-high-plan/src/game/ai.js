import ChessEngine from "./chessEngine.js";

function getAllPossibleMoves() {
  // Very naïve implementation: returns a list of moves (from, to) for any piece that can move one step in any direction.
  const board = ChessEngine.getBoard();
  const moves = [];
  const boardSize = board.length;
  for (let row = 0; row < boardSize; row++) {
    for (let col = 0; col < boardSize; col++) {
      const piece = board[row][col];
      if (piece !== "") {
        // Try moving in 8 directions one square (no proper validation)
        const directions = [
          { dr: -1, dc: 0 },
          { dr: 1, dc: 0 },
          { dr: 0, dc: -1 },
          { dr: 0, dc: 1 },
          { dr: -1, dc: -1 },
          { dr: -1, dc: 1 },
          { dr: 1, dc: -1 },
          { dr: 1, dc: 1 },
        ];
        directions.forEach((dir) => {
          const newRow = row + dir.dr;
          const newCol = col + dir.dc;
          if (
            newRow >= 0 &&
            newRow < boardSize &&
            newCol >= 0 &&
            newCol < boardSize
          ) {
            moves.push({
              from: { row, col },
              to: { row: newRow, col: newCol },
            });
          }
        });
      }
    }
  }
  return moves;
}

export function getAIMove() {
  const moves = getAllPossibleMoves();
  if (moves.length === 0) return null;
  // For prototype, select a random move
  const randomIndex = Math.floor(Math.random() * moves.length);
  return moves[randomIndex];
}
