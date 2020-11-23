/* global expect, test */

import { render, screen } from '@testing-library/react'
import React from 'react'
import App from './App'
import Login from './Login/Login'

test('Get Login Screen by default', () => {
  render(
    <App />
  )
  // verify page content for expected route
  // often you'd use a data-testid or role query, but this is also possible
  expect(screen.getByText(/Sign into your PyMarket Account/i)).toBeInTheDocument()
})

test('Test Login Component', () => {
  render(<Login />)
  expect(screen.getByText(/Sign into your PyMarket Account/i)).toBeInTheDocument()
})
