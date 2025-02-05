import config from "../config.js";

export function parseFEN(fen = config.initialFEN) {
  // Very simplistic parser: only parses board layout part
  const rows = fen.split(" ")[0].split("/");
  const board = rows.map((row) => {
    const boardRow = [];
    for (let char of row) {
      if (isNaN(char)) {
        boardRow.push(char);
      } else {
        let emptyCount = parseInt(char, 10);
        for (let i = 0; i < emptyCount; i++) {
          boardRow.push("");
        }
      }
    }
    return boardRow;
  });
  return board;
}

export function generateFEN(board) {
  // Generate FEN for the board part only.
  return board
    .map((row) => {
      let fenRow = "";
      let emptyCount = 0;
      for (let cell of row) {
        if (cell === "") {
          emptyCount++;
        } else {
          if (emptyCount > 0) {
            fenRow += emptyCount;
            emptyCount = 0;
          }
          fenRow += cell;
        }
      }
      if (emptyCount > 0) {
        fenRow += emptyCount;
      }
      return fenRow;
    })
    .join("/");
}
