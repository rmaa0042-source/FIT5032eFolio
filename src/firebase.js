import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'

const firebaseConfig = {
  apiKey: 'AIzaSyBz8ldLHNqfkP6V8Uhik8ySDddbjpHGjOw',
  authDomain: 'fit5032-efolio-w7-w8.firebaseapp.com',
  projectId: 'fit5032-efolio-w7-w8',
  storageBucket: 'fit5032-efolio-w7-w8.firebasestorage.app',
  messagingSenderId: '482796809481',
  appId: '1:482796809481:web:d18889503598aa006c77d8'
}

const app = initializeApp(firebaseConfig)

export const auth = getAuth(app)
export const db = getFirestore(app)

export default app