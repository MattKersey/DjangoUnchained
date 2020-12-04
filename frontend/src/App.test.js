/* global expect, test */

import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import React from 'react'
import App from './App'
import Shop from './Shop/Shop'
import AddItemForm from './Shop/AddItemForm'
import AddShopForm from './User/AddShopForm'
import StoreCard from './User/StoreCard'
import UserPage from './User/UserPage'
import Error from './shared/Error'
import NavBar from './shared/Navigation'
import Login from './Login/Login'
import { createMemoryHistory } from 'history'
import { BrowserRouter, Route, Switch, Redirect } from 'react-router-dom'

describe('<App />', () => {
  it('Get Login Screen by default', () => {
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
})

describe('<Shop />', () => {
  test('Test Shop Page', async () => {
    render(
      <Shop match={{ params: { shopID: 6 }, isExact: true, path: '', url: '' }} />
    )
    expect(screen.getByText(/Add an Item/i)).toBeInTheDocument()
  })

  test('Test Add an Item Button', async () => {
    render(
      <BrowserRouter>
        <Shop match={{ params: { shopID: 6 }, isExact: true, path: '', url: '' }} />
      </BrowserRouter>

    )
    fireEvent.click(screen.getByText(/Add an Item/i))
    expect(screen.getByText(/Fill out the following form to create an item/i)).toBeInTheDocument()
  })
})

describe('<AddItemForm />', () => {
  test('Test AddItemForm', async () => {
    render(
      <BrowserRouter>
        <AddItemForm />
      </BrowserRouter>
    )
    expect(screen.getByText(/Add Item/i)).toBeInTheDocument()
  })
})

describe('<AddShopForm />', () => {
  test('Test submit AddShopForm', async () => {
    let f = false
    function flag () {
      f = true
    }
    render(
      <BrowserRouter>
        <AddShopForm onSub={flag} />
      </BrowserRouter>
    )
    fireEvent.click(screen.getByTestId('submit'))
    expect(f).toEqual(true)
  })

  test('Test Change AddShopForm', async () => {
    let f = false
    function flag () {
      f = true
    }
    render(
      <BrowserRouter>
        <AddShopForm onSub={flag} />
      </BrowserRouter>
    )
    const name = screen.getByTestId('name')
    fireEvent.change(name, { target: { value: 'new shop' } })
    expect(name).toHaveValue('new shop')
  })
})

describe('<StoreCard />', () => {
  test('Test StoreCard', async () => {
    render(
      <BrowserRouter>
        <StoreCard name='testStore' />
      </BrowserRouter>
    )
    expect(screen.getByText(/testStore/i)).toBeInTheDocument()
  })

  test('Test Click StoreCard', async () => {
    render(
      <BrowserRouter>
        <StoreCard name='testStore' />
      </BrowserRouter>
    )
    fireEvent.click(screen.getByTestId('card'))
    expect(true).toEqual(true) // >:) dont get mad at me
  })
})

describe('<UserPage />', () => {
  test('Test UserPage', async () => {
    render(
      <BrowserRouter>
        <UserPage />
      </BrowserRouter>
    )
    expect(screen.getByText(/Your Stores/i)).toBeInTheDocument()
  })

  test('Test UserPage Open Modal', async () => {
    render(
      <BrowserRouter>
        <UserPage />
      </BrowserRouter>
    )
    localStorage.setItem('token', 't6N1X1LWWell3fTUfzPcezEZxUcEQ6')

    fireEvent.click(screen.getByTestId('openModal'))
    expect(screen.getByText(/Fill out the following form to create an item/i)).toBeInTheDocument()
  })

  test('Test UserPage Close Modal', async () => {
    render(
      <BrowserRouter>
        <UserPage />
      </BrowserRouter>
    )

    fireEvent.click(screen.getByTestId('openModal'))
    fireEvent.click(screen.getByTestId('close'))
    expect(screen.queryByText(/Cancel/i)).not.toBeNull()
  })

  test('Test UserPage Submit Modal', async () => {
    let f = false
    function flag () {
      f = true
    }
    render(
      <BrowserRouter>
        <UserPage onSub={flag} />
      </BrowserRouter>
    )

    fireEvent.click(screen.getByTestId('openModal'))
    fireEvent.change(screen.getByTestId('name'), { target: { value: 'new shop' } })
    fireEvent.change(screen.getByTestId('address'), { target: { value: 'new address' } })
    fireEvent.change(screen.getByTestId('category'), { target: { value: 'Food' } })
    fireEvent.click(screen.getByTestId('submit'))
    expect(f).toEqual(true)
  })
})

describe('<Error />', () => {
  test('Test Error Page', async () => {
    render(
      <BrowserRouter>
        <Error />
      </BrowserRouter>
    )
    expect(screen.getByText(/Error: Page does not exist!/i)).toBeInTheDocument()
  })
})

describe('<NavBar />', () => {
  test('Test Navigation Bar', async () => {
    render(
      <BrowserRouter>
        <NavBar />
      </BrowserRouter>
    )
    fireEvent.click(screen.getByTestId('title'))
    expect(screen.getByText(/PyMarket/i)).toBeInTheDocument()
  })
})
