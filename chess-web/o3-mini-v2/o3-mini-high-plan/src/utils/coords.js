// Converts row and col indices to algebraic notation (e.g., 0,0 -> a8)
export function indexToAlgebraic(row, col) {
  const files = "abcdefgh";
  const ranks = "87654321";
  return files[col] + ranks[row];
}

// Convert algebraic notation into row, col (e.g., a8 -> 0,0)
export function algebraicToIndex(coord) {
  const files = "abcdefgh";
  const ranks = "87654321";
  return {
    row: ranks.indexOf(coord[1]),
    col: files.indexOf(coord[0]),
  };
}
