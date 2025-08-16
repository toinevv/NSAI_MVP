/**
 * Supabase Client Configuration
 * Provides centralized Supabase client for authentication and database access
 */

import { createClient } from '@supabase/supabase-js'

// Get Supabase configuration from environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables. Please check your .env file.')
}

// Create Supabase client with auth persistence
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
    storage: window.localStorage,
  },
})

// Auth helper functions
export const auth = {
  /**
   * Get current user session
   */
  async getSession() {
    const { data: { session }, error } = await supabase.auth.getSession()
    if (error) {
      console.error('Error getting session:', error)
      return null
    }
    return session
  },

  /**
   * Get current access token for API calls
   */
  async getAccessToken() {
    const session = await this.getSession()
    return session?.access_token || null
  },

  /**
   * Sign in with email and password
   */
  async signIn(email: string, password: string) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
    return data
  },

  /**
   * Sign up with email and password
   */
  async signUp(email: string, password: string, metadata?: { 
    first_name?: string
    last_name?: string 
    organization_name?: string
  }) {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: metadata,
      },
    })
    if (error) throw error
    return data
  },

  /**
   * Sign out current user
   */
  async signOut() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  },

  /**
   * Subscribe to auth state changes
   */
  onAuthStateChange(callback: (event: string, session: any) => void) {
    return supabase.auth.onAuthStateChange(callback)
  },

  /**
   * Check if user is authenticated
   */
  async isAuthenticated() {
    const session = await this.getSession()
    return !!session
  },
}

// Export types for TypeScript support
export type { AuthSession as Session, AuthUser as User } from '@supabase/supabase-js'