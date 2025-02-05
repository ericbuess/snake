import Board from "./components/Board.js";
import ChessEngine from "./game/chessEngine.js";

// Initialize the chess engine state
ChessEngine.init();

// Render the chess board into the root element
const root = document.getElementById("root");
const boardComponent = new Board(root);
boardComponent.render();
