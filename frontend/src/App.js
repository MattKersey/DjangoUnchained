import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { BrowserRouter, Route, Switch } from 'react-router-dom'

import Home from './Home/Home'
import Login from './Login/Login'
import Error from './shared/Error'
import NavBar from './shared/Navigation'
import Register from './Login/Register'
import Shop from './Shop/Shop'

import Container from '@material-ui/core/Container'

class App extends Component {
  render () {
    return (
      <BrowserRouter>
        <NavBar />

        <Container fixed>
          <Switch>
            <Route path='/dummy' component={Home} exact />
            <Route path='/' component={Login} exact />
            <Route path='/register' component={Register} exact />
            <Route path='/shop/:shopID' component={Shop} exact />
            <Route component={Error} />
          </Switch>
        </Container>
      </BrowserRouter>
    )
  }
}

App.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired
  })
}

export default App
