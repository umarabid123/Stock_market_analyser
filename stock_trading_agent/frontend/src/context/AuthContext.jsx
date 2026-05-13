import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import {
  GoogleAuthProvider,
  browserLocalPersistence,
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  setPersistence,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
} from 'firebase/auth'
import { auth } from '../lib/firebase'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)

  useEffect(() => {
    let isMounted = true

    setPersistence(auth, browserLocalPersistence).catch((error) => {
      console.error('Failed to set auth persistence:', error)
    })

    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      if (!isMounted) return
      setUser(firebaseUser)
      setAuthLoading(false)
    })

    return () => {
      isMounted = false
      unsubscribe()
    }
  }, [])

  const login = useCallback(
    (email, password) => signInWithEmailAndPassword(auth, email, password),
    []
  )

  const signup = useCallback(
    (email, password) => createUserWithEmailAndPassword(auth, email, password),
    []
  )

  const googleSignIn = useCallback(() => {
    const provider = new GoogleAuthProvider()
    return signInWithPopup(auth, provider)
  }, [])

  const logout = useCallback(() => signOut(auth), [])

  const value = useMemo(
    () => ({
      user,
      authLoading,
      login,
      signup,
      googleSignIn,
      logout,
    }),
    [user, authLoading, login, signup, googleSignIn, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
