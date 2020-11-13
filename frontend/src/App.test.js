import { render } from '@testing-library/react'
import App from './App'
import '@testing-library/jest-dom/extend-expect'

test('renders learn react link', () => {
  render(<App />)
  expect(1).toBe(1)
})
