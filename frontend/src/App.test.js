/* global expect, test */

import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import React from 'react'
import App from './App'
import Shop from './Shop/Shop'
import Login from './Login/Login'
import { createMemoryHistory } from 'history'
import { BrowserRouter, Route, Switch, Redirect } from 'react-router-dom'


//Authorization
test('Get Login Screen by default', () => {
  render(
    <App />
  )
  // verify page content for expected route
  // often you'd use a data-testid or role query, but this is also possible
  expect(screen.getByText(/Sign into your PyMarket Account/i)).toBeInTheDocument()
})


test('Test Shop Page', async () => {

  render(
    <Shop match={{params: {shopID: 6}, isExact: true, path: "", url: ""}} />
  )
  // verify page content for expected route
  // often you'd use a data-testid or role query, but this is also possible
  expect(screen.getByText(/Add an Item/i)).toBeInTheDocument()
})

test('Test Add an Item Button', async () => {
  render(
    <BrowserRouter>
      <Shop match={{params: {shopID: 6}, isExact: true, path: "", url: ""}} />
    </BrowserRouter>

  )
  // verify page content for expected route
  // often you'd use a data-testid or role query, but this is also possible
  fireEvent.click(screen.getByText(/Add an Item/i))
  expect(screen.getByText(/Fill out the following form to create an item/i)).toBeInTheDocument()
})


test('Test Login Component', () => {
  render(<Login />)
  expect(screen.getByText(/Sign into your PyMarket Account/i)).toBeInTheDocument()
})
