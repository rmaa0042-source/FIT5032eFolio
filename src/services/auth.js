import { computed, readonly, ref } from 'vue'
import {
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signOut,
  updateProfile
} from 'firebase/auth'
import { auth } from '../firebase'

const user = ref(auth.currentUser)

onAuthStateChanged(auth, (firebaseUser) => {
  user.value = firebaseUser

  console.log(
    'Current user:',
    firebaseUser
      ? {
          email: firebaseUser.email,
          role: firebaseUser.displayName
        }
      : null
  )
})

export const currentUser = readonly(user)

export const isAuthenticated = computed(() => Boolean(user.value))

export const register = async (email, password, role) => {
  const credential = await createUserWithEmailAndPassword(
    auth,
    email,
    password
  )

  await updateProfile(credential.user, {
    displayName: role
  })

  user.value = credential.user
  return credential.user
}

export const login = async (email, password) => {
  const credential = await signInWithEmailAndPassword(
    auth,
    email,
    password
  )

  user.value = credential.user
  return credential.user
}

export const logout = async () => {
  await signOut(auth)
  user.value = null
}