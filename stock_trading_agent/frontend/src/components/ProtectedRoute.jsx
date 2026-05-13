import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import AuthLoading from './AuthLoading'

const ProtectedRoute = ({ children }) => {
  const { user, authLoading } = useAuth()

  if (authLoading) {
    return <AuthLoading message="Loading your workspace..." />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute
