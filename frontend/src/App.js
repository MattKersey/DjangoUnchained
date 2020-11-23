/* global localStorage */
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { BrowserRouter, Route, Switch, Redirect } from 'react-router-dom'

import Home from './Home/Home'
import Login from './Login/Login'
import Error from './shared/Error'
import NavBar from './shared/Navigation'
import Register from './Login/Register'
import Shop from './Shop/Shop'

import Container from '@material-ui/core/Container'
import LoginButtons from './OauthLogin/LoginButtons'
import LoginRedirect from './OauthLogin/LoginRedirect'

class App extends Component {
  constructor (props) {
    super(props)
    this.state = {
      logged_in: !!localStorage.getItem('token'),
      email: ''
    }
  }

  render () {
    const PrivateRoute = ({ ...props }) => this.state.logged_in ? <Route {...props} /> : <Redirect to='/login' />
    return (
      <BrowserRouter>
        <NavBar />

        <Container fixed>
          <Switch>
            <PrivateRoute path='/dummy' component={Home} exact />
            <PrivateRoute path='/register' component={Register} exact />
            <PrivateRoute path='/shop/:shopID' component={Shop} exact />
            <Route path='/' component={LoginButtons} exact />
            <Route path='/loginredirect' component={LoginRedirect} exact />
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
