import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { BrowserRouter, Route, Switch } from 'react-router-dom'

import Home from './Home/Home'
import Login from './Login/Login'
import Error from './shared/Error'
import NavBar from './shared/Navigation'

class App extends Component {
  componentDidMount () {
    const isAuthenticated = false
    if (isAuthenticated) {
      this.props.history.push('/login')
    }
  }

  render () {
    return (
      <BrowserRouter>
        <div>
          <NavBar />
          <Switch>
            <Route path='/dummy' component={Home} exact />
            <Route path='/' component={Login} exact />
            <Route component={Error} />
          </Switch>
        </div>
      </BrowserRouter>
    )
  }
}

App.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired
  }).isRequired
}

export default App
