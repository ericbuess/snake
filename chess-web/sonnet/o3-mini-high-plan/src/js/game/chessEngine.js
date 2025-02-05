export class ChessGame {
  constructor() {
    this.board = this.createInitialBoard();
    this.currentPlayer = "white";
    this.moveHistory = [];
    this.initializeGame();
  }

  createInitialBoard() {
    return [
      ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
      ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
      Array(8).fill(""),
      Array(8).fill(""),
      Array(8).fill(""),
      Array(8).fill(""),
      ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
    ];
  }

  initializeGame() {
    this.board = this.createInitialBoard();
    this.currentPlayer = "white";
    this.moveHistory = [];
  }

  isValidMove(fromRow, fromCol, toRow, toCol) {
    const piece = this.board[fromRow][fromCol];
    if (!piece || piece[0] !== (this.currentPlayer === "white" ? "w" : "b")) {
      return false;
    }
    // Basic move validation - to be expanded
    return true;
  }

  makeMove(fromRow, fromCol, toRow, toCol) {
    if (!this.isValidMove(fromRow, fromCol, toRow, toCol)) {
      return false;
    }

    const piece = this.board[fromRow][fromCol];
    this.moveHistory.push({
      piece,
      from: { row: fromRow, col: fromCol },
      to: { row: toRow, col: toCol },
      captured: this.board[toRow][toCol],
    });

    this.board[toRow][toCol] = piece;
    this.board[fromRow][fromCol] = "";
    this.currentPlayer = this.currentPlayer === "white" ? "black" : "white";
    return true;
  }

  undoMove() {
    const lastMove = this.moveHistory.pop();
    if (!lastMove) return;

    const { piece, from, to, captured } = lastMove;
    this.board[from.row][from.col] = piece;
    this.board[to.row][to.col] = captured;
    this.currentPlayer = this.currentPlayer === "white" ? "black" : "white";
  }

  resetGame() {
    this.initializeGame();
  }
}
