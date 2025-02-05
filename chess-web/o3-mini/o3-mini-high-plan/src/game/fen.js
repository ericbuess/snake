// Functions to parse and generate FEN strings for saving/loading board state.

export function boardToFEN(board) {
  // Basic stub converting board 2D array into a FEN-like string.
  // TODO: Complete full FEN support including turn, castling rights, etc.
  return board
    .map((row) => row.map((piece) => (piece ? piece : "1")).join(" "))
    .join("/");
}

export function fenToBoard(fen) {
  // Basic stub that converts a FEN-like string to a board.
  // TODO: Implement full parsing.
  const rows = fen.split("/");
  return rows.map((row) => {
    return row.split(" ").map((item) => (item === "1" ? null : item));
  });
}
