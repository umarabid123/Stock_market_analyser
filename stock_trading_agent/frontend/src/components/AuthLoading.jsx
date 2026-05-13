import React from 'react'

const AuthLoading = ({ message = 'Checking session...' }) => (
  <div className="auth-shell">
    <div className="auth-card auth-loading">
      <div className="auth-spinner" />
      <p className="auth-loading-text">{message}</p>
    </div>
  </div>
)

export default AuthLoading
