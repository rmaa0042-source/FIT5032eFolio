const { setGlobalOptions } = require('firebase-functions/v2')
const { onRequest } = require('firebase-functions/v2/https')
const { onDocumentCreated } = require('firebase-functions/v2/firestore')
const logger = require('firebase-functions/logger')
const { initializeApp } = require('firebase-admin/app')
const { getFirestore } = require('firebase-admin/firestore')
const cors = require('cors')({ origin: true })

initializeApp()
setGlobalOptions({ maxInstances: 10, region: 'australia-southeast2' })

const db = getFirestore()

exports.countBooks = onRequest((request, response) => {
  cors(request, response, async () => {
    try {
      const snapshot = await db.collection('books').count().get()
      response.status(200).json({ count: snapshot.data().count })
    } catch (error) {
      logger.error('Unable to count books', error)
      response.status(500).json({ error: 'Unable to count books' })
    }
  })
})

exports.capitalizeBookFields = onDocumentCreated(
  'books/{bookId}',
  async (event) => {
    const snapshot = event.data
    if (!snapshot) return

    const original = snapshot.data()
    const capitalized = Object.fromEntries(
      Object.entries(original).map(([key, value]) => [
        key,
        typeof value === 'string' ? value.toUpperCase() : value
      ])
    )

    await snapshot.ref.update(capitalized)
    logger.info('Capitalized new book fields', { bookId: event.params.bookId })
  }
)

exports.getAllBooksAPI = onRequest((request, response) => {
  cors(request, response, async () => {
    if (request.method !== 'GET') {
      response.status(405).json({ error: 'Method not allowed' })
      return
    }

    try {
      const snapshot = await db.collection('books').orderBy('name').get()
      const books = snapshot.docs.map((document) => ({
        id: document.id,
        ...document.data()
      }))

      response.status(200).json({ count: books.length, books })
    } catch (error) {
      logger.error('Unable to retrieve books', error)
      response.status(500).json({ error: 'Unable to retrieve books' })
    }
  })
})
