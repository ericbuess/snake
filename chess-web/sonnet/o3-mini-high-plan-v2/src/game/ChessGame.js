export class ChessGame {
  constructor() {
    this.reset();
  }

  reset() {
    this.board = this.createInitialBoard();
    this.currentPlayer = "white";
    this.moveHistory = [];
  }

  createInitialBoard() {
    const board = Array(8)
      .fill(null)
      .map(() => Array(8).fill(null));

    // Setup pawns
    for (let i = 0; i < 8; i++) {
      board[1][i] = { type: "pawn", color: "black" };
      board[6][i] = { type: "pawn", color: "white" };
    }

    // Setup other pieces
    const pieces = [
      "rook",
      "knight",
      "bishop",
      "queen",
      "king",
      "bishop",
      "knight",
      "rook",
    ];
    pieces.forEach((type, i) => {
      board[0][i] = { type, color: "black" };
      board[7][i] = { type, color: "white" };
    });

    return board;
  }

  getPiece(row, col) {
    return this.board[row][col];
  }

  makeMove(startRow, startCol, endRow, endCol) {
    const piece = this.board[startRow][startCol];
    if (!piece || piece.color !== this.currentPlayer) return false;

    const validMoves = this.getValidMoves(startRow, startCol);
    if (!validMoves.some(([r, c]) => r === endRow && c === endCol))
      return false;

    const capturedPiece = this.board[endRow][endCol];
    this.moveHistory.push({
      piece,
      from: { row: startRow, col: startCol },
      to: { row: endRow, col: endCol },
      captured: capturedPiece,
    });

    this.board[endRow][endCol] = piece;
    this.board[startRow][startCol] = null;
    this.currentPlayer = this.currentPlayer === "white" ? "black" : "white";
    return true;
  }

  getValidMoves(row, col) {
    const piece = this.board[row][col];
    if (!piece) return [];

    let moves = [];

    switch (piece.type) {
      case "pawn":
        moves = this.getPawnMoves(row, col, piece.color);
        break;
      case "rook":
        moves = this.getRookMoves(row, col, piece.color);
        break;
      case "knight":
        moves = this.getKnightMoves(row, col, piece.color);
        break;
      case "bishop":
        moves = this.getBishopMoves(row, col, piece.color);
        break;
      case "queen":
        moves = [
          ...this.getRookMoves(row, col, piece.color),
          ...this.getBishopMoves(row, col, piece.color),
        ];
        break;
      case "king":
        moves = this.getKingMoves(row, col, piece.color);
        break;
    }

    return moves.filter(
      ([r, c]) =>
        r >= 0 &&
        r < 8 &&
        c >= 0 &&
        c < 8 &&
        (!this.board[r][c] || this.board[r][c].color !== piece.color)
    );
  }

  getPawnMoves(row, col, color) {
    const moves = [];
    const direction = color === "white" ? -1 : 1;

    if (!this.board[row + direction]?.[col]) {
      moves.push([row + direction, col]);
      if (
        ((color === "white" && row === 6) ||
          (color === "black" && row === 1)) &&
        !this.board[row + 2 * direction]?.[col]
      ) {
        moves.push([row + 2 * direction, col]);
      }
    }

    for (const captureCol of [col - 1, col + 1]) {
      const targetSquare = this.board[row + direction]?.[captureCol];
      if (targetSquare && targetSquare.color !== color) {
        moves.push([row + direction, captureCol]);
      }
    }

    return moves;
  }

  getRookMoves(row, col, color) {
    const moves = [];
    const directions = [
      [-1, 0],
      [1, 0],
      [0, -1],
      [0, 1],
    ];

    for (const [dx, dy] of directions) {
      let x = row + dx;
      let y = col + dy;

      while (x >= 0 && x < 8 && y >= 0 && y < 8) {
        const targetPiece = this.board[x][y];
        if (!targetPiece) {
          moves.push([x, y]);
        } else {
          if (targetPiece.color !== color) {
            moves.push([x, y]);
          }
          break;
        }
        x += dx;
        y += dy;
      }
    }

    return moves;
  }

  getKnightMoves(row, col, color) {
    const moves = [];
    const offsets = [
      [-2, -1],
      [-2, 1],
      [-1, -2],
      [-1, 2],
      [1, -2],
      [1, 2],
      [2, -1],
      [2, 1],
    ];

    for (const [dx, dy] of offsets) {
      const newRow = row + dx;
      const newCol = col + dy;
      if (newRow >= 0 && newRow < 8 && newCol >= 0 && newCol < 8) {
        const targetPiece = this.board[newRow][newCol];
        if (!targetPiece || targetPiece.color !== color) {
          moves.push([newRow, newCol]);
        }
      }
    }

    return moves;
  }

  getBishopMoves(row, col, color) {
    const moves = [];
    const directions = [
      [-1, -1],
      [-1, 1],
      [1, -1],
      [1, 1],
    ];

    for (const [dx, dy] of directions) {
      let x = row + dx;
      let y = col + dy;

      while (x >= 0 && x < 8 && y >= 0 && y < 8) {
        const targetPiece = this.board[x][y];
        if (!targetPiece) {
          moves.push([x, y]);
        } else {
          if (targetPiece.color !== color) {
            moves.push([x, y]);
          }
          break;
        }
        x += dx;
        y += dy;
      }
    }

    return moves;
  }

  getKingMoves(row, col, color) {
    const moves = [];
    const directions = [
      [-1, -1],
      [-1, 0],
      [-1, 1],
      [0, -1],
      [0, 1],
      [1, -1],
      [1, 0],
      [1, 1],
    ];

    for (const [dx, dy] of directions) {
      const newRow = row + dx;
      const newCol = col + dy;
      if (newRow >= 0 && newRow < 8 && newCol >= 0 && newCol < 8) {
        const targetPiece = this.board[newRow][newCol];
        if (!targetPiece || targetPiece.color !== color) {
          moves.push([newRow, newCol]);
        }
      }
    }

    return moves;
  }

  getMoveHistory() {
    return this.moveHistory;
  }
}
