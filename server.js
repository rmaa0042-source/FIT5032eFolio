import express from 'express'

const app = express()
const port = process.env.PORT || 3000

app.get('/', (_request, response) => {
  response.send('Hello from Node.js!')
})

app.listen(port, () => {
  console.log(`Server is running on port ${port}`)
})
