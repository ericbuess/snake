import React from "react";

// Renders the chess piece image based on the piece type.
function Piece({ piece }) {
  // piece expected to be a string such as "wP" (white pawn) or "bK" (black king)
  const pieceMap = {
    wP: "/public/assets/images/wP.svg",
    wR: "/public/assets/images/wR.svg",
    wN: "/public/assets/images/wN.svg",
    wB: "/public/assets/images/wB.svg",
    wQ: "/public/assets/images/wQ.svg",
    wK: "/public/assets/images/wK.svg",
    bP: "/public/assets/images/bP.svg",
    bR: "/public/assets/images/bR.svg",
    bN: "/public/assets/images/bN.svg",
    bB: "/public/assets/images/bB.svg",
    bQ: "/public/assets/images/bQ.svg",
    bK: "/public/assets/images/bK.svg",
  };

  const imgSrc = pieceMap[piece] || "";

  return <img className="piece" src={imgSrc} alt={piece} draggable="true" />;
}

export default Piece;
