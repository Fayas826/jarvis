const fs = require('fs');

const path = 'c:\\jarvis AI\\jarvis\\frontend\\src\\core\\AppStateProvider.jsx';
const lines = fs.readFileSync(path, 'utf8').split('\n');

// 0-indexed: lines 162-236 is indices 161 to 235 inclusive
const chunkToMove = lines.splice(161, 236 - 162 + 1);

// Now processInput ends at what was line 491.
// Since we removed 75 lines BEFORE it, the new line number for processInput end is 491 - 75 = 416.
// In 0-indexed, that's index 415. We want to insert AFTER 415, so at index 416.
lines.splice(416, 0, ...chunkToMove);

fs.writeFileSync(path, lines.join('\n'));
console.log("Fixed TDZ by moving lines!");
