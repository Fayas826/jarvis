
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.json({
    message: 'Hello World from JARVIS Enterprise Generated Server!',
    timestamp: new Date().toISOString(),
    status: 'ONLINE'
  });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
