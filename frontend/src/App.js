/* global localStorage, fetch */
/* eslint react/prop-types: 0 */

import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { BrowserRouter, Route, Switch, Redirect } from 'react-router-dom'

import UserPage from './User/UserPage'
/* istanbul ignore file */

import Error from './shared/Error'
import NavBar from './shared/Navigation'
import Register from './Login/Register'
import Shop from './Shop/Shop'
import Success from './Shop/Success'
import History from './Shop/History'
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

  componentDidMount () {
    if (this.state.logged_in) {
      fetch('http://127.0.0.1:8000/api/users/current_user/', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      })
        .then(res => res.json())
        .then(json => {
          localStorage.setItem('user_id', json.pk)
          localStorage.setItem('email', json.email)
        })
    }
  }

  logOut (event) {
    localStorage.removeItem('token')
    localStorage.removeItem('email')
    localStorage.removeItem('user_id')
    this.setState({ logged_in: false, email: '' })
  }

  render () {
    const PrivateRoute = ({ ...props }) => this.state.logged_in ? <Route {...props} /> : <Redirect to='/login' />
    return (
      <BrowserRouter>
        <NavBar isLogged={this.state.logged_in} handleLogOut={(event) => this.logOut(event)} />

        <Container fixed>
          <Switch>
            <PrivateRoute path='/' component={UserPage} exact />
            <Route path='/register' component={Register} exact />
            <PrivateRoute path='/shop/:shopID' component={Shop} exact />
            <PrivateRoute path='/shop/:shopID/success' component={Success} exact />
            <PrivateRoute path='/shop/:shopID/history' component={History} exact />
            <Route path='/login' component={LoginButtons} exact />
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
