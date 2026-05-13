const AUTH_ERROR_MESSAGES = {
  'auth/invalid-credential': 'Invalid email or password.',
  'auth/user-not-found': 'No account found for this email.',
  'auth/wrong-password': 'Invalid email or password.',
  'auth/too-many-requests': 'Too many attempts. Try again later.',
  'auth/email-already-in-use': 'An account already exists with this email.',
  'auth/weak-password': 'Password must be at least 6 characters.',
  'auth/popup-closed-by-user': 'The Google sign-in window was closed.',
  'auth/cancelled-popup-request': 'The Google sign-in was cancelled.',
}

export const getAuthErrorMessage = (error) => {
  const code = error?.code || ''
  return AUTH_ERROR_MESSAGES[code] || 'Authentication failed. Please try again.'
}
