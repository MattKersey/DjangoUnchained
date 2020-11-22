import { render, screen } from '@testing-library/react'
import React from 'react'
import Enzyme, { shallow, mount } from 'enzyme'
import Adapter from '@wojtekmaj/enzyme-adapter-react-17'
import App from './App'
import Login from './Login/Login'
import Register from './Login/Register'
import Product from './Shop/Product'
import Shop from './Shop/Shop'
Enzyme.configure({ adapter: new Adapter() })

test('Get Login Screen by default', () => {
  render(
    <App />
  )
  // verify page content for expected route
  // often you'd use a data-testid or role query, but this is also possible
  expect(screen.getByText(/Sign into your PyMarket Account/i)).toBeInTheDocument()
})

describe('Test Login Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = shallow(<Login />)
  })

  test('Page header should be correct', () => {
    render(<Login />)
    expect(screen.getByText(/Sign into your PyMarket Account/i)).toBeInTheDocument()
  })

  test('Empty fields', () => {
    wrapper.dive().find('form').simulate('submit')
    expect(wrapper.dive().state('username')).toEqual('')
  })

  test('Handle click', () => {
    wrapper.dive().find('form').childAt(3).simulate('click')
  })
})

describe('Test Register Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = shallow(<Register />)
  })

  test('Page header should be correct', () => {
    render(<Register />)
    expect(screen.getByText(/Create a new PyMarket Account/i)).toBeInTheDocument()
  })

  test('Empty fields', () => {
    const input1 = wrapper.dive().find('form').childAt(0)
    expect(input1.prop('id')).toEqual('first_name')
    expect(input1.prop('value')).toBeUndefined()
    input1.props('onChange', { target: { value: 'A' } })
    const input2 = wrapper.dive().find('form').childAt(1)
    input2.props('onChange', { target: { value: 'B' } })
    const input3 = wrapper.dive().find('form').childAt(2)
    input3.props('onChange', { target: { value: 'abc@gmail.com' } })
    const input4 = wrapper.dive().find('form').childAt(3)
    input4.props('onChange', { target: { name: 'password', value: 'password' } })
    expect(wrapper.update().dive().state('password')).toEqual('password')
    //wrapper.dive().find('form').simulate('submit')
    //expect(wrapper.update().dive().state('password')).toEqual('password')
  })
})

describe('Test Product Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = shallow(<Product />)
  })

  test('Check initial status', () => {
    expect(wrapper.dive().state('expanded')).toBe(false)
  })
})

describe('Test Shop Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = shallow(<Shop />)
  })

  test('Check initial status', () => {
    expect(wrapper.state('inCart')).toEqual({})
  })

  test('try', () => {
    wrapper = mount(<Shop />)
  })
})
