export class BoardUI {
  constructor(game) {
    this.game = game;
    this.boardElement = document.getElementById("board");
    this.selectedSquare = null;
    this.initialize();
  }

  initialize() {
    this.createBoard();
    this.render();
    this.addEventListeners();
  }

  createBoard() {
    this.boardElement.innerHTML = "";
    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const square = document.createElement("div");
        square.className = `square ${(row + col) % 2 === 0 ? "light" : "dark"}`;
        square.dataset.row = row;
        square.dataset.col = col;
        this.boardElement.appendChild(square);
      }
    }
  }

  render() {
    const squares = this.boardElement.getElementsByClassName("square");
    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const square = squares[row * 8 + col];
        const piece = this.game.board[row][col];
        square.innerHTML = piece ? this.createPieceElement(piece) : "";
      }
    }
  }

  createPieceElement(piece) {
    const color = piece[0] === "w" ? "white" : "black";
    const type = piece[1];
    const pieceMap = {
      P: "♟",
      R: "♜",
      N: "♞",
      B: "♝",
      Q: "♛",
      K: "♚",
    };
    return `<div class="piece ${color}">${pieceMap[type]}</div>`;
  }

  addEventListeners() {
    this.boardElement.addEventListener("click", (e) => {
      const square = e.target.closest(".square");
      if (!square) return;

      const row = parseInt(square.dataset.row);
      const col = parseInt(square.dataset.col);

      if (this.selectedSquare) {
        const fromRow = parseInt(this.selectedSquare.dataset.row);
        const fromCol = parseInt(this.selectedSquare.dataset.col);

        if (this.game.makeMove(fromRow, fromCol, row, col)) {
          this.render();
        }
        this.clearSelection();
      } else if (this.game.board[row][col]) {
        this.selectSquare(square);
      }
    });
  }

  selectSquare(square) {
    this.clearSelection();
    square.classList.add("selected");
    this.selectedSquare = square;
  }

  clearSelection() {
    if (this.selectedSquare) {
      this.selectedSquare.classList.remove("selected");
      this.selectedSquare = null;
    }
  }
}
