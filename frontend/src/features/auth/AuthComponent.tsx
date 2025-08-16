/**
 * MVP Authentication Component
 * Simple auth UI for testing - production version would be more sophisticated
 */

import React, { useState } from 'react'
import { useAuth } from './AuthContext'
import { User, LogOut, Loader2 } from 'lucide-react'

export const AuthComponent: React.FC = () => {
  const { user, signIn, signUp, signOut, loading, error, isAuthenticated } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSignUp, setIsSignUp] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setAuthError(null)
    
    try {
      if (isSignUp) {
        await signUp(email, password, {
          organization_name: 'Default Organization',
        })
      } else {
        await signIn(email, password)
      }
      // Clear form on success
      setEmail('')
      setPassword('')
    } catch (err: any) {
      setAuthError(err.message || 'Authentication failed')
    }
  }

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (err: any) {
      setAuthError(err.message || 'Sign out failed')
    }
  }

  // If authenticated, show user info and sign out button
  if (isAuthenticated && user) {
    return (
      <div className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <User className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        <span className="text-sm text-gray-700 dark:text-gray-300">
          {user.email}
        </span>
        <button
          onClick={handleSignOut}
          className="ml-auto flex items-center gap-2 px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          disabled={loading}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <LogOut className="w-4 h-4" />
          )}
          Sign Out
        </button>
      </div>
    )
  }

  // Show auth form
  return (
    <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
      <h3 className="text-sm font-semibold mb-3 text-yellow-800 dark:text-yellow-200">
        🔐 Authentication Required
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 text-sm border rounded dark:bg-gray-800 dark:border-gray-700"
            required
            disabled={loading}
          />
        </div>
        
        <div>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 text-sm border rounded dark:bg-gray-800 dark:border-gray-700"
            required
            disabled={loading}
            minLength={6}
          />
        </div>
        
        {(error || authError) && (
          <div className="text-sm text-red-600 dark:text-red-400">
            {error || authError}
          </div>
        )}
        
        <div className="flex gap-2">
          <button
            type="submit"
            className="flex-1 px-3 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors disabled:opacity-50"
            disabled={loading}
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin mx-auto" />
            ) : (
              isSignUp ? 'Sign Up' : 'Sign In'
            )}
          </button>
          
          <button
            type="button"
            onClick={() => setIsSignUp(!isSignUp)}
            className="px-3 py-2 text-sm text-blue-600 dark:text-blue-400 hover:underline"
            disabled={loading}
          >
            {isSignUp ? 'Have an account?' : 'Need an account?'}
          </button>
        </div>
      </form>
      
      <div className="mt-3 text-xs text-gray-600 dark:text-gray-400">
        <p>For MVP testing, use:</p>
        <p className="font-mono">test@newsystem.ai / test123456</p>
        <p className="mt-1">Or create a new account to test multi-tenant isolation</p>
      </div>
    </div>
  )
}