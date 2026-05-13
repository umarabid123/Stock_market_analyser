import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import AuthLoading from './AuthLoading'

const AuthRoute = ({ children }) => {
  const { user, authLoading } = useAuth()

  if (authLoading) {
    return <AuthLoading message="Preparing sign-in..." />
  }

  if (user) {
    return <Navigate to="/trading" replace />
  }

  return children
}

export default AuthRoute
